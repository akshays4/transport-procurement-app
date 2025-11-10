import logging
import os
import re
import streamlit as st
from model_serving_utils import (
    endpoint_supports_feedback, 
    query_endpoint, 
    query_endpoint_stream, 
    _get_endpoint_task_type,
)
from collections import OrderedDict
from messages import UserMessage, AssistantResponse, render_message
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVING_ENDPOINT = os.getenv('SERVING_ENDPOINT')
assert SERVING_ENDPOINT, \
    ("Unable to determine serving endpoint to use for chatbot app. If developing locally, "
     "set the SERVING_ENDPOINT environment variable to the name of your serving endpoint. If "
     "deploying to a Databricks app, include a serving endpoint resource named "
     "'serving_endpoint' with CAN_QUERY permissions, as described in "
     "https://docs.databricks.com/aws/en/generative-ai/agent-framework/chat-app#deploy-the-databricks-app")

ENDPOINT_SUPPORTS_FEEDBACK = endpoint_supports_feedback(SERVING_ENDPOINT)

def clean_text_content(text):
    """
    Clean text by removing XML-like tags and extra whitespace.
    """
    if not text:
        return ""
    
    # Remove XML-like tags (e.g., <think>, <reasoning>, etc.)
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove multiple consecutive whitespaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_structured_json(content):
    """
    Extract structured JSON data from agent response if present.
    Looks for ---STRUCTURED_DATA--- markers and parses JSON content.
    Returns None if no structured data found.
    """
    if not content:
        return None
    
    # Look for structured data markers
    pattern = r'---STRUCTURED_DATA---\s*(\{.*?\})\s*---END_STRUCTURED_DATA---'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return None
    
    try:
        json_str = match.group(1)
        # Clean up any potential formatting issues
        json_str = re.sub(r'[\r\n\t]', ' ', json_str)  # Replace newlines/tabs with spaces
        json_str = re.sub(r'\s+', ' ', json_str)  # Normalize whitespace
        
        data = json.loads(json_str)
        return data
    except (json.JSONDecodeError, AttributeError) as e:
        logger.warning(f"Failed to parse structured JSON data: {e}")
        return None


