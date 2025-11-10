# Structured Output Implementation Guide

## Overview

This guide explains how to configure your multi-agent supervisor to output structured compliance data that integrates seamlessly with the Compliance Report page.

## Benefits of Structured Output

### Before (Regex-based extraction):
- ❌ Inconsistent extraction accuracy
- ❌ Missed data due to varying language patterns
- ❌ Difficulty with complex risk assessments
- ❌ Limited metadata (no rationale, evidence, etc.)
- ❌ Messy JSON visible in chat

### After (JSON-based structured output):
- ✅ 100% accurate extraction when format is followed
- ✅ Rich metadata (rationale, evidence, severity, priority)
- ✅ Consistent categorization
- ✅ Backward compatible with unstructured responses
- ✅ Easy to extend with new fields
- ✅ **Structured data automatically hidden from chat display**
- ✅ Clean user experience with subtle indicator

## Implementation Steps

### Step 1: Configure Your Agent System Prompt

Use the system prompt provided in `suggested_system_prompt.md` when configuring your multi-agent supervisor or LLM endpoint.

**In Databricks:**
1. Go to your Agent/Model Serving configuration
2. Update the system prompt section
3. Include the entire prompt from `suggested_system_prompt.md`

**For MLflow Model:**
```python
import mlflow

system_prompt = """
[Content from suggested_system_prompt.md]
"""

# When logging your model
mlflow.langchain.log_model(
    lc_model=your_agent,
    artifact_path="agent",
    registered_model_name="transport-compliance-agent",
    input_example={"messages": [{"role": "user", "content": "example"}]},
    metadata={"system_prompt": system_prompt}
)
```

### Step 2: Understand the Display Behavior

**Important:** The structured data section is automatically hidden from the chat display to keep the interface clean:

- ✅ **Natural language responses** are displayed normally
- ❌ **Structured JSON blocks** are hidden from users
- 📋 A **subtle indicator** shows when compliance data was captured
- 💾 **Full content with JSON** is saved in session history for extraction

**What users see:**
```
[Agent's natural language response about the supplier risks...]

📋 Compliance data captured for reporting
```

**What's in the actual message (used by extraction):**
```
[Agent's natural language response about the supplier risks...]

---STRUCTURED_DATA---
{
  "suppliers_at_risk": [...],
  "compliance_actions": [...]
}
---END_STRUCTURED_DATA---
```

This design provides:
- Clean, professional chat interface
- No confusing JSON for end users
- Full data preservation for reporting
- Visual confirmation that data was captured

### Step 3: Test the Structured Output

Ask your agent questions that should trigger risk identification:

**Example Test Queries:**
```
1. "What do you know about ABC Transport Services? Are there any compliance risks?"

2. "Search for recent negative news about XYZ Logistics and suggest compliance actions."

3. "Analyze supplier DEF Construction for any financial or operational risks."
```

**Expected Response Format:**
```
[Natural conversation response here...]

---STRUCTURED_DATA---
{
  "suppliers_at_risk": [
    {
      "supplier_name": "ABC Transport Services",
      "risk_type": "Financial Risk",
      "severity": "High",
      "summary": "Company showing signs of financial distress with increasing debt levels",
      "evidence": "Q3 2024 financial report, credit rating downgrade from Moody's"
    }
  ],
  "compliance_actions": [
    {
      "action": "Conduct immediate financial audit of ABC Transport Services",
      "category": "Audit/Review",
      "priority": "High",
      "rationale": "Financial instability may impact ability to complete contracted work"
    }
  ]
}
---END_STRUCTURED_DATA---
```

### Step 4: Verify Extraction

1. Have a conversation with your agent
2. Look for the "📋 *Compliance data captured for reporting*" indicator in the chat
3. Navigate to the "Compliance Report" page
4. Check that:
   - Suppliers are correctly identified with severity and risk type
   - Actions include category, priority, and rationale
   - All structured data is properly extracted
   - No invalid entries (like "compliance" or tool responses)

### Step 5: Fallback Handling

The application automatically falls back to regex-based extraction if:
- The agent doesn't include structured data markers
- The JSON parsing fails
- You're working with older conversation history

This ensures backward compatibility!

## Structured Data Schema

### Suppliers at Risk

```json
{
  "supplier_name": "string (required)",
  "risk_type": "Financial Risk | Compliance Risk | Reputational Risk | Operational Risk",
  "severity": "High | Medium | Low",
  "summary": "string (1-2 sentences)",
  "evidence": "string (specific sources)"
}
```

