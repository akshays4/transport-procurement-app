# Knowledge Assistant System Prompt Setup Guide

## Overview

This guide explains how to configure your NSW Procurement Policy knowledge assistant endpoint with a system prompt that produces clean, readable responses with concise footnotes (no HTML markup or verbose citations).

## The Problem

By default, Databricks Genie/Knowledge Assistant endpoints may return responses with:
- ❌ Verbose footnotes containing HTML table markup
- ❌ Duplicate citation information repeated multiple times
- ❌ Internal file paths and metadata
- ❌ Poorly formatted reference sections

**Example of default output:**
```
You must monitor compliance.¹

Footnotes:
¹ <table><tr><th>Relating to</th><th>Status</th>...[200 lines]...</table> ↩
```

## The Solution

Apply a custom system prompt to the knowledge assistant endpoint that instructs it to:
- ✅ Use clean, concise citations
- ✅ Avoid HTML markup in footnotes
- ✅ Deduplicate references
- ✅ Format responses for readability

**Example of improved output:**
```
You must monitor supplier compliance on an ongoing basis. The level and 
frequency of checks will vary depending on the value and risk profile of 
the contract (Supplier Due Diligence Guide, NSW Procurement Policy Framework).
```

## Implementation Steps

### Step 1: Locate Your Knowledge Assistant Endpoint

1. Log in to your Databricks workspace
2. Navigate to **Serving** → **Serving Endpoints**
3. Find your knowledge assistant endpoint (e.g., `nsw-procurement-policy-ka`)
4. Click on the endpoint name to open its configuration

### Step 2: Access System Instructions

The location of system instructions depends on your Databricks setup:

#### For Databricks Genie Knowledge Assistants:

1. Open the Genie app associated with your endpoint
2. Go to **Settings** or **Configuration**
3. Look for **"Instructions"** or **"System Instructions"** section
4. This is where you'll add the system prompt

#### For Custom Knowledge Assistant Endpoints:

1. In the endpoint configuration page
2. Look for **"Model Configuration"** or **"System Prompt"** section
3. Click **"Edit"** or **"Configure"**

### Step 3: Apply the System Prompt

1. **Copy the entire contents** of `knowledge_assistant_system_prompt.md`
2. **Paste into the system instructions/prompt field**
3. **Save the configuration**
4. **Redeploy the endpoint** if necessary (Databricks will prompt you)

### Step 4: Test the Configuration

Run a test query to verify the new formatting:

**Test Query:**
```
What are the NSW procurement policy requirements for supplier compliance monitoring?
```

**Expected Response Characteristics:**
- ✅ Clean, structured response
- ✅ Inline citations like "(Source Name, Section X)"
- ✅ Simple References section at the end
- ✅ No HTML tags (`<table>`, `<tr>`, `<td>`)
- ✅ No duplicate footnotes
- ✅ No internal file paths

**Red Flags (indicates system prompt not applied):**
- ❌ HTML table markup in footnotes
- ❌ `<think>` tags visible
- ❌ Duplicate citation content
- ❌ File system URLs

## Configuration Examples

### Example 1: Databricks Genie Configuration

**Location:** Genie App → Settings → Instructions

**What to add:**
```
[Paste entire content from knowledge_assistant_system_prompt.md]
```

**Save and Test:**
- Click "Save" or "Update"
- Wait for changes to propagate (may take 1-2 minutes)
- Test with a policy question

### Example 2: Using Databricks API

If you're managing endpoints via API:

```python
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Update the endpoint configuration
w.serving_endpoints.update_config(
    name="nsw-procurement-policy-ka",
    served_entities=[{
        "entity_name": "your-genie-space-name",
        "scale_to_zero_enabled": True,
        "workload_size": "Small",
        "environment_vars": {
            "SYSTEM_PROMPT": open('knowledge_assistant_system_prompt.md').read()
        }
    }]
)
```

**Note:** The exact API method may vary based on your Databricks version and endpoint type.

### Example 3: Genie Space Configuration File

If using Genie space YAML configuration:

```yaml
name: NSW Procurement Policy Assistant
description: Knowledge assistant for NSW procurement policies

instructions: |
  [Content from knowledge_assistant_system_prompt.md]
  
sources:
  - unity_catalog:
      catalog: procurement_demo
      schema: default
      volume: policies
```

## Verification Process

### Quick Verification Test

**Test 1: Simple Policy Query**
```
Query: "What are the payment terms for small businesses?"
Expected: Clean response with inline citation
Check for: No HTML markup
```

