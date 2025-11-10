# Citation Formatting Solution - Complete Guide

## 🎯 Problem Overview

When using knowledge assistant tools (like Databricks Genie) with the NSW Procurement Compliance Agent, responses included excessive, poorly formatted footnotes with:

- ❌ Raw HTML table markup (`<table>`, `<tr>`, `<td>` tags)
- ❌ Duplicate citation content repeated 5-10 times
- ❌ Internal file system URLs and paths
- ❌ Verbose citation tables spanning hundreds of lines
- ❌ `<think>` tags showing internal reasoning

**This made responses unprofessional, difficult to read, and consumed excessive screen space.**

## ✅ Solution Overview

We've implemented a **three-layer defense** approach to ensure clean, professional citations:

### Layer 1: Knowledge Assistant System Prompt (RECOMMENDED)
**Fix the problem at the source** by configuring the knowledge assistant endpoint to produce clean citations from the start.

### Layer 2: Main Agent System Prompt (FALLBACK)
**Backup cleanup** in the main agent to handle any citations that slip through or come from other sources.

### Layer 3: Message Handling Cleanup (GUARANTEED)
**Automatic display filtering** that removes HTML tags, extracts verbose footnotes, and hides them in an expandable section. This layer always works regardless of upstream configuration.

**New Feature:** Verbose footnotes are now automatically hidden from the main chat and shown in a collapsible "📚 View detailed source references" section.

## 📚 Documentation Structure

| Document | Purpose | Who Uses It |
|----------|---------|-------------|
| **`knowledge_assistant_system_prompt.md`** | System prompt for the knowledge assistant endpoint | DevOps/Platform Admin |
| **`KNOWLEDGE_ASSISTANT_SETUP.md`** | How to apply the KA system prompt | DevOps/Platform Admin |
| **`suggested_system_prompt.md`** | System prompt for the main agent | Agent Developer |
| **`FOOTNOTE_CLEANUP_UPDATE.md`** | Details on the main agent cleanup approach | Agent Developer |
| **`FOOTNOTE_HIDING_FEATURE.md`** | **NEW:** Automatic footnote hiding in UI | All Roles |
| **`STRUCTURED_OUTPUT_GUIDE.md`** | Overall implementation guide | All Roles |
| **`QUICK_REFERENCE.md`** | Quick reference for formatting standards | All Roles |
| **This document** | Overview and decision guide | Everyone |

## 🚀 Quick Start

### Option A: Fix at Source (RECOMMENDED)

**Best for:** New implementations, or if you have control over the knowledge assistant endpoint

**Steps:**
1. Read `KNOWLEDGE_ASSISTANT_SETUP.md`
2. Apply system prompt from `knowledge_assistant_system_prompt.md` to your knowledge assistant endpoint
3. Test with sample queries
4. Optionally also apply main agent system prompt as backup

**Time Required:** 15-30 minutes

**Pros:**
- ✅ Fixes problem at the source
- ✅ Cleaner, faster responses
- ✅ Benefits all agents using the knowledge assistant
- ✅ Less processing needed downstream

**Cons:**
- Requires access to knowledge assistant endpoint configuration
- May need platform/admin permissions

### Option B: Fix at Agent Level (FALLBACK)

**Best for:** When you can't modify the knowledge assistant endpoint, or as a backup layer

**Steps:**
1. Read `FOOTNOTE_CLEANUP_UPDATE.md`
2. Apply system prompt from `suggested_system_prompt.md` to your main agent
3. Test with sample queries

**Time Required:** 10-15 minutes

**Pros:**
- ✅ No need to modify knowledge assistant endpoint
- ✅ Works with any external knowledge source
- ✅ Agent developer can implement independently

**Cons:**
- Agent has to do extra cleanup work
- Adds processing overhead
- Only benefits this specific agent

### Option C: Both Layers (BEST PRACTICE)

**Best for:** Production systems where reliability is critical

**Steps:**
1. Implement Option A (knowledge assistant system prompt)
2. Implement Option B (main agent system prompt) as backup
3. Test thoroughly

**Time Required:** 30-45 minutes

**Pros:**
- ✅ **Defense in depth** - if one layer fails, the other catches it
- ✅ Maximum reliability
- ✅ Best user experience
- ✅ Future-proof against format changes

