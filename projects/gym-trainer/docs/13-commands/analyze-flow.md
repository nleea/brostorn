Use this workflow when the goal is to understand how a feature or module currently works before making changes.  
  
## Goal  
Explain the real flow of the system using memory context and actual code, without making premature assumptions.  
  
## Workflow  
  
1. Identify the module or feature to analyze.  
2. Load the relevant context pack.  
3. Start with distilled context.  
4. Review supporting architecture and module notes.  
5. Inspect the real implementation in code.  
6. Trace the flow end to end.  
7. Explain:  
- source of truth  
- main inputs  
- main transformations  
- state transitions  
- rendering/output behavior  
- dependencies  
8. Identify inconsistencies, ambiguities, or risk areas.  
9. If useful, suggest follow-up improvements separately from the analysis.  
  
## Rules  
- Do not assume documentation is fully correct; verify against code.  
- Do not propose code changes until the flow is clearly explained.  
- Keep the explanation structured and grounded.  
  
## Output Expectations  
Your response should include:  
- feature/module overview  
- flow breakdown  
- source-of-truth files  
- risk areas  
- follow-up recommendations if relevant