**Field Descriptions:**

- **supplier_name**: Exact legal or trading name of the supplier
- **risk_type**: Primary category of risk identified
- **severity**: Risk level based on impact and urgency
- **summary**: Concise description of the specific risk
- **evidence**: Verifiable sources (news articles, reports, data)

### Compliance Actions

```json
{
  "action": "string (required, imperative form)",
  "category": "Audit/Review | Verification | Documentation | Monitoring | Communication",
  "priority": "High | Medium | Low",
  "rationale": "string (why this action is necessary)"
}
```

**Field Descriptions:**

- **action**: Clear, actionable description using imperative verbs
- **category**: Type of compliance activity
- **priority**: Urgency level for completion
- **rationale**: Business justification for the action

## Prompt Engineering Tips

### For Better Supplier Detection:

1. **Be Specific in Risk Type:**
   ```
   ❌ "This supplier has issues"
   ✅ "This supplier shows Reputational Risk due to negative media coverage"
   ```

2. **Include Evidence:**
   ```
   ❌ "Poor financial health"
   ✅ "Debt-to-equity ratio increased 40% (Source: 2024 Annual Report)"
   ```

3. **Use Severity Consistently:**
   - High: Immediate procurement impact, requires urgent action
   - Medium: Moderate concern, standard monitoring
   - Low: Minor issue, routine oversight sufficient

### For Better Action Detection:

1. **Use Action Verbs:**
   ```
   ❌ "It would be good to check their finances"
   ✅ "Conduct financial audit of supplier's last three years of statements"
   ```

2. **Categorize Appropriately:**
   - Audit/Review: Formal assessments
   - Verification: Fact-checking, validation
   - Documentation: Record-keeping, reporting
   - Monitoring: Ongoing surveillance
   - Communication: Stakeholder engagement

3. **Explain the Why:**
   ```
   ❌ Just listing actions
   ✅ Including rationale: "...to ensure compliance with NSW Procurement Policy 2.3.4"
   ```

## Advanced Configuration

### Custom Risk Types

You can extend the risk types by modifying the system prompt:

```
- **risk_type**: Choose the most relevant category:
  - Financial Risk: ...
  - Compliance Risk: ...
  - Reputational Risk: ...
  - Operational Risk: ...
  - Environmental Risk: [NEW]
  - Cybersecurity Risk: [NEW]
```

Then update the extraction in `app.py` to handle these new types.

### Custom Action Categories

Similarly, you can add new action categories:

```
- **category**: Choose the most appropriate:
  - Audit/Review: ...
  - Verification: ...
  - Documentation: ...
  - Monitoring: ...
  - Communication: ...
  - Escalation: [NEW]
  - Training: [NEW]
```

### Multi-Language Support

The structured JSON format makes it easy to support multiple languages:

1. Keep JSON keys in English
2. Allow values in local language
3. Update the extraction logic to handle Unicode properly

## Knowledge Assistant Citation Cleanup

### Problem: Excessive Footnotes and Poor Formatting

When using knowledge assistant tools (like Databricks Genie), responses often include:
- Verbose footnotes with raw HTML table markup
- Duplicate citation content
- Internal file system URLs
- Poorly formatted reference sections

### Solution: System Prompt Instructions

The updated system prompt now includes specific instructions for cleaning up knowledge assistant responses:

**What the agent will now do:**
- ✅ Remove `<think>` tags and internal reasoning
- ✅ Remove raw HTML markup from footnotes
- ✅ Convert verbose citations to clean inline references
- ✅ Deduplicate repeated citations
- ✅ Present information in a readable format

**Example transformation:**

**Before (from knowledge assistant):**
```
You must monitor supplier compliance.1

Footnotes
1. <table><tr><th>Relating to</th>...[200 lines of HTML]... ↩
```

**After (cleaned by agent):**
```
Based on the NSW Procurement Policy Framework, you must monitor supplier 
compliance on an ongoing basis (Supplier Due Diligence Guide, Dec 2024).
```

### Implementation

This is automatically handled by the updated system prompt. No code changes needed.

## Troubleshooting

### Issue: Structured data not being extracted

**Possible Causes:**
1. Agent not following the format exactly
2. JSON syntax errors in agent output
3. Missing markers (`---STRUCTURED_DATA---`)