def extract_compliance_data(history):
    """
    Extract suppliers at risk and compliance actions from chat history in a structured manner.
    Supports both structured JSON format and unstructured text extraction.
    Returns a dict with 'suppliers_at_risk', 'compliance_actions', and 'summary' fields.
    """
    suppliers_at_risk = {}  # Use dict for structured storage
    compliance_actions = []
    all_content = []
    
    # Collect and clean all content
    for element in history:
        if isinstance(element, AssistantResponse):
            for msg in element.messages:
                # Skip tool responses - they contain internal processing
                if msg.get("role") == "tool":
                    continue
                
                # Skip messages with tool calls (they're usually empty or contain only function calls)
                if msg.get("tool_calls"):
                    continue
                
                content = msg.get("content", "")
                if content:
                    # First, try to extract structured data if present
                    structured_data = extract_structured_json(content)
                    if structured_data:
                        # Process structured suppliers
                        for supplier in structured_data.get("suppliers_at_risk", []):
                            supplier_name = supplier.get("supplier_name", "").strip()
                            
                            # Validate supplier name from structured data
                            invalid_terms = ['compliance', 'policy', 'procurement', 'government', 'supplier', 'vendor']
                            if not supplier_name or supplier_name.lower() in invalid_terms:
                                continue
                            
                            if len(supplier_name) < 3 or len(supplier_name) > 100:
                                continue
                            
                            if supplier_name and supplier_name not in suppliers_at_risk:
                                suppliers_at_risk[supplier_name] = {
                                    "supplier_name": supplier_name,
                                    "risk_type": supplier.get("risk_type", "General Risk"),
                                    "severity": supplier.get("severity", "Medium"),
                                    "details": [],
                                }
                            if supplier_name:
                                detail_text = f"{supplier.get('summary', '')} Evidence: {supplier.get('evidence', '')}"
                                suppliers_at_risk[supplier_name]["details"].append(detail_text.strip())
                        
                        # Process structured actions
                        for action in structured_data.get("compliance_actions", []):
                            action_text = action.get("action", "")
                            if action_text:
                                compliance_actions.append({
                                    "action": action_text,
                                    "category": action.get("category", "General Action"),
                                    "priority": action.get("priority", "Medium"),
                                    "rationale": action.get("rationale", "")
                                })
                    
                    # Clean the content and add to all_content for unstructured extraction
                    content = clean_text_content(content)
                    all_content.append(content)
    
    full_text = "\n\n".join(all_content)
    
    # ========================================================================
    # STRUCTURED SUPPLIER EXTRACTION
    # ========================================================================
    
    # Pattern 1: Explicit supplier risk mentions
    supplier_patterns = [
        # "Supplier X has risk/issue"
        r"(?i)(?:supplier|vendor|contractor|company|organization)\s+(?:named\s+)?['\"]?([A-Z][A-Za-z0-9\s&\-\.,']+?)['\"]?\s+(?:has|shows|demonstrates|presents|poses|exhibits|faces)\s+(?:a\s+)?(?:significant\s+)?(?:risk|concern|issue|problem|compliance\s+issue|violation)",
        
        # "Risk with Supplier X"
        r"(?i)(?:risk|concern|issue|problem|violation|breach|non-compliance).*?(?:with|regarding|concerning|about|from)\s+(?:supplier|vendor|contractor|company)\s+['\"]?([A-Z][A-Za-z0-9\s&\-\.,']+?)['\"]?(?:\.|,|;|\s+(?:is|has|which|that))",
        
        # Supplier X identified as high risk
        r"(?i)['\"]?([A-Z][A-Za-z0-9\s&\-\.,']+?)['\"]?\s+(?:is\s+)?(?:identified|classified|categorized|flagged|marked)\s+as\s+(?:a\s+)?(?:high|significant|major)?\s*risk",
    ]
    
    for pattern in supplier_patterns:
        matches = re.finditer(pattern, full_text)
        for match in matches:
            supplier_name = match.group(1).strip()
            
            # Clean up supplier name (remove trailing punctuation, limit length)
            supplier_name = re.sub(r'[,\.;]+$', '', supplier_name).strip()
            
            # Skip if too short or too long
            if len(supplier_name) < 3 or len(supplier_name) > 100:
                continue
            
            # Filter out invalid/generic terms that aren't company names
            invalid_terms = [
                'compliance', 'policy', 'procurement', 'government', 'agency',
                'contract', 'supplier', 'vendor', 'contractor', 'company',
                'risk', 'issue', 'concern', 'violation', 'breach', 'procedure',
                'requirement', 'standard', 'regulation', 'framework', 'process',
                'management', 'monitoring', 'assessment', 'audit', 'review',
                'knowledge', 'assistant', 'question', 'search', 'finding'
            ]
            
            # Check if the supplier name is just a generic term
            if supplier_name.lower() in invalid_terms:
                continue
            
            # Skip if it doesn't look like a company name (should have at least one capital letter)
            if not any(c.isupper() for c in supplier_name):
                continue
            
            # Skip if it starts with common non-company words
            skip_prefixes = ['the question', 'the search', 'knowledge', 'assistant', 'policy', 'procedure']
            if any(supplier_name.lower().startswith(prefix) for prefix in skip_prefixes):
                continue
            
            # Extract context (sentence containing the match)
            start = max(0, match.start() - 200)
            end = min(len(full_text), match.end() + 300)
            context = full_text[start:end].strip()
            
            # Skip if context contains markers of tool responses or internal reasoning
            skip_markers = [
                'knowledge-assistant', 'searching', 'verifying', 'possible_sources',
                'tool_calls', 'function_call', 'The search results', 'I will structure',
                'To answer comprehensively', 'The question asks'
            ]
            if any(marker.lower() in context.lower() for marker in skip_markers):
                continue
            
            # Skip if context is too long (likely contains tool output)
            if len(context) > 1000:
                continue
            
            # Extract risk type
            risk_type = "General Risk"
            if re.search(r'(?i)financial|bankruptcy|debt', context):
                risk_type = "Financial Risk"
            elif re.search(r'(?i)compliance|regulatory|violation|breach', context):
                risk_type = "Compliance Risk"
            elif re.search(r'(?i)reputation|negative\s+news|scandal', context):
                risk_type = "Reputational Risk"
            elif re.search(r'(?i)operational|delivery|performance', context):
                risk_type = "Operational Risk"
            
            # Extract severity
            severity = "Medium"
            if re.search(r'(?i)high|critical|severe|significant|major', context):
                severity = "High"
            elif re.search(r'(?i)low|minor|minimal', context):
                severity = "Low"
            
            # Store in structured format
            if supplier_name not in suppliers_at_risk:
                suppliers_at_risk[supplier_name] = {
                    "supplier_name": supplier_name,
                    "risk_type": risk_type,
                    "severity": severity,
                    "details": [],
                }
            
            suppliers_at_risk[supplier_name]["details"].append(context)
    
    # ========================================================================
    # STRUCTURED COMPLIANCE ACTIONS EXTRACTION
    # ========================================================================
    
    # Look for sections with recommendations or actions
    action_sections = []
    
    # Pattern for sections with actions/recommendations
    section_patterns = [
        r'(?i)(?:recommended?\s+actions?|next\s+steps?|compliance\s+measures?|due\s+diligence\s+steps?):?\s*\n((?:[-•*\d]+\.?\s+.+\n?)+)',
        r'(?i)(?:should|must|need\s+to|required\s+to|recommend).*?:\s*\n((?:[-•*\d]+\.?\s+.+\n?)+)',
    ]
    
    for pattern in section_patterns:
        matches = re.finditer(pattern, full_text)
        for match in matches:
            action_sections.append(match.group(1))
    
    # Extract individual actions from bullet points
    for section in action_sections:
        # Match bullet points or numbered lists
        action_items = re.finditer(r'(?:^|\n)\s*(?:[-•*]|\d+\.)\s+(.+?)(?=\n\s*(?:[-•*]|\d+\.)|$)', section, re.MULTILINE)
        
        for item in action_items:
            action_text = clean_text_content(item.group(1))
            
            if len(action_text) < 15:  # Skip very short items
                continue
            
            # Categorize action
            category = "General Action"
            if re.search(r'(?i)audit|review|inspect|examine|assess', action_text):
                category = "Audit/Review"
            elif re.search(r'(?i)verify|confirm|check|validate', action_text):
                category = "Verification"
            elif re.search(r'(?i)document|record|report', action_text):
                category = "Documentation"
            elif re.search(r'(?i)monitor|track|observe', action_text):
                category = "Monitoring"
            elif re.search(r'(?i)contact|communicate|notify|inform', action_text):
                category = "Communication"
            
            # Determine priority from keywords
            priority = "Medium"
            if re.search(r'(?i)immediate|urgent|critical|must|required', action_text):
                priority = "High"
            elif re.search(r'(?i)consider|may|could|optional', action_text):
                priority = "Low"
            
            compliance_actions.append({
                "action": action_text,
                "category": category,
                "priority": priority,
            })
    
    # Also look for standalone recommendations in sentences
    standalone_patterns = [
        r'(?i)(?:it\s+is\s+)?(?:recommended|suggested|advised)\s+(?:that|to)\s+(.+?)(?:\.|;|$)',
        r'(?i)(?:you\s+)?(?:should|must|need\s+to)\s+(.+?)(?:\.|;|$)',
    ]
    
    for pattern in standalone_patterns:
        matches = re.finditer(pattern, full_text)
        for match in matches:
            action_text = clean_text_content(match.group(1))
            
            if len(action_text) < 15 or len(action_text) > 300:
                continue
            
            # Skip if it contains markers of tool responses or internal reasoning
            skip_markers = [
                'knowledge-assistant', 'searching', 'verifying', 'tool_call',
                'function_call', 'search results', 'I will structure', 'possible_sources'
            ]
            if any(marker.lower() in action_text.lower() for marker in skip_markers):
                continue
            
            # Check if similar action already exists
            if any(action_text.lower() in action["action"].lower() or action["action"].lower() in action_text.lower() 
                   for action in compliance_actions):
                continue
            
            compliance_actions.append({
                "action": action_text,
                "category": "General Action",
                "priority": "Medium",
            })
    
    # ========================================================================
    # REMOVE DUPLICATES AND FORMAT OUTPUT
    # ========================================================================
    
    # Convert suppliers dict to list and deduplicate details
    suppliers_list = []
    for supplier_name, supplier_data in suppliers_at_risk.items():
        # Deduplicate details
        unique_details = []
        seen_details = set()
        for detail in supplier_data["details"]:
            detail_key = detail[:100].lower()
            if detail_key not in seen_details:
                seen_details.add(detail_key)
                unique_details.append(detail)
        
        supplier_data["details"] = unique_details[:3]  # Limit to 3 details per supplier
        suppliers_list.append(supplier_data)
    
    # Deduplicate actions
    unique_actions = []
    seen_actions = set()
    for action in compliance_actions:
        action_key = action["action"][:80].lower()
        if action_key not in seen_actions:
            seen_actions.add(action_key)
            unique_actions.append(action)
    
    return {
        "suppliers_at_risk": suppliers_list[:15],  # Limit to 15 suppliers
        "compliance_actions": unique_actions[:25],  # Limit to 25 actions
        "total_messages": len(history),
    }