**Cons:**
- Requires more setup time
- Needs permissions for both systems

### Layer 3: Already Implemented! ✨

**Automatic UI-Level Cleanup** (No configuration needed)

The message handling code (`messages.py`) now automatically:
- ✅ Removes HTML tags and special characters
- ✅ Extracts verbose footnotes from responses
- ✅ Hides footnotes in a "📚 View detailed source references" expander
- ✅ Keeps main chat clean and professional

**This layer is ALWAYS active** and provides guaranteed protection even if Layers 1 and 2 aren't configured.

See `FOOTNOTE_HIDING_FEATURE.md` for details.

## 📋 Implementation Checklist

### Phase 1: Knowledge Assistant Configuration (Recommended)

- [ ] Review `knowledge_assistant_system_prompt.md`
- [ ] Access your Databricks workspace
- [ ] Locate the knowledge assistant endpoint (e.g., `nsw-procurement-policy-ka`)
- [ ] Apply system prompt to the endpoint configuration
- [ ] Save and redeploy endpoint if necessary
- [ ] Test with sample policy query
- [ ] Verify no HTML markup in response
- [ ] Verify citations are clean and concise
- [ ] Document the configuration for future reference

### Phase 2: Main Agent Configuration (Backup/Fallback)

- [ ] Review `suggested_system_prompt.md`
- [ ] Locate your main agent configuration
- [ ] Apply the updated system prompt with citation cleanup instructions
- [ ] Save agent configuration
- [ ] Test with sample policy query
- [ ] Verify agent cleans up any remaining issues
- [ ] Verify structured output still working correctly
- [ ] Test with multiple knowledge assistant tool calls

### Phase 3: Validation and Testing

