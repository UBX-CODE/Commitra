from pydantic import BaseModel, Field
from typing import Literal

CommitType = Literal[
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "test",
    "chore",
    "perf",
    "build",
    "ci"
]

class ChangedFile(BaseModel):
    path: str
    status: str
    staged: bool

class RepoContext(BaseModel):
    branch: str
    changed_files: list[ChangedFile]
    staged_diff: str
    unstaged_diff: str
    recent_commits: list[str]

class CommitGroup(BaseModel):
    files: list[str]
    commit_type: CommitType
    scope: str | None = None
    subject: str
    body: list[str] = []
    reason: str

class CommitAnalysis(BaseModel):
    summary: str
    intent: str
    strategy: Literal["single", "multiple"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    commit_type: CommitType | None = None
    scope: str | None = None
    subject: str | None = None
    body: list[str] = []
    groups: list[CommitGroup] = []
