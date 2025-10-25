# Notes for translators

## ⚠️ Critical Rules to Follow

### 1. CSV Format and Separators

Translation files are in **CSV (Comma-Separated Values)** format. Commas separate the file columns.

**Rule:** Commas separating columns **MUST NOT have spaces** before or after them.

**⚠️ IMPORTANT:** 
- Respect the **column structure** - do not add or remove commas that would alter the number of columns
- Commas **without spaces** around them are interpreted as column separators
- Commas **with spaces** are considered part of the text

---

### 2. File Encoding

Files must be saved in **UTF-8** (without BOM).

**How to verify/set:**
- **VS Code:** Bottom right bar → click on encoding → select "UTF-8"
- **Notepad++:** Encoding menu → "Encode in UTF-8"
- **Other editors:** Look in settings for "Encoding"

**⚠️ Do NOT use:** ANSI, Windows-1252, ISO-8859-1 or other encodings.

---

### 3. Leading and Trailing Spaces

**NO spaces** should be present at the beginning or end of translated strings.

**How to avoid:**
- **Whatever program you use** (Editors, translation tools, office suite etc...): verify it doesn't add spaces
- Use an editor that highlights invisible spaces
- Some translation tools add spaces automatically - always check

---

### 4. Variables in Curly Braces `{}`

Variables in curly braces are replaced by the game with dynamic values. **They MUST NOT be modified**.

**Rule:** Copy variables exactly from the original text:
- **Identical**
- **Braces included**
- **No spaces** inside braces

**💡 Tip:** In the source file comments you can see what the variables are replaced with in-game.

---

### 5. HTML Tags and Code in `<>`

Tags in angle brackets are formatting code. **They MUST NOT be modified, removed or changed**.

**Rule:** 
- DO NOT add spaces inside or around tags
- DO NOT translate tag names or attributes
- DO NOT change tag capitalization
- DO NOT remove or alter tags
- Translate ONLY the text between tags

---

## 🔍 How to Validate Your Translation

Before committing, check:

1. **CSV Separators:** No spaces before/after commas separating columns
2. **Encoding:** File saved in UTF-8
3. **Invisible spaces:** No spaces at beginning or end of strings
4. **Variables:** All `{variables}` identical to original
5. **Tags:** All `<tags>` identical to original (name, capitalization, attributes)
6. **Column count:** Every row has the same number of columns

**Useful tools:**
- Editor that highlights invisible spaces (VS Code, Notepad++ with "Show All Characters")
- Side-by-side comparison with original

---

## 📋 Quick Checklist

- [ ] File saved in UTF-8
- [ ] CSV separators without spaces: `column1,column2`
- [ ] No spaces at beginning/end of strings
- [ ] Variables identical
- [ ] Tags not modified: `<b>` not `<B>` or `< b >`
- [ ] Tags not translated: `<color=#CC8566FF>` not `<colore=#CC8566FF>`

---

## ❓ When In Doubt

- Check **comments in the source file** to understand context
- Compare with other similar strings already translated
- **Never modify** technical structure (separators, variables, tags)
- Translate **only** visible text content
- If you use translation assistance tools: **verify** they haven't added spaces or modified variables/tags