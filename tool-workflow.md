# Tool Workflow — AI-Assisted Development

**Candidate:** Nikhil Kr. Nirmal | **AI Tool:** Cursor

## Process

For each phase:

1. Send focused prompt to Cursor with context from existing docs
2. Review generated code/docs
3. Save prompt summary in `ai-prompts/<phase>.md`
4. Run validation for that phase
5. Commit code + docs + prompt artifact together

## Prompt Artifact Template

```markdown
### PROMPT SENT
(full prompt)

### AI RESPONSE SUMMARY
(what was generated)

### YOUR EVALUATION
✓ Accepted / △ Changed / ✗ Rejected

### FINAL DECISION
(what was kept)
```

## Phase → Prompt File Mapping

| Phase | Prompt file |
|-------|-------------|
| Foundation | `ai-prompts/documentation.md` |
| Data generation | `ai-prompts/data-generation.md` |
| Bronze | `ai-prompts/bronze-layer.md` |
| Silver | `ai-prompts/silver-layer.md` |
| Gold | `ai-prompts/gold-layer.md` |
| Dashboard | `ai-prompts/dashboard.md` |
| Validation | `ai-prompts/validation.md` |
| Database | `ai-prompts/database.md` |
| Debugging | `ai-prompts/debugging.md` |

## Rules

- Human reviews all AI output before acceptance
- No secrets in repository
- Docs updated with implementation, not at the end
- One phase at a time — do not skip ahead
