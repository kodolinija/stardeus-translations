# Notes for translators

## ⚠️ Critical Rules to Follow

### 1. How to Edit Translation Files

**Recommended method:** Use **Google Sheets** to edit translations, then download as CSV when done. This automatically handles CSV formatting correctly.

**If editing manually:** Translation files are in **CSV (Comma-Separated Values)** format. Be careful with the structure:
- Each row must have the same number of columns
- Is possible use commas in text only when the entire cell content is escaped in quotes

---

### 2. File Encoding

Files must be saved in **UTF-8** (without BOM).

**How to verify/set:**
- **VS Code:** Bottom right bar → click on encoding → select "UTF-8"
- **Notepad++:** Encoding menu → "Encode in UTF-8"
- **Other editors:** Look in settings for "Encoding"

---

### 3. Variables in Curly Braces `{}`

Variables in curly braces are replaced by the game with dynamic values. **They MUST NOT be modified**.

**Rule:** Copy variables exactly from the original text:
- **Identical**
- **Braces included**
- **No spaces** inside braces

**💡 Tip:** In the source file comments you can see what the variables are replaced with in-game.

---

### 4. HTML Tags and Code in `<>`

Tags in angle brackets are formatting code. **They MUST NOT be modified, removed or changed**.

**Rule:** 
- DO NOT add spaces inside or around tags
- DO NOT translate tag names or attributes
- DO NOT change tag capitalization
- DO NOT remove or alter tags
- Translate ONLY the text between tags

---

## 🔍 How to Validate Your Translation

**Main validation method:** Use **"Generate Validity Report"** in the game's language panel with your language selected. This will show you all errors and issues.

**Before committing, also check:**

1. **Encoding:** File saved in UTF-8
2. **Variables:** All `{variables}` identical to original
3. **Tags:** All `<tags>` identical to original (name, capitalization, attributes)
4. **Column count:** Every row has the same number of columns

---

## 📋 Quick Checklist

- [ ] File saved in UTF-8
- [ ] Variables identical
- [ ] Tags not modified: `<b>` not `<B>` or `< b >`
- [ ] Tags not translated: `<color=#CC8566FF>` not `<colore=#CC8566FF>`
- [ ] Validated with "Generate Validity Report" in-game

---

## ❓ When In Doubt

- Check **comments in the source file** to understand context
- Compare with other similar strings already translated
- **Never modify** technical structure (separators, variables, tags)
- Translate **only** visible text content
- If you use translation assistance tools: **verify** they haven't modified variables/tags
- Use **Google Sheets** for editing to avoid CSV formatting issues