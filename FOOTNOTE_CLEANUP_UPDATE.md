# Footnote Cleanup Update

## Overview

This update fixes the issue of excessive, poorly formatted footnotes in knowledge assistant tool responses. The system prompt has been updated to instruct the agent to clean up and reformat citations from knowledge assistant tools before presenting them to users.

## Problem Description

When using knowledge assistant tools (like `nsw-procurement-policy-ka`), responses included:
- ❌ Verbose footnotes with raw HTML table markup
- ❌ Duplicate citation content repeated multiple times
- ❌ Internal Databricks file system URLs
- ❌ Poorly formatted reference sections spanning hundreds of lines
- ❌ Visible `<think>` tags showing internal reasoning

**Example of the problem:**
```
You must monitor compliance.1

Footnotes
1. <table><tr><th>Relating to</th><th>Status</th><th>Category</th>...[200+ lines of HTML]...</table> ↩
```

## Solution

Updated the system prompt to include explicit instructions for cleaning up knowledge assistant responses.

### Files Modified

1. **`suggested_system_prompt.md`** - Main system prompt file
   - Added section: "Handling Knowledge Assistant Tool Responses"
   - Added concrete before/after examples
   - Updated example response to show proper citation format
   - Added note in "Important Notes" section

2. **`STRUCTURED_OUTPUT_GUIDE.md`** - Implementation guide
   - Added section: "Knowledge Assistant Citation Cleanup"
   - Added troubleshooting entry for excessive footnotes
   - Updated testing checklist with citation cleanup tests

3. **`QUICK_REFERENCE.md`** - Quick reference guide
   - Added section: "Citation Formatting (Knowledge Assistant Responses)"
   - Included example transformations
   - Updated dos and don'ts lists

## Key Instructions Added to System Prompt

### What the Agent Will Now Do:

✅ Remove `<think>` tags and internal reasoning  
✅ Remove raw HTML markup from footnotes  
✅ Convert verbose citations to clean inline references  
✅ Deduplicate repeated citations  
✅ Present information in a readable format  

### Formatting Guidelines:

**Clean inline citations:**
```
(NSW Procurement Policy Framework, Section 2.03)
```

**Simple References section:**
```
**References:**
- NSW Procurement Policy Framework December 2024, Section 2.03
- Supplier Due Diligence: A Guide for NSW Public Sector Agencies
```

## Expected Transformation

### Before (Raw Tool Output):
```
<think>Searching NSW Procurement Policy...</think>

You must monitor, on an ongoing basis, supplier compliance with 
contractual, regulatory and other obligations.1

Footnotes
1. Section 2 03 Manage Contract and supplier management 
<table><tr><th>Relating to</th><th>Status</th><th>Category</th>
<th>Value</th><th>Obligation</th><th>Reference</th></tr>
<tr><td rowspan="3">Supplier due diligence</td><td></td><td></td>
<td>Any</td><td>You should monitor, on an ongoing basis, supplier 
compliance with contractual, regulatory and other obligations. 
The level and frequency of checks will vary depending on the 
value and risk profile of the contract.</td>
<td>Supplier Due Diligence: A Guide for NSW Public Sector 
Agencies</td></tr>...</table> 
Procurement-Policy-Framework_December-2024.pdf ↩
```

### After (Cleaned Agent Response):
```
Based on the NSW Procurement Policy Framework, agencies must 
monitor supplier compliance with contractual, regulatory and 
other obligations on an ongoing basis. The level and frequency 
of checks will vary depending on the value and risk profile of 
the contract (Supplier Due Diligence: A Guide for NSW Public 
Sector Agencies, December 2024).
```

## Implementation Steps

### 1. Update System Prompt in Your Agent

**For Databricks Agent:**
1. Go to your Agent/Model Serving configuration
2. Navigate to the System Prompt section
3. Replace with the updated content from `suggested_system_prompt.md`
4. Save and redeploy the agent

**For MLflow Model:**
```python
import mlflow

# Read the updated system prompt
with open('suggested_system_prompt.md', 'r') as f:
    system_prompt = f.read()

# Log the model with updated prompt
mlflow.langchain.log_model(
    lc_model=your_agent,
    artifact_path="agent",
    registered_model_name="transport-compliance-agent",
    metadata={"system_prompt": system_prompt}
)
```

### 2. Test the Changes

Run a test query that uses the knowledge assistant tool:

**Test Query:**
```
What are the NSW procurement policy requirements for ensuring 
supplier compliance when suppliers have performance issues or 
payment disputes?
```