**Solutions:**
- Check agent logs for the actual output
- Verify system prompt is correctly applied
- Test with manual JSON response to isolate issue
- Check browser console for JavaScript errors

### Issue: Incomplete data in report

**Possible Causes:**
1. Deduplication removing valid entries
2. Data falling below minimum length thresholds
3. JSON parsing failing silently

**Solutions:**
- Review extraction limits in `extract_compliance_data()` function
- Check logger warnings for JSON parsing errors
- Temporarily disable deduplication to see raw extracted data

### Issue: Backward compatibility problems

**Possible Causes:**
1. Old messages not being extracted
2. Regex patterns too restrictive

**Solutions:**
- Ensure fallback extraction is still active
- Test with both structured and unstructured responses
- Update regex patterns in extraction function if needed

### Issue: Excessive footnotes and HTML markup in responses

**Possible Causes:**
1. Knowledge assistant tool returning verbose citations
2. Agent not processing tool responses properly
3. System prompt not being followed

**Solutions:**
- Ensure the updated system prompt (with citation cleanup instructions) is deployed
- Verify the agent is receiving and processing the system prompt correctly
- Check that the agent is cleaning up knowledge assistant responses before presenting them
- Review the agent's tool call handling logic
- Test with a simple query to verify footnote cleanup is working

**Quick Test:**
Ask the agent a policy question and verify the response:
- ✅ Should have clean inline citations like "(NSW Procurement Policy, Section 2.03)"
- ✅ Should have a simple References section if needed
- ❌ Should NOT have raw HTML `<table>` tags
- ❌ Should NOT have duplicate footnote content
- ❌ Should NOT have `<think>` tags visible

## Testing Checklist

Before deploying to production:

- [ ] Agent outputs valid JSON in structured format
- [ ] Structured data extracts correctly to report
- [ ] Fallback to regex works for unstructured responses
- [ ] All severity levels display correctly (High/Medium/Low)
- [ ] All action priorities work (High/Medium/Low)
- [ ] Rationale displays when present
- [ ] Evidence displays in supplier details
- [ ] Export functions include all structured fields
- [ ] Special characters in supplier names handled correctly
- [ ] Long action descriptions don't break layout
- [ ] **Knowledge assistant citations are clean (no HTML markup)**
- [ ] **Footnotes are deduplicated and readable**
- [ ] **`<think>` tags are removed from responses**
- [ ] **References section is formatted cleanly when present**

## Example Implementation

Here's a complete example of testing the implementation:

```python
# Test script to validate structured output
import requests
import json

endpoint_url = "https://your-databricks-instance/serving-endpoints/your-endpoint/invocations"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

test_query = {
    "messages": [
        {
            "role": "user",
            "content": "Check if there are any risks with ABC Transport Services"
        }
    ]
}

response = requests.post(endpoint_url, headers=headers, json=test_query)
result = response.json()

# Check for structured data
if "---STRUCTURED_DATA---" in result["choices"][0]["message"]["content"]:
    print("✅ Structured data present")
else:
    print("❌ No structured data found")

# Validate JSON
try:
    # Extract and parse JSON
    import re
    pattern = r'---STRUCTURED_DATA---\s*(\{.*?\})\s*---END_STRUCTURED_DATA---'
    match = re.search(pattern, result["choices"][0]["message"]["content"], re.DOTALL)
    if match:
        data = json.loads(match.group(1))
        print(f"✅ Valid JSON with {len(data.get('suppliers_at_risk', []))} suppliers")
        print(f"✅ Valid JSON with {len(data.get('compliance_actions', []))} actions")
except:
    print("❌ JSON parsing failed")
```

## Support

For issues or questions:
1. Check the agent logs in Databricks
2. Review the browser console for extraction errors
3. Test with the provided example queries
4. Verify the system prompt is correctly configured

## Future Enhancements

Potential improvements to consider:

1. **Automated Risk Scoring**: Calculate overall risk scores based on multiple factors
2. **Historical Tracking**: Compare current risks with historical data
3. **Integration with External Systems**: Push data to procurement management systems
4. **Automated Workflows**: Trigger approval workflows based on risk levels
5. **Dashboard Visualizations**: Add charts and graphs for risk trends
6. **Notification System**: Email alerts for high-priority risks
7. **Collaborative Annotations**: Allow multiple users to add notes
8. **Audit Trail**: Track all changes and decisions made in the system

---

**Last Updated:** October 2025  
**Version:** 1.0  
**Compatibility:** Streamlit app v1.0+

