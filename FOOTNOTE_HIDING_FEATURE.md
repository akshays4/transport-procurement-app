# Footnote Hiding Feature - Documentation

## 🎯 Overview

This feature automatically detects and hides verbose footnotes from knowledge assistant tool responses in the main chat, displaying them instead in an expandable "View detailed source references" section.

## ✨ What It Does

### For Users:

**Before (Without Feature):**
```
Main response content here...

Footnotes
1. <table><tr><th>Status</th><th>Category</th>...[500+ lines of HTML]...
2. Contract and supplier management <table>...[more HTML]...
[Continues for hundreds of lines]
```
😱 **Result:** Chat is cluttered, hard to read, unprofessional

**After (With Feature):**
```
Main response content here...

📚 View detailed source references ▼  (collapsed by default)
```
😊 **Result:** Clean chat, references available on-demand

### For Developers:

- ✅ Automatically detects verbose footnotes
- ✅ Removes HTML markup and special characters
- ✅ Hides footnotes in expandable section
- ✅ Preserves original messages for data extraction
- ✅ Works with both assistant and tool responses

## 🔧 Implementation Details

### Key Functions (in `messages.py`)

#### 1. `extract_and_hide_footnotes(content)`

Detects and extracts verbose footnotes from content.

**What it detects:**
- Sections starting with "Footnotes" or "References"
- Content containing HTML table markup
- Numbered footnotes with superscript-like markers
- `<think>` tags (also removed)

**Returns:**
- `cleaned_content`: Main content without footnotes
- `footnotes_text`: Extracted footnote section (or None)

**Example:**
```python
content = """
Policy requirement here.

Footnotes
1. <table><tr>...[verbose HTML]...</table>
"""

cleaned, footnotes = extract_and_hide_footnotes(content)
# cleaned = "Policy requirement here."
# footnotes = "Footnotes\n1. <table>...[content]..."
```

#### 2. `clean_html_and_special_chars(content)`

Removes HTML tags and cleans up special characters.

**What it cleans:**
- HTML tags: `<table>`, `<tr>`, `<td>`, `<th>`, `<tbody>`, etc.
- Any other HTML tags
- HTML entities (unescapes them)
- Extra whitespace

**Example:**
```python
content = "<table><tr><td>Value</td></tr></table> Text with  extra  spaces"
cleaned = clean_html_and_special_chars(content)
# cleaned = "Text with extra spaces"
```

#### 3. `render_message(msg)` - Updated

Enhanced to automatically:
1. Strip structured data (existing)
2. Extract and hide footnotes (new)
3. Clean HTML and special characters (new)
4. Show footnotes in expander if verbose (new)

**Logic:**
```python
if footnotes and (len(footnotes) > 200 or '<table>' in footnotes):
    # Show in expander
    with st.expander("📚 View detailed source references"):
        st.caption("*Detailed citations and source information*")
        st.text(cleaned_footnotes[:2000])  # Truncate if very long
```

## 📋 How It Works

### Processing Flow

```
Agent/Tool Response
       ↓
Strip Structured Data (for compliance extraction)
       ↓
Extract Footnotes (if verbose)
       ↓
Clean HTML & Special Characters
       ↓
Display Main Content
       ↓
Show Footnotes in Expander (if detected & verbose)
```

### Detection Criteria

Footnotes are hidden in an expander if:
- Length > 200 characters, OR
- Contains HTML table markup (`<table>`)

**Why these criteria?**
- Short, clean footnotes can stay in main chat
- Long, verbose, or HTML-laden footnotes are hidden

### Truncation

Footnotes are truncated to 2000 characters in the expander with a notice:
```
"Source references truncated for readability"
```

**Why truncate?**
- Even in expander, extremely long footnotes hurt UX
- Most useful information is in first ~2000 chars
- Users can still see the pattern and key references

## 🎨 User Experience

### Main Chat

**Always Shows:**
- Main response content
- Clean citations (inline or simple references)
- Structured data indicator (if present)