- [ ] Test simple policy query
- [ ] Test complex multi-source query
- [ ] Test query requiring multiple tool calls
- [ ] Check for HTML markup (should be none)
- [ ] Check for duplicate footnotes (should be none)
- [ ] Check citation format (should be clean inline or references)
- [ ] Verify response completeness (cleanup shouldn't remove content)
- [ ] Verify structured output extraction still works
- [ ] Test with edge cases (very long policies, multiple documents)

### Phase 4: Production Rollout

- [ ] Update system prompts in production environment
- [ ] Monitor first few user queries for issues
- [ ] Collect user feedback on readability
- [ ] Document any issues encountered
- [ ] Create runbook for troubleshooting
- [ ] Train team on new citation format (if needed)
- [ ] Set up monitoring for response quality

## 🎨 Expected Results

### Before Implementation

**User sees:**
```
You must monitor compliance.¹

Footnotes
¹ Contract and supplier management <table><tr><th>Relating to</th>
<th>Status</th><th>Category</th><th>Value</th><th>Obligation</th>
<th>Reference</th></tr><tr><td rowspan="4">Contract and supplier 
management</td><td rowspan="4"></td><td rowspan="4"></td><td>Any</td>
<td>Signing an agreement is not the end of a process, but rather 
the start of an ongoing relationship with the supplier. Both the 
contract and supplier relationship need to be managed to deliver 
the best outcome for the agency.</td><td rowspan="4">NSW 
Procurement's Approach</td></tr><tr><td rowspan="3">Any</td>
<td>You should</td></tr><tr><td><ul><li>ensure smooth transition 
of services, especially if there is a new supplier</li><li>jointly 
establish systems and processes with the supplier team to ensure 
compliance with contract terms and performance requirements, and 
determine who is responsible for key tasks and activities on the 
agency and supplier sides</li><li>define and maintain the right 
level of management and resources according to the business 
criticality and complexity of the procurement arrangement</li>
<li>manage performance, drive continuous improvement and encourage 
innovation in coordination with the supplier and key stakeholders</li>
<li>track and report benefits to demonstrate how value for money is 
being delivered.</li></ul></td></tr><tr><td>Supplier relationship 
management</td></tr></table> 129 Procurement-Policy-Framework_December-2024.pdf ↩

[This continues for hundreds more lines with duplicate content...]
```

**User reaction:** 😱 "What is all this mess?!"

### After Implementation

**User sees:**
```
You must monitor supplier compliance with contractual, regulatory 
and other obligations on an ongoing basis. The level and frequency 
of checks will vary depending on the value and risk profile of the 
contract (Supplier Due Diligence: A Guide for NSW Public Sector 
Agencies, NSW Procurement Policy Framework Section 2.03).

Contract management involves establishing systems with the supplier 
team to ensure compliance with contract terms and performance 
requirements. You should define and maintain the right level of 
management resources according to the business criticality and 
complexity of the procurement arrangement.

📚 View detailed source references ▼  [Click to expand if needed]
```

**If user clicks the expander:**
```
📚 View detailed source references ▼

Detailed citations and source information

NSW Procurement Policy Framework December 2024, Section 2.03:
Contract and Supplier Management

Supplier Due Diligence: A Guide for NSW Public Sector Agencies

[Cleaned references without HTML markup]
```

**User reaction:** 😊 "Perfect! Clean, professional, and I can see sources if needed."

## 🧪 Testing Examples

### Test 1: Payment Requirements

**Query:**
```
What are the NSW procurement payment requirements for small businesses?
```

**Expected Response:**
```
In-scope agencies must pay registered small businesses (defined as 
businesses with fewer than 20 FTEs) within 5 business days of receipt 
of a correctly rendered invoice, unless an existing contract or 
standing offer provides for an alternative timeframe (Faster Payment 
Terms Policy).

The Office of the Small Business Commissioner monitors and reports on 
agency payment performance to small businesses.
```

**Check for:**
- ✅ Clean inline citation
- ✅ No HTML markup
- ✅ Accurate information
- ✅ Professional formatting

### Test 2: WHS Requirements

**Query:**
```
What are the Work Health and Safety requirements for construction 
contracts over $1 million?
```

**Expected Response:**
```
For construction contracts of $1 million or more, you must:

• Agree and implement an audit schedule of the contractor's WHS 
  Management Plan
• Conduct an audit within three months of the start of site work
• Conduct at least two audits over the life of the project, or as 
  otherwise determined to suit the level of risk
• Ensure any corrective and preventive actions identified during an 
  audit are carried out within agreed timeframes

All contractors must have an acceptable WHS Management System certified 
by JAS-ANZ and aligned with AS/NZS ISO 45001 (WHS Management Guidelines).
```

**Check for:**
- ✅ Structured list format
- ✅ Clean citation
- ✅ No duplicate content
- ✅ Complete requirements

### Test 3: Multi-Source Query

**Query:**
```
What are all the supplier compliance requirements including conduct, 
monitoring, and payment verification?
```

**Expected Response:**
```
**Supplier Conduct**
You must require suppliers to comply with relevant standards of 
behaviour and use reasonable endeavours to be aware of any adverse 
findings against current or prospective suppliers. The Supplier Code 
of Conduct documents the minimum expectations for doing business with 
NSW Government.¹

**Ongoing Monitoring**
You should monitor supplier compliance with contractual, regulatory 
and other obligations on an ongoing basis. The level and frequency 
of checks will vary depending on the value and risk profile of the 
contract.²

**Payment Verification**
For construction contracts, you must take steps to verify the claims 
of head contractors about payments made to subcontractors as part of 
ongoing contract management activities.³

**References:**
1. PBD-2017-07: Conduct by Suppliers; Supplier Code of Conduct
2. Supplier Due Diligence: A Guide for NSW Public Sector Agencies
3. PBD 2013-01C: Security of Payment Requirements
```

**Check for:**
- ✅ Multiple sources cited correctly
- ✅ Deduplicated references
- ✅ Clean structure with headings
- ✅ No HTML markup

## 🔧 Troubleshooting

### Problem: Still seeing HTML markup

**Solution Path:**
1. Check if knowledge assistant system prompt was applied correctly
2. Verify endpoint was redeployed after configuration change
3. Clear any cached responses
4. Ensure main agent system prompt includes cleanup instructions
5. Test in a fresh session

**Detailed Guide:** See `KNOWLEDGE_ASSISTANT_SETUP.md` → Troubleshooting

### Problem: Citations missing entirely

**Solution Path:**
1. Review knowledge assistant system prompt - ensure it encourages citations
2. Check if the cleanup instructions are too aggressive
3. Test with specific citation-focused query
4. Review agent logs for any errors

**Detailed Guide:** See `STRUCTURED_OUTPUT_GUIDE.md` → Troubleshooting

### Problem: Response quality decreased

**Solution Path:**
1. Compare responses before/after implementation
2. Check if "concise" instruction being interpreted too strictly
3. Adjust system prompt to balance conciseness with completeness
4. Test with queries requiring detailed responses

**Detailed Guide:** See `FOOTNOTE_CLEANUP_UPDATE.md` → Troubleshooting

## 📊 Success Metrics

Track these metrics to validate the improvement:

| Metric | Before | Target After | How to Measure |
|--------|--------|--------------|----------------|
| **HTML Markup in Responses** | ~90% | 0% | Automated scan for `<table>` tags |
| **Average Footnote Length** | ~500 chars | <100 chars | Character count in citation sections |
| **User Readability Rating** | 2.5/5 | 4.5/5 | User feedback surveys |
| **Duplicate Citations** | ~5 per response | 0 | Manual review of responses |
| **Response Cleanliness** | Poor | Excellent | Qualitative assessment |

## 🔄 Maintenance

### Regular Tasks

**Weekly:**
- Spot-check 5-10 responses for formatting quality
- Review any user feedback about citations

**Monthly:**
- Run comprehensive test suite
- Review and update system prompts if needed
- Check for any new edge cases

**After Databricks Updates:**
- Re-test all citation formatting
- Verify system prompts still applied
- Check for any new configuration options

### System Prompt Version Control

Keep system prompts in Git with semantic versioning:

```
knowledge_assistant_system_prompt.md (v1.0) - Initial release
suggested_system_prompt.md (v2.1) - Added citation cleanup
```

Track changes and document reasons for updates.

## 🎓 Training Materials

### For Agent Developers

- Primary: `suggested_system_prompt.md`
- Reference: `FOOTNOTE_CLEANUP_UPDATE.md`
- Testing: `STRUCTURED_OUTPUT_GUIDE.md`

### For Platform Admins

- Primary: `KNOWLEDGE_ASSISTANT_SETUP.md`
- Reference: `knowledge_assistant_system_prompt.md`
- Testing: Test scripts in setup guide

### For End Users

- Brief them on the new citation format
- Show before/after examples
- Explain that information accuracy is maintained
- Collect feedback on readability

## 📞 Support

### If You're Stuck

1. **Read the relevant guide** for your role (see Documentation Structure above)
2. **Check the troubleshooting section** in the appropriate guide
3. **Test with provided example queries** to isolate the issue
4. **Review logs** in Databricks for any errors
5. **Compare your configuration** with the examples provided

### Common Issues Reference

| Issue | Quick Fix | Detailed Guide |
|-------|-----------|----------------|
| HTML markup visible | Apply KA system prompt | `KNOWLEDGE_ASSISTANT_SETUP.md` |
| Duplicate footnotes | Check deduplication instructions | `knowledge_assistant_system_prompt.md` |
| Citations missing | Review system prompt requirements | `FOOTNOTE_CLEANUP_UPDATE.md` |
| Agent not cleaning up | Verify main agent system prompt | `suggested_system_prompt.md` |

## 🎯 Next Steps

1. **Choose your implementation path** (Option A, B, or C above)
2. **Follow the relevant guide(s)** step by step
3. **Test thoroughly** with the provided test cases
4. **Monitor and adjust** based on real-world usage
5. **Document any customizations** you make
6. **Share feedback** to improve these guides

## 📝 Summary

**The Bottom Line:**

✅ **Apply knowledge assistant system prompt** (`knowledge_assistant_system_prompt.md`) to fix citations at the source  
✅ **Apply main agent system prompt** (`suggested_system_prompt.md`) as a backup  
✅ **Test thoroughly** to ensure clean, professional responses  
✅ **Monitor and maintain** to keep quality high  

**Result:** Professional, readable responses with clean citations that help procurement officers make informed decisions.

---

**Version:** 1.0  
**Last Updated:** November 10, 2025  
**Compatibility:** Databricks Genie, Custom Knowledge Assistants, LangChain Agents  
**Status:** Production Ready ✅

