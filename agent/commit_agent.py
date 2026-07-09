import sys
from tools.git_tools import (
    is_git_repository, get_changed_files, gather_repository_context, execute_commit
)
from llm.client import LLMClient
from ui.terminal import (
    display_banner, print_step, print_success, print_error, print_warning,
    display_single_proposal, display_multiple_proposal, prompt_approval,
    prompt_edit_single, prompt_feedback, display_diff, display_repo_summary
)

class CommitAgent:
    def __init__(self):
        self.llm_client = LLMClient()
    
    def run(self):
        display_banner()
        
        # Step 1: Observe
        print_step(1, 6, "Checking repository...")
        if not is_git_repository():
            print_error("Current directory is not a Git repository.")
            sys.exit(1)
        print_success("Git repository detected")
        
        # Step 2: Inspect Changes
        print_step(2, 6, "Inspecting changes...")
        changed_files = get_changed_files()
        if not changed_files:
            print_success("Working tree is clean.\nNothing to commit.")
            sys.exit(0)
        print_success(f"{len(changed_files)} changed files found")
        
        # Step 3: Gather Context
        print_step(3, 6, "Gathering context...")
        repo_context = gather_repository_context()
        print_success("Staged and unstaged changes inspected")
        print_success("Recent commit history inspected")
        
        display_repo_summary(repo_context)
        
        # Step 4 & 5: Analyze and Decide
        print_step(4, 6, "Analyzing semantic intent...")
        
        feedback = None
        analysis = None
        while True:
            # LLM Analysis
            try:
                analysis = self.llm_client.analyze_commits(repo_context, feedback)
            except Exception as e:
                print_error(str(e))
                print_error("AI analysis failed. No repository changes were modified.")
                sys.exit(1)

            # Quality Check
            quality_error = self._run_quality_checks(analysis)
            if quality_error and not feedback:
                # First time quality check failure -> auto-regenerate with targeted feedback
                print_warning(f"Quality check failed: {quality_error}. Retrying...")
                feedback = f"Your previous response failed quality checks: {quality_error}. Please improve it by being specific and concrete."
                continue
            
            # If we pass or already retried once, break and show proposal
            print_success(f"Intent analyzed: {analysis.summary}")
            
            print_step(5, 6, "Deciding strategy...")
            if analysis.strategy == "multiple":
                print_success("Multiple commits recommended")
            else:
                print_success("Single logical commit recommended")
            
            # Step 6: Propose & Approve
            print_step(6, 6, "Generating proposal...\n")
            
            while True:
                if analysis.strategy == "single":
                    display_single_proposal(analysis)
                else:
                    display_multiple_proposal(analysis)
                
                action = prompt_approval()
                
                if action == "C":
                    print_warning("Cancelled by user. No changes made.")
                    sys.exit(0)
                elif action == "D":
                    display_diff()
                    continue # Loop back to prompt
                elif action == "E":
                    if analysis.strategy == "single":
                        prompt_edit_single(analysis)
                        continue # Loop back to show edited proposal
                    else:
                        print_warning("Editing multiple commits directly is not supported in MVP. Try regenerating.")
                        continue
                elif action == "R":
                    feedback = prompt_feedback()
                    print_step(4, 6, "Re-analyzing...")
                    break # Break inner loop to trigger re-analysis
                elif action == "A":
                    self._execute_approved(analysis)
                    sys.exit(0)
            
            if action == "R":
                continue # loop outer

    def _run_quality_checks(self, analysis) -> str | None:
        vague_phrases = ["update code", "make changes", "fix stuff", "improve user experience", 
                         "update configuration settings", "update terminal ui", "minor fixes", "refactor interactive workflow"]
        
        def check_text(text: str) -> str | None:
            if not text: return None
            text_lower = text.lower()
            for phrase in vague_phrases:
                if phrase in text_lower:
                    return f"Contains vague phrase '{phrase}'"
            return None

        if analysis.strategy == "single":
            if err := check_text(analysis.subject): return err
            if err := check_text(analysis.intent): return err
            if analysis.body and any(analysis.subject.strip().lower() == b.strip().lower() for b in analysis.body):
                return "Body repeats subject verbatim."
        else:
            for g in analysis.groups:
                if err := check_text(g.subject): return err
                if g.body and any(g.subject.strip().lower() == b.strip().lower() for b in g.body):
                    return f"Body repeats subject verbatim in commit: {g.subject}"
        return None

    def _execute_approved(self, analysis):
        if analysis.strategy == "single":
            # Gather all files
            files_to_commit = [f.path for f in get_changed_files()]
            
            # Format subject
            subject = analysis.subject
            if analysis.commit_type:
                scope_str = f"({analysis.scope})" if analysis.scope else ""
                subject = f"{analysis.commit_type}{scope_str}: {analysis.subject}"
                
            try:
                print_step(6, 6, "Staging and committing...")
                result = execute_commit(files_to_commit, subject, analysis.body)
                print_success("Commit created successfully")
                print(f"\n{result}\n")
            except Exception as e:
                print_error(f"Failed to commit: {e}")
        else:
            # Multiple strategy execution
            # Ensure disjoint files
            seen_files = set()
            safe = True
            for g in analysis.groups:
                for f in g.files:
                    if f in seen_files:
                        safe = False
                    seen_files.add(f)
            
            if not safe:
                print_error("Multiple commit groups share files. Auto-execution requires disjoint file groups. Please split manually.")
                sys.exit(1)
            
            try:
                for idx, group in enumerate(analysis.groups, 1):
                    scope_str = f"({group.scope})" if group.scope else ""
                    subject = f"{group.commit_type}{scope_str}: {group.subject}"
                    print_step(6, 6, f"Committing group {idx}...")
                    result = execute_commit(group.files, subject, group.body)
                    print_success(f"Commit {idx} created")
                    print(f"\n{result}\n")
            except Exception as e:
                print_error(f"Failed during multiple commits: {e}")
