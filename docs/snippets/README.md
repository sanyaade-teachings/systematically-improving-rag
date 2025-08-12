# MkDocs Snippets

This directory contains reusable content snippets that can be included in any markdown file using the MkDocs snippets feature.

## Available Snippets

### 1. `enrollment-button.md`
Simple enrollment button without additional styling:
```markdown
--8<--
  "snippets/enrollment-button.md"
--8<--
```

### 2. `enrollment-section.md`
Enrollment section with basic styling and explanatory text:
```markdown
--8<--
  "snippets/enrollment-section.md"
--8<--
```

### 3. `enrollment-full.md`
Comprehensive enrollment section with gradient background and detailed copy:
```markdown
--8<--
  "snippets/enrollment-full.md"
--8<--
```

## How to Use

1. **Include a snippet** in any markdown file using the `--8<--` syntax
2. **Customize the snippet** by editing the source file - changes will appear everywhere it's used
3. **Create new snippets** for other recurring content

## Benefits

- **Centralized content**: Update the enrollment button in one place
- **Consistent styling**: All instances use the same design
- **Easy maintenance**: No need to update multiple files
- **Version control**: Track changes to recurring content separately

## Example Usage

```markdown
# My RAG Guide

Here's how to build better RAG applications...

--8<--
  "snippets/enrollment-section.md"
--8<--

Continue reading about evaluation strategies...
```

## Customization

To modify the appearance or content:
1. Edit the snippet file in `docs/snippets/`
2. All instances will automatically update
3. Test locally with `mkdocs serve`
4. Deploy with `mkdocs gh-deploy`

---

IF you want to get discounts and 6 day email source on the topic make sure to subscribe to

<script async data-uid="010fd9b52b" src="https://fivesixseven.kit.com/010fd9b52b/index.js"></script>
