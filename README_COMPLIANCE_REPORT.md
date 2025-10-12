# Transport Procurement Compliance Report Feature

## Overview

The Compliance Report feature automatically extracts suppliers at risk and compliance due diligence actions from chat conversations, presenting them in a structured, actionable format.

## Features

### 📊 Separate Report Page
- Dedicated page accessible via sidebar navigation
- Clean separation between chat and reporting functionality
- Real-time analysis of conversation history

### 🏢 Suppliers at Risk
- **Structured Information:**
  - Supplier name
  - Risk type (Financial, Compliance, Reputational, Operational)
  - Severity level (High, Medium, Low)
  - Detailed context with evidence
- **Visual Indicators:** Color-coded severity badges
- **Interactive:** Add notes and follow-up actions for each supplier

### ✅ Compliance Actions
- **Categorized Actions:**
  - Audit/Review
  - Verification
  - Documentation
  - Monitoring
  - Communication
- **Priority Levels:** High, Medium, Low
- **Rationale:** Why each action is necessary
- **Tracking:** Checkboxes to mark completion

### 📥 Export Options
- **JSON Format:** Machine-readable for system integration
- **Text Format:** Human-readable reports
- **Metadata:** Timestamps, analysis summary
- **Preview:** View data before downloading

## How It Works

### Data Extraction Methods

The system supports **two extraction methods**:

#### 1. Structured JSON (Recommended) ⭐
- Agent outputs data in predefined JSON format
- 100% accurate extraction
- Rich metadata (rationale, evidence, etc.)
- See `suggested_system_prompt.md` for implementation

#### 2. Regex Pattern Matching (Fallback)
- Automatically used for unstructured responses
- Uses intelligent pattern matching
- Backward compatible with existing conversations
- Less accurate but ensures data is never lost

### Extraction Process

```
Chat History → Content Cleaning → JSON Parsing → Regex Fallback → 
Categorization → Deduplication → Structured Output → Display
```

## Quick Start

### For Users

1. **Navigate to Chat Page**
   - Have conversations with the compliance agent
   - Ask about suppliers, risks, compliance issues

2. **Generate Report**
   - Click "📋 Compliance Report" in sidebar
   - Report analyzes all conversation history
   - View structured data in three tabs

3. **Review and Export**
   - Review identified suppliers and actions
   - Add notes and mark completed items
   - Export data as JSON or Text

### For Administrators

1. **Configure Agent System Prompt**
   - Use the prompt from `suggested_system_prompt.md`
   - Update your agent/model serving configuration
   - Test with example queries

2. **Verify Structured Output**
   - Check agent responses include JSON markers
   - Validate JSON format
   - Test extraction in report page

3. **Monitor and Iterate**
   - Review extraction accuracy
   - Adjust patterns if needed
   - Gather user feedback

## Files Reference

| File | Purpose |
|------|---------|
| `app.py` | Main application with chat and report pages |
| `suggested_system_prompt.md` | Recommended agent system prompt |
| `STRUCTURED_OUTPUT_GUIDE.md` | Comprehensive implementation guide |
| `QUICK_REFERENCE.md` | Quick reference card for output format |
| `README_COMPLIANCE_REPORT.md` | This file - overview and guide |

## Architecture

### Page Structure
```
app.py
├── Sidebar Navigation
│   ├── 💬 Chat Page
│   ├── 📋 Compliance Report Page
│   └── 🗑️ Clear History
│
├── Chat Page
│   ├── Message Rendering
│   ├── Chat Input
│   └── Streaming Responses
│
└── Report Page
    ├── Summary Metrics
    ├── Suppliers at Risk Tab
    │   ├── Structured Display
    │   ├── Notes Fields
    │   └── Save Functionality
    ├── Compliance Actions Tab
    │   ├── Priority Groups
    │   ├── Completion Tracking
    │   └── Notes Fields
    └── Export Tab
        ├── JSON Download
        ├── Text Download
        └── Data Preview
```

### Data Flow

```
User Query → Agent Processing → Structured Output → Session History →
Report Generation → Data Extraction → UI Display → Export
```

## Configuration

### Environment Variables

The app uses the following environment variable:
```bash
SERVING_ENDPOINT=your-endpoint-name
```

### Session State

