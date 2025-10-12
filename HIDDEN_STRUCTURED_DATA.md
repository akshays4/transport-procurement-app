# Hidden Structured Data Feature

## Overview

The application now automatically hides structured JSON data from the chat display while preserving it for backend extraction. This provides a clean user experience while maintaining full functionality.

## How It Works

### Chat Display (What Users See)

When the agent responds with structured data, users see:

```
Based on recent news searches, ABC Transport Services has been mentioned 
in several articles regarding delays in project delivery for government 
contracts in Queensland...

[Natural language response continues...]

📋 Compliance data captured for reporting
```

✅ Clean, professional appearance  
✅ No confusing JSON  
✅ Subtle indicator of data capture  

### Backend Storage (What System Uses)

The full message including structured data is preserved:

```
Based on recent news searches, ABC Transport Services has been mentioned 
in several articles regarding delays in project delivery...

---STRUCTURED_DATA---
{
  "suppliers_at_risk": [
    {
      "supplier_name": "ABC Transport Services",
      "risk_type": "Operational Risk",
      "severity": "Medium",
      "summary": "Multiple reported delays in government contract delivery",
      "evidence": "News articles from Queensland government contracts (2024)"
    }
  ],
  "compliance_actions": [...]
}
---END_STRUCTURED_DATA---
```

✅ Full data preserved  
✅ Extraction works perfectly  
✅ No data loss  

## Implementation Details

### Location
- **File:** `messages.py`
- **Functions:**
  - `strip_structured_data()` - Removes JSON for display
  - `render_message()` - Shows cleaned content

### Logic Flow

```python
1. Agent responds with natural text + structured JSON
   ↓
2. Message stored in session history (full content with JSON)
   ↓
3. Display layer calls strip_structured_data()
   ↓
4. User sees clean response + indicator
   ↓
5. Compliance Report extracts from original full content
```

### The Strip Function

```python
def strip_structured_data(content):
    """Remove structured data markers and JSON from content for display."""
    # Remove entire structured data section
    pattern = r'\s*---STRUCTURED_DATA---.*?---END_STRUCTURED_DATA---\s*'
    cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Clean up extra whitespace
    cleaned_content = re.sub(r'\n{3,}', '\n\n', cleaned_content)
    return cleaned_content.strip()
```

### The Display Enhancement

```python
def render_message(msg):
    if msg["role"] == "assistant":
        # Check if structured data exists
        has_structured_data = "---STRUCTURED_DATA---" in msg["content"]
        
        # Strip for display
        display_content = strip_structured_data(msg["content"])
        st.markdown(display_content)
        
        # Show indicator
        if has_structured_data:
            st.caption("📋 Compliance data captured for reporting")
```

## Benefits

### For End Users
- ✅ **Clean Interface**: No technical JSON clutter
- ✅ **Professional Look**: Natural conversation flow
- ✅ **Confidence**: Indicator confirms data was captured
- ✅ **Better UX**: Focus on insights, not format

### For System
- ✅ **Full Data Preservation**: No information loss
- ✅ **Extraction Works**: Original content intact
- ✅ **Backward Compatible**: Existing extraction unchanged
- ✅ **Dual Purpose**: One response, two views

### For Developers
- ✅ **Simple Implementation**: Clean separation of concerns
- ✅ **Easy Maintenance**: Single regex pattern
- ✅ **Testable**: Display logic independent
- ✅ **Extensible**: Easy to modify indicator

## User Experience Flow

### Conversation Example

**User:** "Check ABC Transport for risks"

**Agent Display:**
```
I've analyzed ABC Transport Services. Based on recent news and financial 
reports, I've identified the following concerns:

1. Financial Stability: Debt-to-equity ratio increased 40% year-over-year
2. Operational Issues: Multiple delivery delays reported in similar contracts

I recommend conducting a financial audit and verifying current capacity.

📋 Compliance data captured for reporting
```

**Behind the Scenes:**
- Full structured data stored in session
- Available for Compliance Report page
- Can be exported as JSON or text

**User Action:**
1. Continues conversation naturally
2. Clicks "Compliance Report" in sidebar when ready
3. Sees fully structured data with all details