def render_action_item(action_info, unique_key):
    """Helper function to render a single action item."""
    with st.container():
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{action_info['category']}**")
            st.write(action_info["action"])
            
            # Show rationale if available (from structured data)
            if action_info.get("rationale"):
                st.caption(f"💡 Rationale: {action_info['rationale']}")
        with col2:
            st.checkbox("✓ Done", key=f"action_completed_{unique_key}")
        
        st.text_area(
            "Notes",
            key=f"action_notes_{unique_key}",
            placeholder="Add notes about this action...",
            height=80,
            label_visibility="collapsed"
        )
        st.markdown("---")


def format_text_report(data, timestamp):
    """Format the compliance data as a text report."""
    lines = []
    lines.append("=" * 80)
    lines.append("NSW PROCUREMENT COMPLIANCE REPORT")
    lines.append("=" * 80)
    lines.append(f"Generated: {timestamp}")
    lines.append(f"Total Messages Analyzed: {data['report_metadata']['total_messages_analyzed']}")
    lines.append("")
    
    lines.append("=" * 80)
    lines.append("SUPPLIERS AT RISK")
    lines.append("=" * 80)
    lines.append(f"Total: {data['report_metadata']['suppliers_at_risk_count']}")
    lines.append("")
    
    for supplier in data["suppliers_at_risk"]:
        lines.append("-" * 80)
        lines.append(f"Supplier: {supplier['supplier_name']}")
        lines.append(f"Risk Type: {supplier['risk_type']}")
        lines.append(f"Severity: {supplier['severity']}")
        lines.append("")
        lines.append("Details:")
        for idx, detail in enumerate(supplier["details"], 1):
            lines.append(f"  {idx}. {detail}")
        lines.append("")
    
    lines.append("")
    lines.append("=" * 80)
    lines.append("COMPLIANCE DUE DILIGENCE ACTIONS")
    lines.append("=" * 80)
    lines.append(f"Total: {data['report_metadata']['compliance_actions_count']}")
    lines.append("")
    
    for idx, action in enumerate(data["compliance_actions"], 1):
        lines.append(f"{idx}. [{action['priority']}] {action['category']}")
        lines.append(f"   {action['action']}")
        if action.get('rationale'):
            lines.append(f"   Rationale: {action['rationale']}")
        lines.append("")
    
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    return "\n".join(lines)


