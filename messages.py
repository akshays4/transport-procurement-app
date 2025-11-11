"""
Message classes for the chatbot application.

This module contains the message classes used throughout the app.
By keeping them in a separate module, they remain stable across
Streamlit app reruns, avoiding isinstance comparison issues.
"""
import streamlit as st
from abc import ABC, abstractmethod
import re
import html


def clean_html_and_special_chars(content):
    """
    Remove HTML tags and clean up special characters from content.
    This provides a safety layer to clean up any HTML markup that gets through.
    """
    if not content:
        return content
    
    # Remove common HTML tags
    content = re.sub(r'<table[^>]*>.*?</table>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<tr[^>]*>.*?</tr>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<td[^>]*>.*?</td>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<th[^>]*>.*?</th>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<tbody[^>]*>.*?</tbody>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content = re.sub(r'<thead[^>]*>.*?</thead>', '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove any remaining HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    
    # Unescape HTML entities
    content = html.unescape(content)
    
    # Clean up extra whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r' {2,}', ' ', content)
    
    return content.strip()


def extract_and_hide_footnotes(content):
    """
    Extract verbose footnotes from knowledge assistant responses and return
    cleaned content and footnotes separately.
    
    Returns: (cleaned_content, footnotes_text)
    """
    if not content:
        return content, None
    
    # Pattern to match "Footnotes" section with verbose content
    # Matches from "Footnotes" or "References:" to end or next major section
    footnote_patterns = [
        # Pattern 1: "Footnotes" followed by numbered items with ↩ or similar
        r'\n\s*Footnotes?\s*\n(.*?)(?=\n\n[A-Z]|\n\n---|\Z)',
        # Pattern 2: Numbered footnotes with superscript-like markers
        r'\n\s*(?:\d+\.?\s*<table|¹.*?<table).*?(?=\n\n[A-Z]|\Z)',
        # Pattern 3: Any section with heavy HTML table markup
        r'\n\s*(?:References?:?\s*\n)?(.*?<table.*?</table>.*?)(?=\n\n[A-Z]|\Z)',
    ]
    
    footnotes_found = None
    cleaned_content = content
    
    for pattern in footnote_patterns:
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            footnotes_found = match.group(0).strip()
            # Remove the footnote section from main content
            cleaned_content = content[:match.start()] + content[match.end():]
            break
    
    # Also check for <think> tags and remove them
    think_pattern = r'<think>.*?</think>'
    if re.search(think_pattern, cleaned_content, re.DOTALL):
        cleaned_content = re.sub(think_pattern, '', cleaned_content, flags=re.DOTALL)
    
    # Clean up extra whitespace
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content).strip()
    
    return cleaned_content, footnotes_found


def strip_structured_data(content):
    """
    Remove structured data markers and JSON from content for display.
    Keeps the original content intact for extraction but hides it from users.
    """
    if not content:
        return content
    
    # Remove the entire structured data section
    pattern = r'\s*---STRUCTURED_DATA---.*?---END_STRUCTURED_DATA---\s*'
    cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Clean up any extra whitespace left behind
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
    cleaned_content = cleaned_content.strip()
    
    return cleaned_content