**Test 2: Complex Multi-Source Query**
```
Query: "What are all the supplier conduct requirements?"
Expected: Structured response with References section
Check for: Deduplicated citations, no duplicate content
```

**Test 3: Specific Document Reference**
```
Query: "What does Section 2.03 say about contract management?"
Expected: Direct quote or summary with clear section reference
Check for: Clean footnote format
```

### Detailed Verification Checklist

- [ ] System prompt deployed to knowledge assistant endpoint
- [ ] Endpoint redeployed/restarted (if required)
- [ ] Test query returns response
- [ ] Response has clean citations (inline or numbered)
- [ ] No HTML tags visible in response
- [ ] No `<table>`, `<tr>`, `<td>` markup
- [ ] No duplicate footnote content
- [ ] References section is clean and readable (if present)
- [ ] Citations include source name and section
- [ ] Response is well-structured with headings
- [ ] Information accuracy maintained

## Troubleshooting

### Issue 1: HTML Markup Still Appearing

**Symptoms:**
- Footnotes still contain `<table>` tags
- Duplicate citation information
- Verbose metadata in footnotes

**Possible Causes:**
1. System prompt not applied correctly
2. Endpoint not redeployed after configuration change
3. Caching issues
4. Prompt not in the correct configuration field

**Solutions:**
```bash
# Verify endpoint configuration
databricks serving-endpoints get --name nsw-procurement-policy-ka

# Check if system prompt is present in config
# Look for instructions/system_prompt field

# Redeploy endpoint if needed
databricks serving-endpoints update --name nsw-procurement-policy-ka --json @config.json
```

**Manual Steps:**
1. Re-check that system prompt was saved
2. Restart the endpoint
3. Clear any cached responses
4. Test with a fresh query in a new session

### Issue 2: System Prompt Not Taking Effect

**Symptoms:**
- Knowledge assistant ignoring formatting instructions
- Still using default citation format
- No change in response style

**Possible Causes:**
1. Wrong configuration field
2. Genie-specific configuration needed
3. Endpoint type doesn't support system prompts

**Solutions:**

For **Databricks Genie**:
- System prompts may be called "Instructions" in Genie
- Check Genie Space settings, not endpoint settings
- May need to update the Genie Space configuration directly

For **Custom Endpoints**:
- Verify endpoint type supports custom system prompts
- Check if there's a separate "Instructions" or "Behavior" configuration
- Consult Databricks documentation for your specific endpoint type

### Issue 3: Citations Missing Entirely

**Symptoms:**
- Response has no citations or references
- Information provided without sources

**Possible Causes:**
1. System prompt removed default citation behavior
2. Instructions interpreted too strictly

**Solutions:**
- Review the system prompt - ensure it encourages citations
- Modify the prompt to emphasize: "Always cite your sources"
- Test with specific citation-focused queries

### Issue 4: Response Quality Degraded

**Symptoms:**
- Responses less comprehensive than before
- Missing important policy details
- Overly brief responses

**Possible Causes:**
1. "Concise" instruction interpreted too aggressively
2. System prompt limiting response completeness

**Solutions:**
- Adjust system prompt to balance conciseness with completeness
- Add instruction: "Provide comprehensive policy information while keeping citations concise"
- Test with queries requiring detailed responses

## Integration with Main Agent

This knowledge assistant system prompt works in conjunction with the main agent's system prompt:

### Two-Layer Approach

**Layer 1: Knowledge Assistant** (this prompt)
- Produces clean responses at the source
- Formats citations properly
- Removes HTML markup

**Layer 2: Main Agent** (`suggested_system_prompt.md`)
- Can further clean up if needed
- Synthesizes information from multiple tools
- Adds structured output for compliance tracking

### Recommended Setup

For **best results**, apply both:
1. ✅ Knowledge assistant system prompt (this guide)
2. ✅ Main agent system prompt (suggested_system_prompt.md)

This provides **defense in depth**:
- Primary cleanup happens at the knowledge assistant
- Secondary cleanup happens at the main agent
- Even if one layer fails, the other catches issues

## Testing Script

Save this as `test_knowledge_assistant.py`:

