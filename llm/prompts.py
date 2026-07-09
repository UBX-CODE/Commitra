SYSTEM_PROMPT = """You are Commitra, an expert agentic Git commit assistant.

Your responsibility is to analyze repository changes and propose safe, meaningful, logically coherent Git commits.

You must:
1. Understand semantic code intent.
2. Classify changes using Conventional Commits.
3. Infer concise scopes.
4. Consider repository commit history.
5. Decide whether changes form one logical concern or multiple independent concerns.
6. Avoid vague commit messages.
7. Never claim that a commit was executed.
8. Never generate shell commands for execution.
9. Return valid structured JSON only.
10. Prefer concise imperative subjects.

Avoid vague subjects such as:
- update code
- fix stuff
- make changes
- modified files
- improvements
- minor fixes

Supported commit types: feat, fix, docs, style, refactor, test, chore, perf, build, ci

Output Requirements:
You must return a valid JSON object matching the requested schema exactly.
"""

def build_analysis_prompt(repo_context_json: str, user_feedback: str = None) -> str:
    prompt = f"""
Analyze the following repository context and determine the best Git commit strategy.

Repository Context:
{repo_context_json}
"""
    if user_feedback:
        prompt += f"\nUser Feedback for Regeneration:\n{user_feedback}\n"
    
    prompt += """
Based on the context, decide if the changes should be a single commit or split into multiple commits.
- Use 'single' if all changes relate to a single logical concern.
- Use 'multiple' if there are distinct, independent concerns that can be cleanly separated by file.

Output a JSON object matching this schema:
{
  "summary": "string, a brief summary of all changes",
  "intent": "string, the semantic intent behind the changes",
  "strategy": "string, either 'single' or 'multiple'",
  "confidence": "number, float between 0.0 and 1.0",
  "reasoning": "string, explanation for your strategy and commit choice",
  
  // IF strategy is 'single', provide these fields:
  "commit_type": "string, one of the supported types",
  "scope": "string, optional scope",
  "subject": "string, concise imperative subject",
  "body": ["string", "string"], // optional list of body paragraphs
  
  // IF strategy is 'multiple', provide this field instead of the single commit fields:
  "groups": [
    {
      "files": ["file1.py", "file2.py"],
      "commit_type": "string",
      "scope": "string",
      "subject": "string",
      "body": ["string"],
      "reason": "string"
    }
  ]
}
"""
    return prompt
