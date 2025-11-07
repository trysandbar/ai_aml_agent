# CLAUDE.md

AI AML Agent - Browser automation for AML verification workflows.

## Best Practices

### Code Quality
- **NEVER overwrite working code** - Only make additive changes
- **COMMIT working code immediately** after verification
- Never over-engineer - do exactly what was asked
- Add comments instead of single-use helper functions
- Use existing patterns from reference implementations

### Web Search Policy
Always Get the current date before web searching
**ALWAYS web search for:**
- API syntax and best practices
- Python features and syntax
- Any API or library you're uncertain about
- Security best practices

Search proactively - don't guess syntax or make assumptions.

### Browser Automation Patterns
- **Dynamic selectors**: Use JavaScript to find selectors that exist at runtime
- **Screenshots with metadata**: Always save metadata for compliance and debugging
- **Form values**: Set directly via JavaScript when possible - faster and more reliable than typing
- **Authentication caching**: Use storage state to cache auth between runs
- **Headless mode**: Always run browsers in headless mode for production

### Debugging Workflow
1. Check screenshots in debug output directory
2. Fix errors (selectors, timeouts, URLs)
3. Verify with multiple runs
4. Commit when stable

### Security
- Store secrets in `.env` files (gitignored)
- Never commit credentials or API keys
- Use environment variables for sensitive data
- always check for a venv before testing or running anything, and load keys from the env or .env