**Never Shows in Main Chat:**
- Verbose HTML footnotes
- Raw `<table>` markup
- `<think>` tags
- Duplicate citation content

### Expandable Section

**When Shown:**
- When footnotes are detected AND verbose (>200 chars or HTML)

**Label:**
- "📚 View detailed source references"

**Default State:**
- Collapsed (user must click to expand)

**Content:**
- Cleaned footnotes (HTML removed)
- Truncated to 2000 chars if needed
- Caption: "Detailed citations and source information"

## 🧪 Testing

### Test Case 1: Normal Response (No Footnotes)

**Input:**
```
This is a policy requirement (Source Name, Section 2.03).
```

**Expected Output:**
- Main content displayed normally
- No expander shown
- ✅ Pass

### Test Case 2: Response with Clean References

**Input:**
```
Policy requirement here.

**References:**
- NSW Procurement Policy Framework
- Supplier Due Diligence Guide
```

**Expected Output:**
- Full content displayed in main chat
- No expander (references are clean and short)
- ✅ Pass

### Test Case 3: Response with Verbose HTML Footnotes

**Input:**
```
Policy requirement here.¹

Footnotes
¹ <table><tr><th>Status</th>...[500 lines of HTML]...</table>
```

**Expected Output:**
- Main content: "Policy requirement here."
- Expander shown: "📚 View detailed source references"
- Expander contains cleaned footnote text
- No HTML visible in main chat
- ✅ Pass

### Test Case 4: Tool Response with HTML

**Input (from tool):**
```json
{
  "response": "Requirement text <table>...[HTML content]...</table>"
}
```

**Expected Output:**
- Tool response cleaned
- HTML removed
- If very verbose, truncated
- ✅ Pass

## 🔧 Configuration Options

### Adjusting Truncation Limit

In `render_message()`, find:
```python
st.text(cleaned_footnotes[:2000])  # Limit to 2000 chars
```

Change `2000` to your preferred limit.

### Adjusting Verbosity Threshold

In `render_message()`, find:
```python
if footnotes and (len(footnotes) > 200 or '<table>' in footnotes.lower()):
```

Change `200` to your preferred threshold.

### Changing Expander Label

In `render_message()`, find:
```python
with st.expander("📚 View detailed source references", expanded=False):
```

Change the label text as needed.

### Expander Default State

To show expanded by default:
```python
with st.expander("📚 View detailed source references", expanded=True):
```

## 🎯 Benefits

### For End Users

- ✅ **Cleaner chat interface** - No clutter from verbose footnotes
- ✅ **Better readability** - Focus on main content
- ✅ **Optional details** - Can expand to see sources if needed
- ✅ **Professional appearance** - No raw HTML or markup visible
- ✅ **Faster scanning** - Easier to find important information

### For Developers

- ✅ **Automatic cleaning** - No manual intervention needed
- ✅ **Safety layer** - Catches HTML that slips through system prompts
- ✅ **Original data preserved** - Messages unchanged for extraction
- ✅ **Flexible configuration** - Easy to adjust thresholds
- ✅ **Works everywhere** - Applied to all message rendering

### For Organizations

- ✅ **Better UX** - Users more likely to engage with clean interface
- ✅ **Professional image** - No technical clutter visible
- ✅ **Reduced confusion** - Users focus on policy content, not formatting
- ✅ **Compliance maintained** - Full references still available

## 🔄 Integration with Other Features

### Structured Data Extraction

This feature works alongside structured data extraction:

1. **Strip structured data** (hidden from display, kept for extraction)
2. **Extract footnotes** (hidden in expander)
3. **Clean HTML** (removed from display)

All original message content is preserved in `msg["content"]` for:
- Compliance report extraction
- Data analysis
- Audit trails

### System Prompts

This feature provides **defense in depth** with system prompts:

**Layer 1:** Knowledge assistant system prompt
- Tries to prevent HTML from being generated

**Layer 2:** Main agent system prompt
- Instructs agent to clean up citations

**Layer 3:** This message handling feature (MOST RELIABLE)
- Guarantees clean display even if layers 1&2 fail
- Always catches HTML markup
- Always hides verbose footnotes