class Message(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def to_input_messages(self):
        """Convert this message into a list of dicts suitable for the model API."""
        pass

    @abstractmethod
    def render(self, idx):
        """Render the message in the Streamlit app."""
        pass


class UserMessage(Message):
    def __init__(self, content):
        super().__init__()
        self.content = content

    def to_input_messages(self):
        return [{
            "role": "user",
            "content": self.content
        }]

    def render(self, _):
        with st.chat_message("user"):
            st.markdown(self.content)


class AssistantResponse(Message):
    def __init__(self, messages, request_id):
        super().__init__()
        self.messages = messages
        # Request ID tracked to enable submitting feedback on assistant responses via the feedback endpoint
        self.request_id = request_id

    def to_input_messages(self):
        return self.messages

    def render(self, idx):
        with st.chat_message("assistant"):
            for msg in self.messages:
                render_message(msg)

            if self.request_id is not None:
                render_assistant_message_feedback(idx, self.request_id)


def render_message(msg):
    """Render a single message."""
    if msg["role"] == "assistant":
        # Render content first if it exists
        if msg.get("content"):
            # Check if structured data exists
            has_structured_data = "---STRUCTURED_DATA---" in msg["content"]
            
            # Strip structured data for display (but keep it in the original message)
            display_content = strip_structured_data(msg["content"])
            
            # Extract and hide verbose footnotes
            display_content, footnotes = extract_and_hide_footnotes(display_content)
            
            # Clean HTML tags and special characters
            display_content = clean_html_and_special_chars(display_content)
            
            if display_content:  # Only display if there's content after stripping
                st.markdown(display_content)
            
            # Show footnotes in an expander if they exist and contain verbose content
            if footnotes and (len(footnotes) > 200 or '<table>' in footnotes.lower()):
                # Create a container to prevent scroll jump
                with st.container():
                    with st.expander("📚 View detailed source references", expanded=False):
                        st.caption("*Detailed citations and source information*")
                        # Clean the footnotes before displaying
                        cleaned_footnotes = clean_html_and_special_chars(footnotes)
                        
                        # Escape HTML to prevent injection, but preserve formatting
                        import html as html_lib
                        escaped_footnotes = html_lib.escape(cleaned_footnotes)
                        
                        # Create a scrollable container for the footnotes with scroll anchoring
                        # Use markdown with a div for scrolling
                        scrollable_html = f"""
                        <div style="max-height: 400px; overflow-y: auto; overflow-x: hidden; 
                                    padding: 10px; background-color: #f8f9fa; border-radius: 5px; 
                                    border: 1px solid #dee2e6; font-family: monospace; 
                                    font-size: 12px; line-height: 1.5; color: #212529; 
                                    position: relative; width: 100%; box-sizing: border-box;
                                    overflow-anchor: auto; scroll-margin-top: 20px;">
                            <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; color: #212529;">{escaped_footnotes}</pre>
                        </div>
                        """
                        st.markdown(scrollable_html, unsafe_allow_html=True)
                        
                        if len(cleaned_footnotes) > 1000:
                            st.caption(f"*{len(cleaned_footnotes):,} characters • Scroll to view all references*")
            
            # Add subtle indicator if structured data was captured
            if has_structured_data:
                st.caption("📋 *Compliance data captured for reporting*")
        
        # Then render tool calls if they exist
        if "tool_calls" in msg and msg["tool_calls"]:
            for call in msg["tool_calls"]:
                fn_name = call["function"]["name"]
                args = call["function"]["arguments"]
                st.markdown(f"🛠️ Calling **`{fn_name}`** with:\n```json\n{args}\n```")
    elif msg["role"] == "tool":
        # Always display tool responses in a scrollable container
        import html as html_lib
        import json
        
        st.markdown("🧰 Tool Response:")
        
        tool_content = msg["content"]
        
        # Clean HTML and extract footnotes
        cleaned_content, footnotes = extract_and_hide_footnotes(tool_content)
        cleaned_content = clean_html_and_special_chars(cleaned_content)
        
        # Escape HTML for safe display
        escaped_content = html_lib.escape(cleaned_content)
        
        # Always show in scrollable container (no length check)
        scrollable_html = f"""
        <div style="max-height: 400px; overflow-y: auto; overflow-x: hidden; 
                    padding: 10px; background-color: #f8f9fa; border-radius: 5px; 
                    border: 1px solid #dee2e6; font-family: monospace; 
                    font-size: 12px; line-height: 1.5; color: #212529; 
                    position: relative; width: 100%; box-sizing: border-box;">
            <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; color: #212529;">{escaped_content}</pre>
        </div>
        """
        st.markdown(scrollable_html, unsafe_allow_html=True)
        
        # Show character count for long responses
        if len(cleaned_content) > 1000:
            st.caption(f"*{len(cleaned_content):,} characters • Scroll to view all content*")
        
        # Show footnotes in expander if detected
        if footnotes and (len(footnotes) > 200 or '<table>' in footnotes.lower() or 'footnote' in footnotes.lower()):
            # Create a container to prevent scroll jump
            with st.container():
                with st.expander("📚 View detailed source references", expanded=False):
                    st.caption("*Detailed citations and source information*")
                    cleaned_footnotes = clean_html_and_special_chars(footnotes)
                    escaped_footnotes = html_lib.escape(cleaned_footnotes)
                    
                    scrollable_footnotes_html = f"""
                    <div style="max-height: 400px; overflow-y: auto; overflow-x: hidden; 
                                padding: 10px; background-color: #f8f9fa; border-radius: 5px; 
                                border: 1px solid #dee2e6; font-family: monospace; 
                                font-size: 12px; line-height: 1.5; color: #212529; 
                                position: relative; width: 100%; box-sizing: border-box;
                                overflow-anchor: auto; scroll-margin-top: 20px;">
                        <pre style="white-space: pre-wrap; word-wrap: break-word; margin: 0; color: #212529;">{escaped_footnotes}</pre>
                    </div>
                    """
                    st.markdown(scrollable_footnotes_html, unsafe_allow_html=True)
                    
                    if len(cleaned_footnotes) > 1000:
                        st.caption(f"*{len(cleaned_footnotes):,} characters • Scroll to view all references*")


@st.fragment
def render_assistant_message_feedback(i, request_id):
    """Render feedback UI for assistant messages."""
    from model_serving_utils import submit_feedback
    import os
    
    def save_feedback(index):
        serving_endpoint = os.getenv('SERVING_ENDPOINT')
        if serving_endpoint:
            submit_feedback(
                endpoint=serving_endpoint,
                request_id=request_id,
                rating=st.session_state[f"feedback_{index}"]
            )
    
    st.feedback("thumbs", key=f"feedback_{i}", on_change=save_feedback, args=[i])