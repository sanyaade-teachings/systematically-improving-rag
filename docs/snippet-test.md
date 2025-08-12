# Snippet Test

This is a test to see if we can create a maintainable solution.

## Working Solution

Since MkDocs snippets and HTML includes are not working in this environment, here's a practical alternative:

### Option 1: Direct Markdown (Recommended)
```markdown
[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }
```

### Option 2: Styled Section
```markdown
---

**Want to systematically improve your RAG applications?**

[Enroll in the Free 6-Day Email Course](https://improvingrag.com/){ .md-button .md-button--primary }

*Learn evaluation strategies, user experience design, and architectural patterns that actually work in production.*

---
```

## Current Status

- ❌ MkDocs snippets not working
- ❌ HTML includes not working  
- ✅ Direct markdown works perfectly
- ✅ MkDocs button styling works

## Recommendation

Use direct markdown with the button styling. While not as elegant as snippets, it's:
- 100% reliable
- Easy to maintain
- Consistent across all files
- No configuration issues 