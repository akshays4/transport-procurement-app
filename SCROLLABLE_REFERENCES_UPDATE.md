# Scrollable References Update

## 🎉 Enhancement: Scrollable Reference Sections

The "View detailed source references" section is now **scrollable** instead of truncated!

## What Changed

### ✅ Before (Truncated)
- Footnotes were cut off at 2000 characters
- Users couldn't see all references
- Important information might be hidden

### ✅ After (Scrollable)
- Full references displayed in a scrollable container
- Max height: 400px for main references
- Smooth scrolling with scrollbar
- All content accessible
- Character count shown for long references

## Visual Changes

### New Scrollable Container

**Styled box with:**
- Light gray background (`#f8f9fa`)
- Subtle border
- Monospace font (easier to read)
- 400px max height (for main references)
- 300px max height (for tool responses)
- Automatic scrollbar when content exceeds height
- Word wrapping for long lines

### User Experience

**What users see:**
```
📚 View detailed source references ▼

Detailed citations and source information

┌─────────────────────────────────────────┐
│ Reference 1: NSW Procurement Policy    │
│ Framework December 2024, Section 2.03  │
│                                         │
│ Reference 2: Supplier Due Diligence:   │
│ A Guide for NSW Public Sector Agencies │
│                                         │
│ [Scrollable content continues...]      ║ ← Scrollbar
│                                         ║
└─────────────────────────────────────────┘

2,543 characters • Scroll to view all references
```

## Technical Details

### Scrollable Container Implementation

```html
<div style="max-height: 400px; overflow-y: auto; 
            padding: 10px; background-color: #f8f9fa; 
            border-radius: 5px; border: 1px solid #dee2e6; 
            font-family: monospace; font-size: 12px;">
    <pre>[Content here]</pre>
</div>
```

### Security

- All content is **HTML-escaped** before display
- Prevents XSS injection attacks
- Uses Python's `html.escape()` function
- Safe to display user-generated or tool-generated content

### Heights

| Section | Max Height | Reason |
|---------|------------|--------|
| **Main assistant references** | 400px | More important, users likely to read |
| **Tool response content** | 300px | Less critical, more technical |
| **Tool response references** | 300px | Secondary information |

## Benefits

### For Users

- ✅ **See all references** - Nothing is truncated
- ✅ **Easy navigation** - Smooth scrolling
- ✅ **Better readability** - Monospace font, good line height
- ✅ **Space efficient** - Doesn't take up entire screen
- ✅ **Visual cue** - Character count shows there's more to scroll

### For Content

- ✅ **Preserves all information** - No data loss
- ✅ **Maintains formatting** - Line breaks preserved
- ✅ **Handles long content** - Thousands of characters OK
- ✅ **Responsive** - Works on different screen sizes

## Configuration

### Adjust Max Height

In `messages.py`, find the scrollable container and change `max-height`:

```python
# For main references (currently 400px)
<div style="max-height: 400px; ...">

# For tool responses (currently 300px)
<div style="max-height: 300px; ...">
```

**Recommendations:**
- **400-500px** for main references (most readable)
- **300-400px** for tool responses (secondary content)
- **Smaller screens:** Consider responsive design with media queries

### Change Styling

You can customize the appearance by modifying the inline styles:

```python
background-color: #f8f9fa  # Light gray background
border: 1px solid #dee2e6  # Subtle border
border-radius: 5px         # Rounded corners
padding: 10px              # Inner spacing
font-family: monospace     # Font type
font-size: 12px           # Font size
line-height: 1.5          # Line spacing
```

### Character Count Threshold

The character count caption appears when content > 1000 characters:

```python
if len(cleaned_footnotes) > 1000:
    st.caption(f"*{len(cleaned_footnotes):,} characters • Scroll to view all references*")
```

Change `1000` to adjust when the caption appears.

## User Instructions

### How to Use Scrollable References

1. **Expand the section**
   - Click "📚 View detailed source references"

2. **Scroll through content**
   - Use mouse wheel
   - Drag scrollbar on the right
   - Use arrow keys (if focused)
   - Use trackpad gestures

3. **Read comfortably**
   - Content is formatted for readability
   - Line breaks preserved
   - No horizontal scrolling needed (text wraps)

4. **Check length**
   - Look at character count at bottom
   - Indicates how much content is available

## Examples

### Example 1: Short References (No Scroll)

If references are < 400px height, no scrollbar appears:

```
📚 View detailed source references ▼

Detailed citations and source information

Reference 1: NSW Procurement Policy Framework
Reference 2: Supplier Due Diligence Guide

[All visible, no scrollbar needed]
```