def reduce_chat_agent_chunks(chunks):
    """
    Reduce a list of ChatAgentChunk objects corresponding to a particular
    message into a single ChatAgentMessage
    """
    deltas = [chunk.delta for chunk in chunks]
    first_delta = deltas[0]
    result_msg = first_delta
    msg_contents = []
    
    # Accumulate tool calls properly
    tool_call_map = {}  # Map call_id to tool call for accumulation
    
    for delta in deltas:
        # Handle content
        if delta.content:
            msg_contents.append(delta.content)
            
        # Handle tool calls
        if hasattr(delta, 'tool_calls') and delta.tool_calls:
            for tool_call in delta.tool_calls:
                call_id = getattr(tool_call, 'id', None)
                tool_type = getattr(tool_call, 'type', "function")
                function_info = getattr(tool_call, 'function', None)
                if function_info:
                    func_name = getattr(function_info, 'name', "")
                    func_args = getattr(function_info, 'arguments', "")
                else:
                    func_name = ""
                    func_args = ""
                
                if call_id:
                    if call_id not in tool_call_map:
                        # New tool call
                        tool_call_map[call_id] = {
                            "id": call_id,
                            "type": tool_type,
                            "function": {
                                "name": func_name,
                                "arguments": func_args
                            }
                        }
                    else:
                        # Accumulate arguments for existing tool call
                        existing_args = tool_call_map[call_id]["function"]["arguments"]
                        tool_call_map[call_id]["function"]["arguments"] = existing_args + func_args

                        # Update function name if provided
                        if func_name:
                            tool_call_map[call_id]["function"]["name"] = func_name

        # Handle tool call IDs (for tool response messages)
        if hasattr(delta, 'tool_call_id') and delta.tool_call_id:
            result_msg = result_msg.model_copy(update={"tool_call_id": delta.tool_call_id})
    
    # Convert tool call map back to list
    if tool_call_map:
        accumulated_tool_calls = list(tool_call_map.values())
        result_msg = result_msg.model_copy(update={"tool_calls": accumulated_tool_calls})
    
    result_msg = result_msg.model_copy(update={"content": "".join(msg_contents)})
    return result_msg