## 📊 Monitoring

### What to Monitor

1. **Footnote detection rate**
   - How often are footnotes detected and hidden?
   - Are legitimate content sections being incorrectly classified as footnotes?

2. **HTML cleaning effectiveness**
   - Are any HTML tags still visible?
   - Are any special characters causing issues?

3. **User engagement with expanders**
   - Are users clicking to view detailed references?
   - Should default state be changed?

4. **Performance impact**
   - Any slowdown from regex processing?
   - Any issues with very long messages?

### Metrics to Track

```python
# Example tracking (add to your monitoring)
footnotes_hidden_count = 0
html_cleaned_count = 0
avg_footnote_length = 0
user_expander_clicks = 0
```

## 🐛 Troubleshooting

### Issue: Legitimate content hidden in expander

**Symptoms:**
- Important policy text hidden
- Content incorrectly classified as footnote

**Solution:**
- Review `footnote_patterns` in `extract_and_hide_footnotes()`
- Make patterns more specific
- Adjust to only match "Footnotes" heading + HTML tables

### Issue: HTML still visible in chat

**Symptoms:**
- Tags like `<table>` still showing
- Raw HTML in response

**Solution:**
- Check if new HTML tag types need to be added to `clean_html_and_special_chars()`
- Verify function is being called in render path
- Check for edge cases in HTML structure

### Issue: Footnotes not being detected

**Symptoms:**
- Verbose footnotes still in main chat
- No expander shown

**Solution:**
- Check if footnote format matches patterns in `extract_and_hide_footnotes()`
- Add new patterns for different formats
- Lower verbosity threshold if needed

### Issue: Performance problems

**Symptoms:**
- Slow message rendering
- UI lag when displaying responses

**Solution:**
- Profile the regex operations
- Consider caching cleaned content
- Limit maximum message length processed
- Optimize regex patterns

## 📝 Future Enhancements

Potential improvements to consider:

1. **Smart Reference Extraction**
   - Parse references into structured format
   - Link to source documents
   - Group by document type

2. **Reference Search**
   - Allow searching within references
   - Filter by document name
   - Find specific sections

3. **Citation Formatting Options**
   - User preference for citation style
   - Toggle between inline and footnote display
   - Export references in different formats

4. **Reference Validation**
   - Check if referenced documents exist
   - Verify section numbers are valid
   - Flag broken references

5. **Analytics**
   - Track which references users view most
   - Identify most-cited policies
   - User engagement with expanders

## 🎓 Best Practices

### For Developers

1. **Test with Real Data**
   - Use actual knowledge assistant responses
   - Test with various formats and lengths
   - Check edge cases (very long, no footnotes, etc.)

2. **Monitor Performance**
   - Profile regex operations
   - Check impact on render times
   - Optimize if needed

3. **Keep Patterns Updated**
   - Review new footnote formats from KA
   - Update regex patterns as needed
   - Document any changes

### For Product Teams

1. **User Testing**
   - Get feedback on expander UX
   - Test with different user types
   - Adjust based on usage patterns

2. **Documentation**
   - Show users how to access references
   - Explain what's in the expander
   - Provide examples

3. **Iteration**
   - Monitor user engagement
   - Adjust thresholds based on feedback
   - Refine what gets hidden vs shown

## 📞 Support

### Quick Reference

| Question | Answer |
|----------|--------|
| **Where is footnote hiding implemented?** | `messages.py` → `render_message()` |
| **How to disable feature?** | Comment out footnote extraction and expander code |
| **How to adjust threshold?** | Change `len(footnotes) > 200` to different value |
| **How to change expander label?** | Edit text in `st.expander()` call |
| **Original data preserved?** | Yes, in `msg["content"]` unchanged |

### Getting Help

1. Review this documentation
2. Check `messages.py` implementation
3. Test with example responses
4. Review troubleshooting section above

---

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Status:** Production Ready ✅  
**Impact:** Display Only - Original Messages Unchanged

