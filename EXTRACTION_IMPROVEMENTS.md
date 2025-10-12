# Extraction Improvements - Filtering Invalid Data

## Issue Identified

The compliance report was extracting invalid entries like:
- Generic terms (e.g., "compliance", "policy") as supplier names
- Internal agent reasoning and tool responses as risk details
- Unstructured tool output appearing in supplier details

## Root Causes

1. **Tool Responses**: Agent's internal processing (tool calls, searches, reasoning) was being included in extraction
2. **Broad Regex Patterns**: Patterns were too permissive and caught generic terms
3. **No Validation**: Missing checks for valid company names vs. generic terms
4. **No Content Type Filtering**: Tool messages and function call results were processed like regular content

## Solutions Implemented

### 1. Message-Level Filtering

**Skip Tool Responses:**
```python
# Skip tool responses - they contain internal processing
if msg.get("role") == "tool":
    continue

# Skip messages with tool calls
if msg.get("tool_calls"):
    continue
```

**Impact:** Eliminates internal agent processing from extraction entirely.

### 2. Supplier Name Validation

**Invalid Term Filtering:**
```python
invalid_terms = [
    'compliance', 'policy', 'procurement', 'government', 'agency',
    'contract', 'supplier', 'vendor', 'contractor', 'company',
    'risk', 'issue', 'concern', 'violation', 'breach', 'procedure',
    'requirement', 'standard', 'regulation', 'framework', 'process',
    'management', 'monitoring', 'assessment', 'audit', 'review',
    'knowledge', 'assistant', 'question', 'search', 'finding'
]

if supplier_name.lower() in invalid_terms:
    continue
```

**Company Name Validation:**
```python
# Must have at least one capital letter
if not any(c.isupper() for c in supplier_name):
    continue

# Skip if it starts with non-company words
skip_prefixes = ['the question', 'the search', 'knowledge', 'assistant', 'policy', 'procedure']
if any(supplier_name.lower().startswith(prefix) for prefix in skip_prefixes):
    continue
```

**Impact:** Only real company names are extracted.

### 3. Context Filtering

**Skip Internal Reasoning:**
```python
skip_markers = [
    'knowledge-assistant', 'searching', 'verifying', 'possible_sources',
    'tool_calls', 'function_call', 'The search results', 'I will structure',
    'To answer comprehensively', 'The question asks'
]

if any(marker.lower() in context.lower() for marker in skip_markers):
    continue
```

**Length Validation:**
```python
# Skip if context is too long (likely contains tool output)
if len(context) > 1000:
    continue
```

**Impact:** Cleaner, more relevant risk details without internal processing text.

### 4. Action Filtering

**Same Approach for Compliance Actions:**
```python
skip_markers = [
    'knowledge-assistant', 'searching', 'verifying', 'tool_call',
    'function_call', 'search results', 'I will structure', 'possible_sources'
]

if any(marker.lower() in action_text.lower() for marker in skip_markers):
    continue
```

**Impact:** Only actionable compliance steps are extracted.

### 5. Structured Data Validation

**Even Structured JSON Gets Validated:**
```python
# Validate supplier name from structured data
invalid_terms = ['compliance', 'policy', 'procurement', 'government', 'supplier', 'vendor']
if not supplier_name or supplier_name.lower() in invalid_terms:
    continue

if len(supplier_name) < 3 or len(supplier_name) > 100:
    continue
```

**Impact:** Protection against malformed agent output even with structured format.

## Before vs. After

### Before ❌
```
Suppliers at Risk:
1. ✅ Silverbridge Civil Engineering Pty Ltd (Valid)
2. ✅ Pacific Station Solutions Pty Ltd (Valid)
3. ✅ SmartTransit Analytics Pty Ltd (Valid)
4. ❌ compliance (Invalid - generic term)
   - Details contain tool output and internal reasoning
```

### After ✅
```
Suppliers at Risk:
1. ✅ Silverbridge Civil Engineering Pty Ltd
2. ✅ Pacific Station Solutions Pty Ltd
3. ✅ SmartTransit Analytics Pty Ltd
   - Clean details with only relevant risk information
```

## Validation Rules Summary

### Supplier Names Must:
- ✅ Be 3-100 characters long
- ✅ Contain at least one capital letter
- ✅ Not be a generic term (compliance, policy, etc.)
- ✅ Not start with non-company prefixes
- ✅ Come from assistant messages (not tool responses)

