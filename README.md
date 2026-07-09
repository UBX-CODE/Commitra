# Commitra - Agentic AI Git Commit CLI

**One-line description:** An Agentic AI-powered command-line tool that intelligently analyzes Git repository changes and helps users create meaningful, context-aware Git commits.

## Problem Statement
Creating high-quality, descriptive Git commits is often treated as an afterthought. Standard AI wrappers usually just pipe `git diff` to an LLM, which ignores context, fails on large diffs, exposes secrets, and lacks an understanding of repository-specific commit styles. 

## Why this is Agentic AI
Commitra is not just a text-generator. It operates as an **agent** using the following workflow:
**Observe → Gather Context → Analyze → Decide → Propose → Human Approval → Act → Verify**
It inspects the state of the repository, uses deterministic tools to pull safe data, makes independent strategic decisions (like grouping commits vs single commits), waits for explicit human approval, and then safely executes actions.

## Features
- Detects staged, unstaged, and untracked files separately.
- Infers Conventional Commit types and scopes based on semantic intent.
- Infers repository style from recent commit history.
- Decides between single vs multiple commit strategies.
- Truncates oversized diffs to maintain stability.
- Redacts/ignores common sensitive files (e.g., `.env`, `.pem`).
- Interactive terminal UI with rich formatting.
- Safely stages and commits only approved files.

## Architecture
```
                CommitAgent
                    │
       ┌────────────┼─────────────┐
       │            │             │
       ▼            ▼             ▼
   Git Tools    LLM Analyzer   Terminal UI
       │            │             │
       ▼            ▼             ▼
 Repository     Semantic       Human
  Context       Decision       Approval
       │            │             │
       └────────────┼─────────────┘
                    ▼
             Safe Git Action
                    │
                    ▼
                Verification
```

## Agent Workflow
1. **Observe**: Ensure we are in a valid Git repo with changes.
2. **Gather Repository Context**: Use Git tools to pull diffs, file status, and history.
3. **Semantic Analysis**: Send context to the LLM to understand intent.
4. **Commit Strategy Decision**: Decide between a `single` or `multiple` commit strategy.
5. **Generate Proposal**: Return structured Pydantic models with the commit data.
6. **Human Approval**: Display the interactive UI prompt.
7. **Safe Git Execution**: If approved, explicitly stage and commit files.
8. **Verification**: Confirm commit success using `git log`.

## Tech Stack
- **Python 3.11+**
- **Typer**: CLI structure
- **Rich**: Terminal UI
- **Pydantic**: Structured schemas and validation
- **python-dotenv**: Environment variables
- **subprocess**: Deterministic Git command execution
- **google-generativeai**: Direct LLM SDK

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/commitra.git
   cd commitra
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Configuration
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open `.env` and add your Gemini API Key:
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-flash
MAX_DIFF_CHARS=30000
RECENT_COMMIT_COUNT=5
```

## Usage
Run the default workflow in any Git repository:
```bash
python main.py
```
This will automatically observe your current repository, gather context, and provide a proposal.

## Example Terminal Session
```
╭────────────────────────────────────────────╮
│ Commitra                                   │
│ Agentic AI Git Commit CLI                  │
╰────────────────────────────────────────────╯

[1/6] Checking repository...
✓ Git repository detected
...
╭────────────────────────────────────────────╮
│ Suggested Commit                           │
├────────────────────────────────────────────┤
│ feat(auth): improve JWT token handling     │
│                                            │
│ • extract token generation utility         │
│ • strengthen middleware validation         │
│ • simplify authentication controller       │
╰────────────────────────────────────────────╯
Intent:
Improve authentication reliability and token handling.
Confidence:
92%

[A] Approve  [E] Edit  [R] Regenerate  [D] Show Diff  [C] Cancel
Action: A

[6/6] Staging and committing...
✓ Commit created successfully
```

## Safety Model
- **No `shell=True`**: All Git commands use explicit argument lists.
- **Sensitive file protection**: Files like `.env`, `*.key` are excluded from the diff context.
- **Diff size limit**: Configurable limits prevent exceeding context windows.
- **Explicit staging**: Commitra stages specific paths instead of running `git add .` blindly.
- **No LLM execution**: The LLM output is strictly validated JSON. It cannot run commands.

## Current Limitations
- Untracked file contents are not read.
- Hunk-level commit splitting is not supported; multiple commits only work for completely disjoint file groups.
- No auto-push functionality.

## Future Improvements
- Pluggable LLM providers (e.g., OpenAI, Anthropic).
- Integration with pre-commit hooks.
- Semantic file grouping logic without relying on disjoint strict file changes.