def query_endpoint_and_render(task_type, input_messages):
    """Handle streaming response based on task type."""
    if task_type == "agent/v1/responses":
        return query_responses_endpoint_and_render(input_messages)
    elif task_type == "agent/v2/chat":
        return query_chat_agent_endpoint_and_render(input_messages)
    else:  # chat/completions
        return query_chat_completions_endpoint_and_render(input_messages)


def query_chat_completions_endpoint_and_render(input_messages):
    """Handle ChatCompletions streaming format."""
    with st.chat_message("assistant"):
        response_area = st.empty()
        response_area.markdown("_Thinking..._")
        
        accumulated_content = ""
        request_id = None
        
        try:
            for chunk in query_endpoint_stream(
                endpoint_name=SERVING_ENDPOINT,
                messages=input_messages,
                return_traces=ENDPOINT_SUPPORTS_FEEDBACK
            ):
                if "choices" in chunk and chunk["choices"]:
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        accumulated_content += content
                        response_area.markdown(accumulated_content)
                
                if "databricks_output" in chunk:
                    req_id = chunk["databricks_output"].get("databricks_request_id")
                    if req_id:
                        request_id = req_id
            
            return AssistantResponse(
                messages=[{"role": "assistant", "content": accumulated_content}],
                request_id=request_id
            )
        except Exception as e:
            logger.error(
                f"Error in query_chat_completions_endpoint_and_render (streaming):\n"
                f"Endpoint: {SERVING_ENDPOINT}\n"
                f"Error: {str(e)}\n"
                f"Accumulated content so far: {accumulated_content[:500]}...\n"
                f"Input messages count: {len(input_messages)}"
            )
            response_area.markdown("_Ran into an error. Retrying without streaming..._")
            try:
                messages, request_id = query_endpoint(
                    endpoint_name=SERVING_ENDPOINT,
                    messages=input_messages,
                    return_traces=ENDPOINT_SUPPORTS_FEEDBACK
                )
                response_area.empty()
                with response_area.container():
                    for message in messages:
                        render_message(message)
                return AssistantResponse(messages=messages, request_id=request_id)
            except Exception as retry_error:
                logger.error(
                    f"Error in query_chat_completions_endpoint_and_render (non-streaming retry):\n"
                    f"Endpoint: {SERVING_ENDPOINT}\n"
                    f"Error: {str(retry_error)}\n"
                    f"Input messages: {json.dumps(input_messages, indent=2)}"
                )
                raise


def query_chat_agent_endpoint_and_render(input_messages):
    """Handle ChatAgent streaming format."""
    from mlflow.types.agent import ChatAgentChunk
    
    with st.chat_message("assistant"):
        response_area = st.empty()
        response_area.markdown("_Thinking..._")
        
        message_buffers = OrderedDict()
        request_id = None
        
        try:
            for raw_chunk in query_endpoint_stream(
                endpoint_name=SERVING_ENDPOINT,
                messages=input_messages,
                return_traces=ENDPOINT_SUPPORTS_FEEDBACK
            ):
                response_area.empty()
                chunk = ChatAgentChunk.model_validate(raw_chunk)
                delta = chunk.delta
                message_id = delta.id

                req_id = raw_chunk.get("databricks_output", {}).get("databricks_request_id")
                if req_id:
                    request_id = req_id
                if message_id not in message_buffers:
                    message_buffers[message_id] = {
                        "chunks": [],
                        "render_area": st.empty(),
                    }
                message_buffers[message_id]["chunks"].append(chunk)
                
                partial_message = reduce_chat_agent_chunks(message_buffers[message_id]["chunks"])
                render_area = message_buffers[message_id]["render_area"]
                message_content = partial_message.model_dump_compat(exclude_none=True)
                with render_area.container():
                    render_message(message_content)
            
            messages = []
            for msg_id, msg_info in message_buffers.items():
                messages.append(reduce_chat_agent_chunks(msg_info["chunks"]))
            
            return AssistantResponse(
                messages=[message.model_dump_compat(exclude_none=True) for message in messages],
                request_id=request_id
            )
        except Exception as e:
            logger.error(
                f"Error in query_chat_agent_endpoint_and_render (streaming):\n"
                f"Endpoint: {SERVING_ENDPOINT}\n"
                f"Error: {str(e)}\n"
                f"Accumulated messages count: {len(message_buffers)}\n"
                f"Input messages count: {len(input_messages)}"
            )
            response_area.markdown("_Ran into an error. Retrying without streaming..._")
            try:
                messages, request_id = query_endpoint(
                    endpoint_name=SERVING_ENDPOINT,
                    messages=input_messages,
                    return_traces=ENDPOINT_SUPPORTS_FEEDBACK
                )
                response_area.empty()
                with response_area.container():
                    for message in messages:
                        render_message(message)
                return AssistantResponse(messages=messages, request_id=request_id)
            except Exception as retry_error:
                logger.error(
                    f"Error in query_chat_agent_endpoint_and_render (non-streaming retry):\n"
                    f"Endpoint: {SERVING_ENDPOINT}\n"
                    f"Error: {str(retry_error)}\n"
                    f"Input messages: {json.dumps(input_messages, indent=2)}"
                )
                raise