## Customization Options

### Change the Indicator

In `messages.py`, modify:
```python
st.caption("📋 Compliance data captured for reporting")
```

**Options:**
- `"✅ Data saved for report"`
- `"📊 Structured data available"`
- `"💾 Compliance info captured"`
- Or hide completely by removing this line

### Add More Details

Show quick preview without full JSON:
```python
if has_structured_data:
    # Extract counts
    suppliers_count = content.count('"supplier_name":')
    actions_count = content.count('"action":')
    st.caption(f"📋 Captured {suppliers_count} suppliers and {actions_count} actions")
```

### Optional Expander

Let users peek at structured data if curious:
```python
if has_structured_data:
    st.caption("📋 Compliance data captured")
    with st.expander("🔍 View structured data"):
        # Extract and display JSON
        import json
        match = re.search(r'---STRUCTURED_DATA---\s*(\{.*?\})\s*---END', 
                         msg["content"], re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                st.json(data)
            except:
                st.text("Unable to parse structured data")
```

## Testing

### Test Case 1: Structured Data Present
```python
content = """
Natural response here.

---STRUCTURED_DATA---
{"suppliers_at_risk": [...]}
---END_STRUCTURED_DATA---
"""

display = strip_structured_data(content)
assert "STRUCTURED_DATA" not in display
assert "Natural response here" in display
```

### Test Case 2: No Structured Data
```python
content = "Just a normal response"
display = strip_structured_data(content)
assert display == "Just a normal response"
```

### Test Case 3: Extraction Still Works
```python
# Full content stored in history
full_content = st.session_state.history[-1].messages[0]["content"]
assert "---STRUCTURED_DATA---" in full_content

# Display content is clean
# But extraction function still accesses full_content
```

## Troubleshooting

### Issue: Indicator not showing
**Cause:** Structured data markers not exact  
**Fix:** Verify `---STRUCTURED_DATA---` format exactly

### Issue: Data not extracting
**Cause:** Original message being modified  
**Fix:** Ensure stripping only happens in `render_message()`, not storage

### Issue: Extra whitespace in display
**Cause:** Regex cleanup not sufficient  
**Fix:** Adjust the `\n{3,}` pattern to be more aggressive

### Issue: Want to hide indicator too
**Solution:** Comment out the caption line:
```python
# if has_structured_data:
#     st.caption("📋 Compliance data captured for reporting")
```

## Best Practices

### 1. Keep Extraction Independent
```python
# ❌ DON'T strip before storing
content = strip_structured_data(agent_response)
store_message(content)

# ✅ DO strip only for display
store_message(agent_response)  # Full content
display(strip_structured_data(agent_response))  # Clean display
```

### 2. Test Both Views
- Test chat display (should be clean)
- Test report extraction (should have full data)
- Test with and without structured data

### 3. Document for Users
Include in user guide:
- What the indicator means
- Where to find the structured report
- That no data is lost

### 4. Monitor Performance
- Regex is fast but watch for very long messages
- Consider caching stripped content if performance issue
- Profile if handling 100+ messages

## Future Enhancements

### 1. Collapsible Indicator
```python
with st.expander("📋 Compliance data captured (click to preview)"):
    st.info(f"Found {supplier_count} suppliers at risk")
    st.info(f"Identified {action_count} compliance actions")
```

### 2. Real-time Preview
Show small cards inline:
```python
if has_structured_data and supplier_count > 0:
    st.info(f"⚠️ {supplier_count} suppliers flagged for review")
```

### 3. Direct Links
```python
st.caption("📋 [View full compliance report](#) | Data captured")
# Link to report page
```

### 4. Animation
```python
if has_structured_data:
    st.success("✅ Compliance data captured!")
    # With animation or success message
```

## Summary

The hidden structured data feature provides the best of both worlds:

- **Users** get a clean, professional chat experience
- **System** gets structured, extractable data
- **Developers** get simple, maintainable code

No compromises, just better UX! 🎉

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Files Modified:** `messages.py`, `suggested_system_prompt.md`

