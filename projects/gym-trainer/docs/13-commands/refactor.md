Use this workflow when improving code quality, structure, naming, or maintainability without intentionally changing behavior.  
  
## Goal  
Refactor code safely while preserving existing behavior and keeping documentation aligned.  
  
## Workflow  
  
1. Identify the target module.  
2. Load the relevant context pack.  
3. Review distilled context first.  
4. Review architecture notes, patterns, and related decisions.  
5. Summarize the current design and constraints.  
6. Identify refactor opportunities:  
- duplicated logic  
- weak naming  
- poor separation of concerns  
- stale patterns  
- brittle conditionals  
7. Propose the refactor before implementing it.  
8. Preserve behavior unless explicitly instructed otherwise.  
9. Apply the refactor incrementally.  
10. Validate that behavior remains intact.  
11. Update relevant notes if the structure or important conventions changed.  
  
## Rules  
- Do not mix refactor and feature work unless explicitly requested.  
- Do not silently change business behavior.  
- Prefer small, well-justified changes.  
- Keep the code aligned with existing architectural patterns.  
  
## Output Expectations  
Your response should include:  
- current structure summary  
- refactor targets  
- implementation summary  
- files changed  
- behavior preservation notes  
- documentation updated