//! Typed task records per GECK v1.3.
//!
//! Canonical line:
//!   `- [<state>] TASK-NNN | TYPE: <type> | SCOPE: <scope> | OWNER: <owner>`
//! followed by an optional nested description bullet:
//!   `  - <description>`
//!
//! States:
//!   - `[ ]` proposed
//!   - `[~]` active
//!   - `[!:reason]` blocked with reason
//!   - `[x]` completed

use std::fmt;
use std::str::FromStr;
use thiserror::Error;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TaskState {
    Proposed,
    Active,
    Blocked(String),
    Completed,
}

impl fmt::Display for TaskState {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TaskState::Proposed => f.write_str(" "),
            TaskState::Active => f.write_str("~"),
            TaskState::Blocked(reason) => write!(f, "!:{}", reason),
            TaskState::Completed => f.write_str("x"),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskType {
    Feature,
    Fix,
    Refactor,
    Research,
    Chore,
    Docs,
    Test,
}

impl fmt::Display for TaskType {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            TaskType::Feature => "feature",
            TaskType::Fix => "fix",
            TaskType::Refactor => "refactor",
            TaskType::Research => "research",
            TaskType::Chore => "chore",
            TaskType::Docs => "docs",
            TaskType::Test => "test",
        })
    }
}

impl FromStr for TaskType {
    type Err = ParseTaskError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "feature" => Ok(TaskType::Feature),
            "fix" => Ok(TaskType::Fix),
            "refactor" => Ok(TaskType::Refactor),
            "research" => Ok(TaskType::Research),
            "chore" => Ok(TaskType::Chore),
            "docs" => Ok(TaskType::Docs),
            "test" => Ok(TaskType::Test),
            other => Err(ParseTaskError::UnknownType(other.to_string())),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskScope {
    Small,
    Medium,
    Large,
}

impl fmt::Display for TaskScope {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            TaskScope::Small => "small",
            TaskScope::Medium => "medium",
            TaskScope::Large => "large",
        })
    }
}

impl FromStr for TaskScope {
    type Err = ParseTaskError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "small" => Ok(TaskScope::Small),
            "medium" => Ok(TaskScope::Medium),
            "large" => Ok(TaskScope::Large),
            other => Err(ParseTaskError::UnknownScope(other.to_string())),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum TaskOwner {
    Agent,
    Human,
}

impl fmt::Display for TaskOwner {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            TaskOwner::Agent => "agent",
            TaskOwner::Human => "human",
        })
    }
}

impl FromStr for TaskOwner {
    type Err = ParseTaskError;
    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "agent" => Ok(TaskOwner::Agent),
            "human" => Ok(TaskOwner::Human),
            other => Err(ParseTaskError::UnknownOwner(other.to_string())),
        }
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Task {
    pub id: u32,
    pub state: TaskState,
    pub kind: TaskType,
    pub scope: TaskScope,
    pub owner: TaskOwner,
    pub description: Option<String>,
}

impl fmt::Display for Task {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "- [{}] TASK-{:03} | TYPE: {} | SCOPE: {} | OWNER: {}",
            self.state, self.id, self.kind, self.scope, self.owner
        )?;
        if let Some(desc) = &self.description {
            write!(f, "\n  - {}", desc)?;
        }
        Ok(())
    }
}

