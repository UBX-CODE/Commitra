import subprocess
from typing import List, Tuple
from models.schemas import ChangedFile, RepoContext
from utils.config import config

SENSITIVE_PATTERNS = [
    ".env", ".env.", ".pem", ".key", "id_rsa", "id_ed25519", 
    "credentials.json", "service-account", "secret"
]

def run_git_command(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
        check=False
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"Git command failed: git {' '.join(args)}")
    return result.stdout.strip()

def is_git_repository() -> bool:
    try:
        run_git_command(["rev-parse", "--is-inside-work-tree"])
        return True
    except RuntimeError:
        return False

def get_current_branch() -> str:
    try:
        return run_git_command(["branch", "--show-current"])
    except RuntimeError:
        return ""

def is_file_sensitive(filepath: str) -> bool:
    filepath_lower = filepath.lower()
    for pattern in SENSITIVE_PATTERNS:
        if pattern in filepath_lower:
            return True
    return False

def get_changed_files() -> List[ChangedFile]:
    status_output = run_git_command(["status", "--porcelain"])
    if not status_output:
        return []

    changed_files = []
    for line in status_output.splitlines():
        if len(line) < 4:
            continue
        
        status_code = line[0:2]
        filepath = line[3:].strip()
        
        # Handle renames (e.g., R  old -> new)
        if "->" in filepath:
            filepath = filepath.split("->")[-1].strip()

        # X is staged, Y is unstaged
        # Index status is line[0], Working tree status is line[1]
        staged_status = status_code[0]
        unstaged_status = status_code[1]

        if staged_status not in [" ", "?", "!"]:
            status_desc = _map_status_code(staged_status)
            changed_files.append(ChangedFile(path=filepath, status=status_desc, staged=True))
            
        if unstaged_status not in [" ", "?", "!"]:
            status_desc = _map_status_code(unstaged_status)
            changed_files.append(ChangedFile(path=filepath, status=status_desc, staged=False))
            
        if staged_status == "?" and unstaged_status == "?":
            changed_files.append(ChangedFile(path=filepath, status="untracked", staged=False))

    return changed_files

def _map_status_code(code: str) -> str:
    mapping = {
        "M": "modified",
        "A": "added",
        "D": "deleted",
        "R": "renamed",
        "C": "copied",
        "U": "updated but unmerged",
    }
    return mapping.get(code, "unknown")

def get_diff(staged: bool = False, max_chars: int = config.MAX_DIFF_CHARS) -> str:
    args = ["diff"]
    if staged:
        args.append("--cached")
    
    # We must exclude sensitive files from the diff
    files = get_changed_files()
    sensitive_files = [f.path for f in files if is_file_sensitive(f.path) and f.staged == staged]
    
    for sensitive_file in sensitive_files:
        args.extend([":(exclude)" + sensitive_file])

    diff_text = run_git_command(args)
    
    if len(diff_text) > max_chars:
        # Truncate and add warning
        truncated = diff_text[:max_chars]
        return truncated + f"\n\n... [DIFF TRUNCATED: Exceeded {max_chars} characters] ..."
    return diff_text

def get_recent_commits(count: int = config.RECENT_COMMIT_COUNT) -> List[str]:
    try:
        log_output = run_git_command(["log", f"-{count}", "--pretty=format:%s"])
        return [line.strip() for line in log_output.splitlines() if line.strip()]
    except RuntimeError:
        return []

def gather_repository_context() -> RepoContext:
    branch = get_current_branch()
    changed_files = get_changed_files()
    staged_diff = get_diff(staged=True)
    unstaged_diff = get_diff(staged=False)
    recent_commits = get_recent_commits()
    
    return RepoContext(
        branch=branch,
        changed_files=changed_files,
        staged_diff=staged_diff,
        unstaged_diff=unstaged_diff,
        recent_commits=recent_commits
    )

def execute_commit(files: List[str], subject: str, body: List[str]) -> str:
    if not files:
        raise ValueError("No files provided to commit.")

    # Stage explicitly
    run_git_command(["add", "--"] + files)
    
    # Commit
    commit_args = ["commit", "-m", subject]
    for p in body:
        commit_args.extend(["-m", p])
        
    run_git_command(commit_args)
    
    # Verify and return hash/message
    return run_git_command(["log", "-1", "--pretty=format:%H%n%s"])