def query_responses_endpoint_and_render(input_messages):
    """Handle ResponsesAgent streaming format using MLflow types."""
    from mlflow.types.responses import ResponsesAgentStreamEvent
    
    with st.chat_message("assistant"):
        response_area = st.empty()
        response_area.markdown("_Thinking..._")
        
        # Track all the messages that need to be rendered in order
        all_messages = []
        request_id = None

        try:
            for raw_event in query_endpoint_stream(
                endpoint_name=SERVING_ENDPOINT,
                messages=input_messages,
                return_traces=ENDPOINT_SUPPORTS_FEEDBACK
            ):
                # Extract databricks_output for request_id
                if "databricks_output" in raw_event:
                    req_id = raw_event["databricks_output"].get("databricks_request_id")
                    if req_id:
                        request_id = req_id
                
                # Parse using MLflow streaming event types, similar to ChatAgentChunk
                if "type" in raw_event:
                    event = ResponsesAgentStreamEvent.model_validate(raw_event)
                    
                    if hasattr(event, 'item') and event.item:
                        item = event.item  # This is a dict, not a parsed object
                        
                        if item.get("type") == "message":
                            # Extract text content from message if present
                            content_parts = item.get("content", [])
                            for content_part in content_parts:
                                if content_part.get("type") == "output_text":
                                    text = content_part.get("text", "")
                                    if text:
                                        all_messages.append({
                                            "role": "assistant",
                                            "content": text
                                        })
                            
                        elif item.get("type") == "function_call":
                            # Tool call
                            call_id = item.get("call_id")
                            function_name = item.get("name")
                            arguments = item.get("arguments", "")
                            
                            # Add to messages for history
                            all_messages.append({
                                "role": "assistant",
                                "content": "",
                                "tool_calls": [{
                                    "id": call_id,
                                    "type": "function",
                                    "function": {
                                        "name": function_name,
                                        "arguments": arguments
                                    }
                                }]
                            })
                            
                        elif item.get("type") == "function_call_output":
                            # Tool call output/result
                            call_id = item.get("call_id")
                            output = item.get("output", "")
                            
                            # Add to messages for history
                            all_messages.append({
                                "role": "tool",
                                "content": output,
                                "tool_call_id": call_id
                            })
                
                # Update the display by rendering all accumulated messages
                if all_messages:
                    with response_area.container():
                        for msg in all_messages:
                            render_message(msg)

            return AssistantResponse(messages=all_messages, request_id=request_id)
        except Exception as e:
            logger.error(
                f"Error in query_responses_endpoint_and_render (streaming):\n"
                f"Endpoint: {SERVING_ENDPOINT}\n"
                f"Error: {str(e)}\n"
                f"Accumulated messages count: {len(all_messages)}\n"
                f"Input messages count: {len(input_messages)}"
            )
            response_area.markdown("_Ran into an error. Retrying without streaming..._")
            try:
                messages, request_id = query_endpoint(
                    endpoint_name=SERVING_ENDPOINT,
                    messages=input_messages,
                    return_traces=ENDPOINT_SUPPORTS_FEEDBACK
                )
                response_area.empty()
                with response_area.container():
                    for message in messages:
                        render_message(message)
                return AssistantResponse(messages=messages, request_id=request_id)
            except Exception as retry_error:
                logger.error(
                    f"Error in query_responses_endpoint_and_render (non-streaming retry):\n"
                    f"Endpoint: {SERVING_ENDPOINT}\n"
                    f"Error: {str(retry_error)}\n"
                    f"Input messages: {json.dumps(input_messages, indent=2)}"
                )
                raise


