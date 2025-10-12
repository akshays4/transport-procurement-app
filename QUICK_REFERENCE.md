# Structured Output Quick Reference

## Output Template

```
[Your natural language response here]

---STRUCTURED_DATA---
{
  "suppliers_at_risk": [
    {
      "supplier_name": "Company Name",
      "risk_type": "Financial Risk | Compliance Risk | Reputational Risk | Operational Risk",
      "severity": "High | Medium | Low",
      "summary": "Brief description of risk",
      "evidence": "Source of information"
    }
  ],
  "compliance_actions": [
    {
      "action": "Action description starting with verb",
      "category": "Audit/Review | Verification | Documentation | Monitoring | Communication",
      "priority": "High | Medium | Low",
      "rationale": "Why this action is needed"
    }
  ]
}
---END_STRUCTURED_DATA---
```

## Risk Types

| Type | Use When |
|------|----------|
| **Financial Risk** | Bankruptcy, debt, cash flow problems, credit issues |
| **Compliance Risk** | Policy violations, regulatory breaches, non-compliance |
| **Reputational Risk** | Negative news, scandals, public criticism, PR issues |
| **Operational Risk** | Delivery failures, capacity issues, performance problems |

## Severity Levels

| Level | Definition | Timeline |
|-------|------------|----------|
| **High** | Immediate procurement impact | Urgent action required |
| **Medium** | Moderate concern | Standard monitoring |
| **Low** | Minor issue | Routine oversight |

## Action Categories

| Category | Examples |
|----------|----------|
| **Audit/Review** | Conduct audit, Perform assessment, Review records |
| **Verification** | Verify credentials, Confirm compliance, Validate claims |
| **Documentation** | Record findings, Maintain logs, Prepare report |
| **Monitoring** | Track performance, Monitor deliveries, Observe progress |
| **Communication** | Contact supplier, Notify stakeholders, Report to management |

## Priority Levels

| Priority | Timeframe | Action |
|----------|-----------|--------|
| **High** | Days to weeks | Must complete urgently |
| **Medium** | Weeks to months | Should complete in normal timeframe |
| **Low** | Months+ | Can defer if resources limited |

## Common Patterns

### Financial Risk Example
```json
{
  "supplier_name": "ABC Logistics Ltd",
  "risk_type": "Financial Risk",
  "severity": "High",
  "summary": "Company reported 45% decline in revenue and defaulted on recent loan payments",
  "evidence": "Q3 2024 Financial Report, ASX announcement dated 15 Sept 2024"
}
```

### Compliance Risk Example
```json
{
  "supplier_name": "XYZ Construction",
  "risk_type": "Compliance Risk",
  "severity": "Medium",
  "summary": "Found to be non-compliant with WH&S regulations in recent audit",
  "evidence": "SafeWork NSW audit report #2024-1234, dated 20 Aug 2024"
}
```

### High Priority Action Example
```json
{
  "action": "Conduct immediate financial audit of supplier's last three years of financial statements",
  "category": "Audit/Review",
  "priority": "High",
  "rationale": "Significant financial instability may impact ability to deliver on multi-year contract obligations"
}
```

## Dos and Don'ts

### ✅ DO:
- Use exact company names
- Cite specific sources and dates
- Use imperative verbs for actions
- Include clear rationale
- Be specific about timeframes
- Provide measurable criteria

### ❌ DON'T:
- Use vague terms like "some issues"
- Omit evidence sources
- Mix multiple risk types in one entry
- Use passive voice for actions
- Skip the rationale field
- Include subjective opinions without evidence

## Testing Commands

```bash
# Test the agent response format
curl -X POST "YOUR_ENDPOINT" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "role": "user",
      "content": "What are the risks with ABC Transport?"
    }]
  }' | jq '.choices[0].message.content'
```

## Validation Checklist

Before submitting agent output:

- [ ] JSON is valid (use jsonlint.com)
- [ ] All required fields present
- [ ] Values match allowed options
- [ ] Evidence includes sources
- [ ] Actions use imperative form
- [ ] Markers are exact (including dashes)
- [ ] No extra characters in JSON

## Emergency Fallback

If structured output fails, the system automatically falls back to regex-based extraction. But structured output is much more accurate!

---

**Print this page for quick reference while configuring your agent!**

