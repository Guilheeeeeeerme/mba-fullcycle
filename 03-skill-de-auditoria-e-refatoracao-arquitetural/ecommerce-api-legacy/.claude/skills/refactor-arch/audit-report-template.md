# Audit report template (Phase 2)

Print exactly this structure (fill placeholders):

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <directory name>
Stack:   <Language> + <Framework>
Files:   <N> analyzed | ~<LOC> lines of code

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERITY>] <Title>
File: <path>:<start>-<end>
Description: <what>
Impact: <why it matters>
Recommendation: <concrete fix aligned with MVC guidelines / playbook>

### [<SEVERITY>] <Title>
...

================================
Total: <n> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

## Ordering rules

1. CRITICAL first, then HIGH, MEDIUM, LOW
2. Within same severity, security before pure structure
3. Each finding must be actionable (file + lines)
4. Include at least one deprecated-API finding when any deprecated usage exists