#[derive(Debug, Error, PartialEq, Eq)]
pub enum ParseTaskError {
    #[error("task block is empty")]
    Empty,
    #[error("missing `- [` prefix")]
    MissingPrefix,
    #[error("missing closing `]` on state")]
    UnterminatedState,
    #[error("malformed task line: {0}")]
    Malformed(String),
    #[error("missing field: {0}")]
    MissingField(&'static str),
    #[error("unknown TYPE: {0}")]
    UnknownType(String),
    #[error("unknown SCOPE: {0}")]
    UnknownScope(String),
    #[error("unknown OWNER: {0}")]
    UnknownOwner(String),
    #[error("invalid TASK id: {0}")]
    InvalidId(String),
}

/// Parse a task block: the header line plus an optional nested description line.
///
/// Accepts lines separated by `\n`. Trailing whitespace on each line is trimmed.
pub fn parse_task_block(block: &str) -> Result<Task, ParseTaskError> {
    let mut lines = block.lines();
    let header = lines.next().ok_or(ParseTaskError::Empty)?.trim_end();
    let task = parse_header(header)?;

    let description = lines
        .map(str::trim_end)
        .find(|l| !l.is_empty())
        .map(|l| {
            let stripped = l.trim_start();
            stripped
                .strip_prefix("- ")
                .or_else(|| stripped.strip_prefix("-"))
                .unwrap_or(stripped)
                .trim()
                .to_string()
        })
        .filter(|s| !s.is_empty());

    Ok(Task { description, ..task })
}

fn parse_header(line: &str) -> Result<Task, ParseTaskError> {
    let rest = line
        .trim_start()
        .strip_prefix("- [")
        .ok_or(ParseTaskError::MissingPrefix)?;
    let close = rest.find(']').ok_or(ParseTaskError::UnterminatedState)?;
    let (state_raw, tail) = (&rest[..close], &rest[close + 1..]);
    let state = parse_state(state_raw)?;

    let mut fields = tail.split('|').map(str::trim);
    let id_field = fields
        .next()
        .ok_or(ParseTaskError::MissingField("TASK-NNN"))?;
    let id = id_field
        .strip_prefix("TASK-")
        .ok_or_else(|| ParseTaskError::Malformed(format!("expected TASK-NNN, got {id_field:?}")))?
        .parse::<u32>()
        .map_err(|_| ParseTaskError::InvalidId(id_field.to_string()))?;

    let kind = parse_kv(fields.next(), "TYPE")?.parse()?;
    let scope = parse_kv(fields.next(), "SCOPE")?.parse()?;
    let owner = parse_kv(fields.next(), "OWNER")?.parse()?;

    Ok(Task {
        id,
        state,
        kind,
        scope,
        owner,
        description: None,
    })
}

fn parse_state(raw: &str) -> Result<TaskState, ParseTaskError> {
    match raw {
        " " | "" => Ok(TaskState::Proposed),
        "~" => Ok(TaskState::Active),
        "x" | "X" => Ok(TaskState::Completed),
        other => {
            if let Some(reason) = other.strip_prefix("!:") {
                Ok(TaskState::Blocked(reason.trim().to_string()))
            } else if other == "!" {
                Ok(TaskState::Blocked(String::new()))
            } else {
                Err(ParseTaskError::Malformed(format!("state {other:?}")))
            }
        }
    }
}

fn parse_kv<'a>(field: Option<&'a str>, key: &'static str) -> Result<&'a str, ParseTaskError> {
    let field = field.ok_or(ParseTaskError::MissingField(key))?;
    let prefix = format!("{key}:");
    field
        .strip_prefix(&prefix)
        .map(str::trim)
        .ok_or_else(|| ParseTaskError::Malformed(format!("expected `{key}: ...`, got {field:?}")))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_canonical_proposed_task() {
        let block = "- [ ] TASK-001 | TYPE: feature | SCOPE: medium | OWNER: agent\n  - Draft proposal";
        let task = parse_task_block(block).unwrap();
        assert_eq!(task.id, 1);
        assert_eq!(task.state, TaskState::Proposed);
        assert_eq!(task.kind, TaskType::Feature);
        assert_eq!(task.scope, TaskScope::Medium);
        assert_eq!(task.owner, TaskOwner::Agent);
        assert_eq!(task.description.as_deref(), Some("Draft proposal"));
    }

    #[test]
    fn parse_active_and_completed() {
        let active = parse_task_block("- [~] TASK-042 | TYPE: fix | SCOPE: small | OWNER: human").unwrap();
        assert_eq!(active.state, TaskState::Active);
        assert_eq!(active.id, 42);
        assert_eq!(active.description, None);

        let done = parse_task_block("- [x] TASK-999 | TYPE: chore | SCOPE: large | OWNER: agent").unwrap();
        assert_eq!(done.state, TaskState::Completed);
        assert_eq!(done.id, 999);
    }

    #[test]
    fn parse_blocked_with_reason() {
        let task = parse_task_block(
            "- [!:waiting on API access] TASK-007 | TYPE: research | SCOPE: small | OWNER: agent",
        )
        .unwrap();
        assert_eq!(task.state, TaskState::Blocked("waiting on API access".into()));
    }

    #[test]
    fn display_roundtrip() {
        let block = "- [ ] TASK-003 | TYPE: docs | SCOPE: small | OWNER: human\n  - Update README";
        let task = parse_task_block(block).unwrap();
        assert_eq!(task.to_string(), block);
    }

    #[test]
    fn display_roundtrip_blocked() {
        let block = "- [!:needs review] TASK-010 | TYPE: refactor | SCOPE: medium | OWNER: agent";
        let task = parse_task_block(block).unwrap();
        assert_eq!(task.to_string(), block);
    }

    #[test]
    fn rejects_unknown_type() {
        let err = parse_task_block("- [ ] TASK-001 | TYPE: invalid | SCOPE: small | OWNER: agent")
            .unwrap_err();
        assert_eq!(err, ParseTaskError::UnknownType("invalid".into()));
    }

    #[test]
    fn rejects_malformed_prefix() {
        let err = parse_task_block("[ ] TASK-001 | TYPE: feature | SCOPE: small | OWNER: agent")
            .unwrap_err();
        assert_eq!(err, ParseTaskError::MissingPrefix);
    }
}