```python
"""Test script for knowledge assistant formatting."""
import requests
import os
import re

ENDPOINT_URL = os.getenv("DATABRICKS_ENDPOINT_URL")
TOKEN = os.getenv("DATABRICKS_TOKEN")

def test_knowledge_assistant(query):
    """Test a single query against the knowledge assistant."""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [{"role": "user", "content": query}]
    }
    
    response = requests.post(ENDPOINT_URL, headers=headers, json=payload)
    result = response.json()
    
    content = result["choices"][0]["message"]["content"]
    
    # Check for issues
    issues = []
    
    if "<table>" in content or "<tr>" in content or "<td>" in content:
        issues.append("❌ HTML table markup found")
    else:
        print("✅ No HTML table markup")
    
    if "<think>" in content:
        issues.append("❌ Think tags visible")
    else:
        print("✅ No think tags")
    
    # Count duplicate lines (basic check)
    lines = content.split('\n')
    unique_lines = set(lines)
    if len(lines) > len(unique_lines) * 1.2:  # 20% tolerance
        issues.append("⚠️  Possible duplicate content")
    else:
        print("✅ No obvious duplication")
    
    # Check for clean citations
    if re.search(r'\([^)]+,\s*[^)]+\)', content):
        print("✅ Inline citations found")
    elif re.search(r'References:', content):
        print("✅ References section found")
    else:
        issues.append("⚠️  No clear citation format found")
    
    if issues:
        print("\n⚠️  Issues found:")
        for issue in issues:
            print(f"  {issue}")
        return False
    else:
        print("\n✅ All checks passed!")
        return True

# Test queries
test_queries = [
    "What are the payment terms for small businesses?",
    "What are the WHS requirements for construction contracts?",
    "What are the supplier compliance monitoring requirements?"
]

print("Testing Knowledge Assistant Formatting\n" + "="*50)

for i, query in enumerate(test_queries, 1):
    print(f"\nTest {i}: {query}")
    print("-" * 50)
    test_knowledge_assistant(query)
    print()
```

**Run the test:**
```bash
export DATABRICKS_ENDPOINT_URL="https://your-workspace.databricks.com/serving-endpoints/your-ka-endpoint/invocations"
export DATABRICKS_TOKEN="your-token"

python test_knowledge_assistant.py
```

## Monitoring and Maintenance

### Regular Checks

**Weekly:**
- Spot-check a few responses for formatting quality
- Review any user feedback about citation readability

**Monthly:**
- Test with a comprehensive set of queries
- Review and update system prompt if new issues arise

**After Databricks Updates:**
- Re-test knowledge assistant formatting
- Verify system prompt still applied correctly
- Check for any new configuration options

### Metrics to Track

1. **Response Cleanliness**: % of responses without HTML markup
2. **Citation Quality**: % of responses with properly formatted citations
3. **User Satisfaction**: Feedback on readability
4. **Response Completeness**: Ensure cleaning doesn't reduce accuracy

## Best Practices

1. **Test Before Production**: Always test in a dev/staging environment first
2. **Version Control**: Keep system prompt in version control (Git)
3. **Document Changes**: Note any customizations to the system prompt
4. **Monitor Performance**: Track response times after applying system prompt
5. **Backup Configuration**: Save current configuration before making changes
6. **Gradual Rollout**: If possible, A/B test the new format with users

## FAQ

**Q: Will this slow down the knowledge assistant?**
A: No, system prompts don't significantly impact response time.

**Q: Can I customize the citation format further?**
A: Yes, edit `knowledge_assistant_system_prompt.md` to specify your preferred format.

**Q: What if my Databricks version doesn't support system prompts for Genie?**
A: Use the main agent cleanup approach (suggested_system_prompt.md) as a fallback.

**Q: Can I use this with non-Genie knowledge assistants?**
A: Yes, any LLM-based endpoint that accepts system prompts can use this.

**Q: Will this work with other document types (not just procurement policies)?**
A: Yes, but you may want to adjust the examples and terminology in the system prompt.

## Support and Resources

- **Main System Prompt**: `suggested_system_prompt.md` (for the main agent)
- **Knowledge Assistant Prompt**: `knowledge_assistant_system_prompt.md` (for the KA endpoint)
- **Implementation Guide**: This document
- **Troubleshooting**: `STRUCTURED_OUTPUT_GUIDE.md`
- **Quick Reference**: `QUICK_REFERENCE.md`

## Next Steps

After implementing this system prompt:

1. ✅ Test thoroughly with various query types
2. ✅ Compare responses before/after to validate improvement
3. ✅ Train users on the new citation format (if needed)
4. ✅ Monitor for any edge cases or formatting issues
5. ✅ Document any customizations you make to the prompt
6. ✅ Consider applying the main agent system prompt as well (defense in depth)

---

**Last Updated:** November 10, 2025  
**Version:** 1.0  
**Compatibility:** Databricks Genie, Custom Knowledge Assistant Endpoints