### Example 2: Long References (Scrollable)

If references exceed 400px, scrollbar appears:

```
📚 View detailed source references ▼

Detailed citations and source information

┌─────────────────────────────────────────┐
│ Reference 1: NSW Procurement Policy... │
│ [Many more references...]              ║ ← Scrollbar
│                                         ║
└─────────────────────────────────────────┘

3,245 characters • Scroll to view all references
```

### Example 3: Tool Response with References

```
🧰 Tool Response:

┌─────────────────────────────────────────┐
│ Main tool response content here...     │
│ [Scrollable if long]                   ║
└─────────────────────────────────────────┘

📚 View source references ▼

┌─────────────────────────────────────────┐
│ Detailed source references...           │
│ [Also scrollable]                       ║
└─────────────────────────────────────────┘
```

## Accessibility

### Keyboard Navigation

- **Tab**: Focus on scrollable area
- **Arrow Keys**: Scroll up/down
- **Page Up/Down**: Scroll by page
- **Home/End**: Jump to top/bottom

### Screen Readers

- Content is in semantic HTML (`<pre>` tag)
- Screen readers can navigate line by line
- All content is accessible

### Browser Compatibility

Works in all modern browsers:
- ✅ Chrome
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Mobile browsers

## Performance

### No Performance Impact

- CSS-based scrolling (hardware accelerated)
- No JavaScript required
- No impact on render time
- Works smoothly with thousands of characters

### Memory Efficient

- Only visible content is rendered
- Browser handles scrolling efficiently
- No virtual scrolling needed for typical use

## Comparison: Truncation vs Scrolling

| Aspect | Truncation (Old) | Scrolling (New) |
|--------|-----------------|-----------------|
| **Content Access** | ❌ Lost after 2000 chars | ✅ Full access |
| **User Experience** | ❌ Frustrating | ✅ Intuitive |
| **Space Usage** | ✅ Fixed | ✅ Fixed (with scroll) |
| **Readability** | ⚠️ Good until cutoff | ✅ Excellent |
| **Performance** | ✅ Fast | ✅ Fast |
| **Flexibility** | ❌ Limited | ✅ Full control |

## Future Enhancements

Potential improvements:

1. **Search within references**
   - Add search box to filter references
   - Highlight matches

2. **Copy button**
   - One-click copy of all references
   - Copy individual references

3. **Export references**
   - Download as text file
   - Export to citation manager

4. **Collapsible sections**
   - Expand/collapse individual references
   - Group by document type

5. **Sticky headers**
   - Keep section headers visible while scrolling
   - Better navigation

## Testing

### Test Cases

**Test 1: Short content**
- Content < 400px height
- Should not show scrollbar
- Should display fully

**Test 2: Long content**
- Content > 400px height
- Should show scrollbar
- Should be scrollable
- Should show character count

**Test 3: Very long content**
- 10,000+ character references
- Should scroll smoothly
- Should not lag
- Should show accurate character count

**Test 4: HTML injection**
- Content with `<script>` tags
- Should be escaped
- Should display as text, not execute

**Test 5: Special characters**
- Unicode, emojis, symbols
- Should display correctly
- Should not break formatting

## Troubleshooting

### Scrollbar not appearing?

**Check:**
1. Is content actually > 400px tall?
2. Is CSS being applied correctly?
3. Browser zoom level (affects height)

**Fix:**
- Reduce max-height to see scrollbar sooner
- Check browser console for CSS errors

### Content not scrolling?

**Check:**
1. Is `overflow-y: auto` in the style?
2. Is max-height set?
3. Is content actually overflowing?

**Fix:**
- Verify inline styles are correct
- Check for CSS conflicts

### Character count wrong?

**Check:**
1. Counting before or after cleaning?
2. Including newlines in count?

**Fix:**
- Use `len(cleaned_footnotes)` after cleaning
- Count shows cleaned content length

## Summary

✨ **The "View detailed source references" section is now scrollable!**

**Key Points:**
- ✅ No content truncation
- ✅ 400px max height (main references)
- ✅ Smooth scrolling
- ✅ Professional appearance
- ✅ Character count indicator
- ✅ HTML escaped for security
- ✅ Works immediately, no config needed

**User Impact:**
- Better access to source information
- More professional interface
- Easier to verify policy sources
- No information loss

---

**Version:** 1.1  
**Released:** November 10, 2025  
**Status:** Active ✅  
**Breaking Changes:** None  
**Previous Behavior:** Truncated at 2000 characters  
**New Behavior:** Scrollable with full content access