### Risk Details Must:
- ✅ Be under 1000 characters
- ✅ Not contain tool response markers
- ✅ Not contain internal reasoning phrases
- ✅ Be relevant to the supplier

### Compliance Actions Must:
- ✅ Be 15-300 characters long
- ✅ Not contain tool response markers
- ✅ Be actionable (not internal processing)
- ✅ Not be duplicates

## Testing the Fix

### Test Case 1: Generic Terms
```python
# These should be filtered out:
"compliance"
"policy"
"procurement"
"supplier"
```

### Test Case 2: Tool Responses
```python
# Messages with role="tool" should be skipped
{
  "role": "tool",
  "content": "Searching... knowledge-assistant..."
}
```

### Test Case 3: Valid Company Names
```python
# These should pass:
"ABC Transport Pty Ltd"
"Silverbridge Civil Engineering Pty Ltd"
"XYZ Logistics & Services"
```

### Test Case 4: Context Validation
```python
# Too long (>1000 chars) - Skip
# Contains "knowledge-assistant" - Skip
# Contains "The question asks" - Skip
# Clean, relevant context (200-500 chars) - Include ✅
```

## Monitoring Recommendations

### Log Warning Signs:
```python
# Add logging for filtered items (optional)
if supplier_name.lower() in invalid_terms:
    logger.debug(f"Filtered invalid supplier term: {supplier_name}")
```

### Metrics to Track:
- Number of suppliers extracted per report
- Percentage of filtered vs. included suppliers
- Average context length
- Number of actions extracted

### Quality Checks:
1. All supplier names should be proper company names
2. Risk details should be concise and relevant
3. No internal reasoning text should appear
4. No tool response markers should be visible

## Future Improvements

### 1. Company Name Recognition
Use NLP or entity recognition to better identify company names:
```python
from spacy import load
nlp = load("en_core_web_sm")
# Extract ORGANIZATION entities
```

### 2. Confidence Scoring
Add confidence scores based on:
- Pattern match quality
- Context relevance
- Name structure validation

### 3. User Feedback Loop
Allow users to mark false positives:
```python
# Add "Report Issue" button per supplier
# Track patterns that lead to false positives
# Update filters based on feedback
```

### 4. Allowlist/Blocklist
Maintain lists of:
- Known valid suppliers (auto-approve)
- Known invalid terms (auto-reject)
- User-specific customization

### 5. Advanced Pattern Matching
```python
# Company name patterns
company_suffixes = ["Pty Ltd", "Ltd", "Inc", "Corp", "LLC", "GmbH"]
company_patterns = [
    r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:" + "|".join(company_suffixes) + ")"
]
```

## Configuration Options

### Adjust Sensitivity
Modify in `app.py`:

```python
# More strict (fewer false positives)
MIN_SUPPLIER_NAME_LENGTH = 5
MAX_CONTEXT_LENGTH = 500
invalid_terms.extend(['additional', 'terms'])

# More permissive (catch more suppliers)
MIN_SUPPLIER_NAME_LENGTH = 3
MAX_CONTEXT_LENGTH = 1500
invalid_terms = ['compliance', 'policy']  # Minimal list
```

### Environment-Specific Filters
```python
# For different industries
if industry == "transport":
    invalid_terms.extend(['transport', 'railway'])
elif industry == "healthcare":
    invalid_terms.extend(['hospital', 'clinic'])
```

## Troubleshooting

### Issue: Valid suppliers being filtered
**Solution:** Check if name matches invalid_terms or skip_prefixes

### Issue: Still seeing tool responses
**Solution:** Add more markers to skip_markers list

### Issue: Missing suppliers
**Solution:** Ensure structured JSON format is used for 100% accuracy

### Issue: Empty report
**Solution:** Verify messages have role="assistant" and content is not empty

## Summary

The improved extraction system now:
- ✅ Filters out tool responses and internal reasoning
- ✅ Validates supplier names are real companies
- ✅ Removes generic terms
- ✅ Limits context to relevant information
- ✅ Prevents duplicate entries
- ✅ Maintains backward compatibility
- ✅ Works with both structured and unstructured data

**Result:** Clean, accurate compliance reports with only valid supplier data! 🎉

---

**Version:** 1.1  
**Last Updated:** October 2025  
**Related Files:** `app.py`, `suggested_system_prompt.md`