The application manages these session state variables:
- `history`: Chat message history
- `current_page`: Active page ("chat" or "report")
- `report_timestamp`: When report was generated
- `show_report`: (deprecated) Legacy report display flag

### Extraction Parameters

Configurable in `extract_compliance_data()`:
```python
suppliers_list[:15]      # Max 15 suppliers
unique_actions[:25]      # Max 25 actions
detail[:100]             # Detail key length for deduplication
action[:80]              # Action key length for deduplication
```

## Customization

### Adding New Risk Types

1. Update `suggested_system_prompt.md`:
```markdown
- Environmental Risk: Climate-related concerns
- Cybersecurity Risk: Data security issues
```

2. Update extraction patterns in `app.py` if needed

3. Test with queries targeting new risk types

### Adding New Action Categories

1. Update system prompt with new categories
2. Update categorization logic in extraction
3. Update UI display if needed

### Custom Export Formats

Add new export formats in the Export tab:
```python
# Example: CSV export
csv_data = convert_to_csv(export_data)
st.download_button(
    label="📊 Download as CSV",
    data=csv_data,
    file_name=f"compliance_report_{timestamp}.csv",
    mime="text/csv"
)
```

## Best Practices

### For Agent Configuration

1. **Use Structured Output**: Implement the suggested system prompt
2. **Be Specific**: Include exact supplier names and evidence
3. **Categorize Clearly**: Use provided categories consistently
4. **Include Rationale**: Always explain why actions are needed

### For End Users

1. **Ask Specific Questions**: Better questions = better extraction
2. **Review Before Export**: Verify accuracy of extracted data
3. **Add Context**: Use notes fields to add local knowledge
4. **Track Actions**: Mark items as completed for follow-up

### For Developers

1. **Test Both Methods**: Verify structured and regex extraction
2. **Monitor Logs**: Check for JSON parsing warnings
3. **Validate Input**: Ensure clean text before extraction
4. **Handle Edge Cases**: Long names, special characters, etc.

## Troubleshooting

### Common Issues

**Issue: No data in report**
- Ensure conversations mention suppliers and risks
- Check that system prompt is properly configured
- Try example queries from documentation

**Issue: Incorrect categorization**
- Review agent output format
- Check JSON structure matches expected schema
- Verify regex patterns capture relevant text

**Issue: Missing fields**
- Ensure agent includes all required fields
- Check JSON parsing isn't failing silently
- Review logger warnings

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check browser console for JavaScript errors.

## Performance

### Optimization Tips

1. **Limit History**: Clear old conversations periodically
2. **Efficient Extraction**: Limits prevent processing huge datasets
3. **Caching**: Session state caches extracted data
4. **Streaming**: Chat uses streaming for better UX

### Scalability

Current limits:
- Max 15 suppliers in report
- Max 25 compliance actions
- Max 3 details per supplier
- Processes entire session history on demand

For large-scale deployments, consider:
- Database storage for history
- Background processing for extraction
- Pagination in report display
- Incremental extraction updates

## Security Considerations

1. **Data Privacy**: Conversations may contain sensitive procurement data
2. **Access Control**: Implement authentication before deployment
3. **Audit Trail**: Consider logging report generation events
4. **Export Security**: Validate user permissions before allowing exports

## Future Enhancements

Potential roadmap items:

- [ ] Real-time extraction during conversation
- [ ] Historical trend analysis
- [ ] Risk score calculations
- [ ] Email notifications for high-priority items
- [ ] Integration with procurement management systems
- [ ] Collaborative features (multi-user notes)
- [ ] Advanced filtering and search
- [ ] Custom report templates
- [ ] Scheduled report generation
- [ ] API endpoints for programmatic access

## Support

### Documentation
- `suggested_system_prompt.md` - System prompt template
- `STRUCTURED_OUTPUT_GUIDE.md` - Implementation guide
- `QUICK_REFERENCE.md` - Quick reference card

### Testing
- Use provided example queries
- Validate JSON output format
- Test both extraction methods
- Check export functionality

### Feedback
- Report issues with extraction accuracy
- Suggest new risk types or categories
- Request additional export formats
- Share use cases and improvements

## License

This feature is part of the Transport Procurement Compliance App.

---

**Version:** 1.0  
**Last Updated:** October 2025  
**Author:** Transport Procurement Team

