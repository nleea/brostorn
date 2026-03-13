## Goal  
Understand the problem, load the correct context, identify the root cause, implement a robust fix, validate it, and document it in the memory system.

## Workflow  
  
1. Identify the affected module or domain.  
2. Load the relevant context pack.  
3. Start with distilled context if available.  
4. Inspect supporting notes from architecture, frontend/backend, decisions, and debugging history.  
5. Summarize the current behavior before changing code.  
6. Inspect the real code paths involved in the issue.  
7. Compare expected behavior vs actual behavior.  
8. Identify the root cause.  
9. Implement a robust fix in the correct layer.  
10. Validate the fix with realistic scenarios.  
11. Save a debugging note.  
12. Update architecture or module notes if the fix changes expected behavior.  
  
## Rules  
- Do not jump directly to code changes.  
- Do not apply a quick patch without root cause analysis.  
- Prefer consistency with the existing architecture.  
- Reuse existing patterns before introducing new ones.  
- Always document the fix.  
  
## Output Expectations  
Your response should include:  
- current behavior summary  
- root cause  
- implementation plan  
- files changed  
- validation summary  
- documentation updated