# --- Init state ---
if "history" not in st.session_state:
    st.session_state.history = []

# Initialize page state
if "current_page" not in st.session_state:
    st.session_state.current_page = "chat"

# Navigation in sidebar
with st.sidebar:
    st.header("🧭 Navigation")
    if st.button("💬 Chat", use_container_width=True):
        st.session_state.current_page = "chat"
        st.rerun()
    if st.button("📋 Compliance Report", use_container_width=True):
        st.session_state.current_page = "report"
        st.session_state.report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.rerun()
    
    st.markdown("---")
    
    # Show chat stats in sidebar
    if st.session_state.history:
        st.metric("Chat Messages", len(st.session_state.history))
    
    if st.button("🗑️ Clear Chat History", type="secondary", use_container_width=True):
        st.session_state.history = []
        st.session_state.current_page = "chat"
        st.rerun()


# ============================================================================
# CHAT PAGE
# ============================================================================
if st.session_state.current_page == "chat":
    st.title("📚 NSW Procurement Compliance Agent")
    st.write(f"An agent to check contract/subcontract data, recent news articles and sentiment, and apply NSW Procurement Policies.")
    st.write(f"Endpoint name: `{SERVING_ENDPOINT}`")
    st.write(f"Example Prompt: Find some recent negative news articles and suggest methods to ensure supplier compliance with those suppliers by referring to the NSW policy")

    # --- Render chat history ---
    for i, element in enumerate(st.session_state.history):
        element.render(i)
    
    # --- Chat input (only on chat page) ---
    prompt = st.chat_input("Ask a question")
    if prompt:
        # Get the task type for this endpoint
        task_type = _get_endpoint_task_type(SERVING_ENDPOINT)
        
        # Add user message to chat history
        user_msg = UserMessage(content=prompt)
        st.session_state.history.append(user_msg)
        user_msg.render(len(st.session_state.history) - 1)

        # Convert history to standard chat message format for the query methods
        input_messages = [msg for elem in st.session_state.history for msg in elem.to_input_messages()]
        
        # Handle the response using the appropriate handler
        assistant_response = query_endpoint_and_render(task_type, input_messages)
        
        # Add assistant response to history
        st.session_state.history.append(assistant_response)