**Expected Result:**
- ✅ Clean, readable response with inline citations
- ✅ No HTML markup visible
- ✅ No duplicate citations
- ✅ No `<think>` tags
- ✅ Simple References section (if present)

**Failure Indicators:**
- ❌ Raw `<table>`, `<tr>`, `<td>` tags visible
- ❌ Repeated footnote content
- ❌ Internal file URLs displayed
- ❌ `<think>` tags in response

### 3. Validation Checklist

- [ ] Updated system prompt deployed to agent
- [ ] Test query returns clean citations
- [ ] No HTML markup in responses
- [ ] No duplicate footnotes
- [ ] References section formatted cleanly
- [ ] Agent still provides accurate policy information
- [ ] Structured data extraction still working

## Benefits

### Before:
- 😞 Users see hundreds of lines of HTML markup
- 😞 Duplicate citations repeated 5-10 times
- 😞 Internal system paths exposed
- 😞 Response is difficult to read and unprofessional
- 😞 Takes up excessive screen space

### After:
- ✅ Clean, professional responses
- ✅ Clear inline citations
- ✅ Deduplicated references
- ✅ Easy to read and understand
- ✅ Maintains citation accuracy
- ✅ Compact, scannable format

## Technical Details

### How It Works

1. **Agent receives tool response** from knowledge assistant with verbose footnotes
2. **System prompt instructions trigger** citation cleanup process
3. **Agent extracts key information** and removes HTML/duplicates
4. **Agent reformats citations** into clean inline or reference format
5. **Agent presents cleaned response** to user

### No Code Changes Required

This is a **prompt-only update**. No changes to:
- Python code
- Streamlit app
- Tool configurations
- API endpoints
- Extraction logic

The agent handles the cleanup automatically based on the system prompt instructions.

## Troubleshooting

### Issue: Agent still showing HTML markup

**Possible Causes:**
1. System prompt not deployed correctly
2. Agent not following instructions
3. Caching issues

**Solutions:**
- Verify system prompt is updated in agent configuration
- Clear any cached responses
- Test with a fresh agent session
- Check agent logs for prompt compliance

### Issue: Citations missing entirely

**Possible Causes:**
1. Agent removing too much content
2. Overly aggressive cleanup

**Solutions:**
- Review agent's response - main policy content should still be present
- Citations should be converted to inline format, not removed
- Check that References section is included when needed

### Issue: Some HTML still visible

**Possible Causes:**
1. Agent not catching all HTML tags
2. Unusual formatting in tool response

**Solutions:**
- Report specific cases for system prompt refinement
- May need to add post-processing rules for edge cases

## Rollback Instructions

If you need to revert these changes:

1. Use a previous version of `suggested_system_prompt.md`
2. Redeploy agent with old system prompt
3. Test to confirm old behavior

**Note:** This should not be necessary as the changes are improvements only.

## Testing Examples

### Test Case 1: Policy Query
**Query:** "What are the payment requirements for small businesses under NSW procurement policy?"

**Expected:** Clean response with inline citation like:
```
In-scope agencies must pay registered small businesses (<20 FTEs) 
within 5 business days of receipt of a correctly rendered invoice 
(NSW Procurement Policy Framework, Faster Payment Terms Policy).
```

### Test Case 2: Compliance Requirements
**Query:** "What WHS monitoring is required for construction contracts?"

**Expected:** Clean response with References section:
```
For construction contracts, you must review contractors' WHS 
performance throughout the life of the contract, including WHS 
management monthly reports and investigating any Notifiable WHS 
incidents.

**References:**
- WHS Management Guidelines
- NSW Procurement Policy Framework, Section 2.03
```

### Test Case 3: Multi-Requirement Query
**Query:** "What are all the supplier conduct requirements?"

**Expected:** Clean summary with deduplicated citations, NO repeated HTML tables.

## Future Enhancements

Potential improvements to consider:
1. Automated citation style selection (inline vs. footnote vs. references)
2. Smart citation grouping for related sources
3. Hyperlinks to source documents where available
4. Citation export for reference management tools

## Support

For questions or issues:
1. Review this document
2. Check `STRUCTURED_OUTPUT_GUIDE.md` troubleshooting section
3. Test with provided example queries
4. Verify system prompt is correctly configured

---

**Last Updated:** November 10, 2025  
**Version:** 1.0  
**Impact:** System Prompt Only - No Code Changes Required

