# Quick Start: Fix Citation Formatting

## 🎯 Goal
Get clean, professional citations without HTML markup or duplicate footnotes.

## ⚡ Fastest Path (5 minutes)

### For Knowledge Assistant Endpoint

1. **Copy the system prompt:**
   ```bash
   cat knowledge_assistant_system_prompt.md | pbcopy
   ```

2. **Apply to your endpoint:**
   - Go to Databricks → Serving → Your KA Endpoint
   - Find "Instructions" or "System Prompt" section
   - Paste the copied content
   - Save and redeploy

3. **Test:**
   ```
   Query: "What are the payment terms for small businesses?"
   
   ✅ Should see: Clean citation like "(Faster Payment Terms Policy)"
   ❌ Should NOT see: <table>, <tr>, <td> tags
   ```

**Done!** ✨

---

## 📚 Full Documentation

| What You Need | Read This |
|---------------|-----------|
| **Detailed setup for KA endpoint** | `KNOWLEDGE_ASSISTANT_SETUP.md` |
| **The KA system prompt** | `knowledge_assistant_system_prompt.md` |
| **Main agent setup** | `FOOTNOTE_CLEANUP_UPDATE.md` |
| **Main agent system prompt** | `suggested_system_prompt.md` |
| **Complete overview** | `CITATION_FORMATTING_README.md` |

---

## 🔍 Quick Validation

After applying the system prompt, test with:

```
What are the NSW procurement policy requirements for supplier monitoring?
```

**Good Response:**
```
You must monitor supplier compliance on an ongoing basis. The level 
and frequency of checks will vary depending on the value and risk 
profile of the contract (Supplier Due Diligence Guide).
```

**Bad Response:**
```
You must monitor compliance.¹

Footnotes:
¹ <table><tr><th>Status</th>...[200 lines of HTML]...
```

---

## 🆘 Having Issues?

1. **HTML still appearing?** → See `KNOWLEDGE_ASSISTANT_SETUP.md` → Troubleshooting → Issue 1
2. **Prompt not taking effect?** → See `KNOWLEDGE_ASSISTANT_SETUP.md` → Troubleshooting → Issue 2
3. **Citations missing?** → See `KNOWLEDGE_ASSISTANT_SETUP.md` → Troubleshooting → Issue 3

---

## 📞 Need More Help?

Read the comprehensive guide: `CITATION_FORMATTING_README.md`