# ============================================================================
# COMPLIANCE REPORT PAGE
# ============================================================================
elif st.session_state.current_page == "report":
    st.title("📊 Compliance Due Diligence Report")
    
    timestamp = st.session_state.get("report_timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.caption(f"Generated: {timestamp}")
    
    if not st.session_state.history:
        st.warning("⚠️ No chat history available. Please have a conversation on the Chat page first before generating a report.")
        st.info("💡 Go to the Chat page and ask questions about suppliers, contracts, or compliance issues.")
    else:
        # Extract compliance data
        with st.spinner("Analyzing chat history and extracting compliance data..."):
            compliance_data = extract_compliance_data(st.session_state.history)
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", compliance_data["total_messages"])
        with col2:
            st.metric("Suppliers at Risk", len(compliance_data["suppliers_at_risk"]))
        with col3:
            st.metric("Compliance Actions", len(compliance_data["compliance_actions"]))
        
        st.markdown("---")
        
        # Create tabs for different sections
        tab1, tab2, tab3 = st.tabs(["🚨 Suppliers at Risk", "✅ Compliance Actions", "📥 Export"])
        
        # ====================================================================
        # TAB 1: SUPPLIERS AT RISK
        # ====================================================================
        with tab1:
            st.subheader("Suppliers at Risk")
            
            if compliance_data["suppliers_at_risk"]:
                with st.form("suppliers_risk_form"):
                    st.write(f"Identified **{len(compliance_data['suppliers_at_risk'])}** supplier(s) with potential risk indicators:")
                    st.markdown("")
                    
                    for idx, supplier_info in enumerate(compliance_data["suppliers_at_risk"]):
                        with st.container():
                            # Supplier header with severity badge
                            severity_color = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
                            severity_badge = severity_color.get(supplier_info["severity"], "⚪")
                            
                            st.markdown(f"### {severity_badge} {supplier_info['supplier_name']}")
                            
                            col1, col2 = st.columns([1, 1])
                            with col1:
                                st.markdown(f"**Risk Type:** {supplier_info['risk_type']}")
                            with col2:
                                st.markdown(f"**Severity:** {supplier_info['severity']}")
                            
                            st.markdown("**Risk Details:**")
                            for detail_idx, detail in enumerate(supplier_info["details"]):
                                with st.expander(f"Detail {detail_idx + 1}", expanded=detail_idx == 0):
                                    st.info(detail)
                            
                            # Allow users to add notes
                            st.text_area(
                                "Internal Notes / Follow-up Actions",
                                key=f"supplier_notes_{idx}",
                                placeholder="Add any notes, follow-up actions, or assessment for this supplier...",
                                height=100
                            )
                            
                            st.markdown("---")
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        submitted = st.form_submit_button("💾 Save Notes", type="primary", use_container_width=True)
                    
                    if submitted:
                        st.success("✅ Notes saved to session!")
                        st.balloons()
            else:
                st.info("ℹ️ No suppliers at risk identified in the conversation.")
                st.markdown("""
                **Tips for better detection:**
                - Ask the agent about specific suppliers
                - Request risk assessments or compliance checks
                - Inquire about negative news or issues with suppliers
                """)
        
        # ====================================================================
        # TAB 2: COMPLIANCE ACTIONS
        # ====================================================================
        with tab2:
            st.subheader("Recommended Compliance Due Diligence Actions")
            
            if compliance_data["compliance_actions"]:
                # Group actions by priority
                high_priority = [a for a in compliance_data["compliance_actions"] if a["priority"] == "High"]
                medium_priority = [a for a in compliance_data["compliance_actions"] if a["priority"] == "Medium"]
                low_priority = [a for a in compliance_data["compliance_actions"] if a["priority"] == "Low"]
                
                with st.form("compliance_actions_form"):
                    st.write(f"Identified **{len(compliance_data['compliance_actions'])}** recommended compliance action(s):")
                    st.markdown("")
                    
                    # Display by priority
                    if high_priority:
                        st.markdown("### 🔴 High Priority Actions")
                        for idx, action_info in enumerate(high_priority):
                            render_action_item(action_info, f"high_{idx}")
                    
                    if medium_priority:
                        st.markdown("### 🟡 Medium Priority Actions")
                        for idx, action_info in enumerate(medium_priority):
                            render_action_item(action_info, f"medium_{idx}")
                    
                    if low_priority:
                        st.markdown("### 🟢 Low Priority Actions")
                        for idx, action_info in enumerate(low_priority):
                            render_action_item(action_info, f"low_{idx}")
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        submitted = st.form_submit_button("💾 Save Actions", type="primary", use_container_width=True)
                    
                    if submitted:
                        st.success("✅ Action status saved to session!")
                        st.balloons()
            else:
                st.info("ℹ️ No specific compliance actions identified.")
                st.markdown("""
                **Tips for better detection:**
                - Ask the agent for recommendations on due diligence steps
                - Request compliance checklists or action items
                - Inquire about next steps for supplier management
                """)
        
        # ====================================================================
        # TAB 3: EXPORT
        # ====================================================================
        with tab3:
            st.subheader("Export Compliance Report")
            st.write("Download the compliance data in various formats for sharing and documentation:")
            st.markdown("")
            
            # Prepare export data
            export_data = {
                "report_metadata": {
                    "generated_timestamp": timestamp,
                    "total_messages_analyzed": compliance_data["total_messages"],
                    "suppliers_at_risk_count": len(compliance_data["suppliers_at_risk"]),
                    "compliance_actions_count": len(compliance_data["compliance_actions"])
                },
                "suppliers_at_risk": compliance_data["suppliers_at_risk"],
                "compliance_actions": compliance_data["compliance_actions"]
            }
            
            col1, col2 = st.columns(2)
            
            with col1:
                # JSON export
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="📥 Download as JSON",
                    data=json_str,
                    file_name=f"compliance_report_{timestamp.replace(' ', '_').replace(':', '-')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            with col2:
                # Text export
                txt_report = format_text_report(export_data, timestamp)
                st.download_button(
                    label="📄 Download as Text",
                    data=txt_report,
                    file_name=f"compliance_report_{timestamp.replace(' ', '_').replace(':', '-')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Preview export data
            with st.expander("👁️ Preview Export Data (JSON)"):
                st.json(export_data)
            
            st.markdown("---")
            st.caption("💡 **Tip:** Use the JSON format for integration with other systems or the text format for reports and documentation.")