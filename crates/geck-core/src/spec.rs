//! The `MissionSpec` model — the in-memory form of `mission-spec.md`.
//!
//! `mission-spec.md` is YAML frontmatter (machine-readable: harness, merge
//! mode, work branch, profile) followed by a markdown body (human-readable:
//! goal, success criteria, constraints, working agreement, backlog seeds).
//! The frontmatter is the single source of truth `geck prompt` re-parses to
//! regenerate `launch-prompt.md` without re-deriving the whole spec.

use std::fmt;
use std::str::FromStr;

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::frontmatter;

/// The agent runtime a launch prompt targets.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum Harness {
    ClaudeCode,
    CodexCli,
    OpenHarness,
    Antigravity,
}

impl fmt::Display for Harness {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let s = match self {
            Harness::ClaudeCode => "claude-code",
            Harness::CodexCli => "codex-cli",
            Harness::OpenHarness => "open-harness",
            Harness::Antigravity => "antigravity",
        };
        f.write_str(s)
    }
}

impl FromStr for Harness {
    type Err = SpecError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "claude-code" => Ok(Harness::ClaudeCode),
            "codex-cli" => Ok(Harness::CodexCli),
            "open-harness" => Ok(Harness::OpenHarness),
            "antigravity" => Ok(Harness::Antigravity),
            other => Err(SpecError::InvalidField {
                field: "harness",
                value: other.to_string(),
            }),
        }
    }
}

/// How a sprint's PR reaches `main` once CI is green.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "kebab-case")]
pub enum MergeMode {
    /// Human approves each sprint's PR.
    Approve,
    /// Merge on green CI proceeds autonomously.
    Auto,
}

impl fmt::Display for MergeMode {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(match self {
            MergeMode::Approve => "approve",
            MergeMode::Auto => "auto",
        })
    }
}

impl FromStr for MergeMode {
    type Err = SpecError;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        match s {
            "approve" => Ok(MergeMode::Approve),
            "auto" => Ok(MergeMode::Auto),
            other => Err(SpecError::InvalidField {
                field: "merge_mode",
                value: other.to_string(),
            }),
        }
    }
}

/// The machine-readable frontmatter block of `mission-spec.md`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpecFrontmatter {
    /// Spec format version (`geck-core::SPEC_VERSION` at write time).
    pub geck: String,
    pub project: String,
    pub created: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub profile: Option<String>,
    pub harness: Harness,
    pub merge_mode: MergeMode,
    pub work_branch: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub repo: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub sprint_loops_ref: Option<String>,
}

/// The full mission spec: frontmatter plus the body sections a human edits.
#[derive(Debug, Clone)]
pub struct MissionSpec {
    pub frontmatter: SpecFrontmatter,
    pub goal: String,
    pub success_criteria: Vec<String>,
    pub non_goals: Vec<String>,
    pub languages: Option<String>,
    pub frameworks: Vec<String>,
    pub platforms: Vec<String>,
    pub must_use: Option<String>,
    pub must_avoid: Option<String>,
    /// Extra stop-criterion checkpoints beyond SKILL.md's four, in prose.
    pub working_agreement_notes: Vec<String>,
    pub sprint_zero_charter: String,
    /// Rendered as `T-1xx (backlog)` entries in `agent-tasks.md`.
    pub backlog_seeds: Vec<String>,
}

#[derive(Debug, Error)]
pub enum SpecError {
    #[error("invalid value for {field}: {value}")]
    InvalidField { field: &'static str, value: String },
    #[error("mission-spec.md is missing required field: {0}")]
    MissingField(&'static str),
    #[error(transparent)]
    Frontmatter(#[from] frontmatter::FrontmatterError),
    #[error("failed to parse frontmatter YAML: {0}")]
    Yaml(#[from] serde_yaml::Error),
}

#[derive(Debug, Error)]
pub enum ValidationError {
    #[error("project name must not be empty")]
    EmptyProject,
    #[error("goal must not be empty")]
    EmptyGoal,
    #[error("work branch must not be empty")]
    EmptyWorkBranch,
}

/// Validate the fields that must be non-empty for the launcher to produce a
/// usable spec. Enum fields (harness, merge mode) are already constrained by
/// the type system at parse time.
pub fn validate(spec: &MissionSpec) -> Result<(), ValidationError> {
    if spec.frontmatter.project.trim().is_empty() {
        return Err(ValidationError::EmptyProject);
    }
    if spec.goal.trim().is_empty() {
        return Err(ValidationError::EmptyGoal);
    }
    if spec.frontmatter.work_branch.trim().is_empty() {
        return Err(ValidationError::EmptyWorkBranch);
    }
    Ok(())
}

/// Minimal source `geck prompt` needs to regenerate `launch-prompt.md` from
/// an on-disk `mission-spec.md` without reconstructing the full spec: the
/// frontmatter (authoritative) plus the Goal section (for the one-line
/// distillation in the prompt's invocation step).
#[derive(Debug, Clone)]
pub struct PromptSource {
    pub frontmatter: SpecFrontmatter,
    pub goal: String,
}

/// Parse just enough of an existing `mission-spec.md` to regenerate the
/// launch prompt: split frontmatter/body, deserialize the frontmatter, and
/// extract the `## Goal` section text.
pub fn load_for_prompt(document: &str) -> Result<PromptSource, SpecError> {
    let (yaml, body) = frontmatter::split(document)?;
    let frontmatter: SpecFrontmatter = serde_yaml::from_str(yaml)?;
    let goal = extract_section(body, "Goal").ok_or(SpecError::MissingField("Goal"))?;
    Ok(PromptSource { frontmatter, goal })
}

/// Extract the text of a `## <heading>` section: everything after the
/// heading line up to (but not including) the next `## ` heading or EOF,
/// trimmed. Returns `None` if the heading is absent.
pub fn extract_section(body: &str, heading: &str) -> Option<String> {
    let marker = format!("## {heading}");
    let start = body.find(&marker)? + marker.len();
    let rest = &body[start..];
    let end = rest.find("\n## ").unwrap_or(rest.len());
    Some(rest[..end].trim().to_string())
}

/// A one-line distillation of the goal for the launch prompt's invocation
/// line: the first sentence, or the first 120 characters if no sentence
/// boundary is found, whichever is shorter.
pub fn summarize_goal(goal: &str) -> String {
    let first_line = goal.lines().next().unwrap_or(goal).trim();
    let cut = first_line
        .find(". ")
        .map(|i| i + 1)
        .unwrap_or(first_line.len());
    let candidate = &first_line[..cut];
    if candidate.chars().count() <= 120 {
        candidate.trim_end_matches('.').to_string()
    } else {
        let truncated: String = candidate.chars().take(117).collect();
        format!("{}...", truncated.trim_end())
    }
}

/// Render the frontmatter block (`---\n...\n---\n`) for a spec.
pub fn render_frontmatter(fm: &SpecFrontmatter) -> Result<String, SpecError> {
    Ok(serde_yaml::to_string(fm)?)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample() -> MissionSpec {
        MissionSpec {
            frontmatter: SpecFrontmatter {
                geck: "2.0".into(),
                project: "Demo".into(),
                created: "2026-07-21".into(),
                profile: Some("cli_tool".into()),
                harness: Harness::ClaudeCode,
                merge_mode: MergeMode::Approve,
                work_branch: "dev".into(),
                repo: Some("https://github.com/x/demo".into()),
                sprint_loops_ref: Some("2026-07-21".into()),
            },
            goal: "Ship the thing. It should work well.".into(),
            success_criteria: vec!["passes tests".into()],
            non_goals: vec!["not a GUI".into()],
            languages: Some("Rust".into()),
            frameworks: vec![],
            platforms: vec!["Linux".into()],
            must_use: None,
            must_avoid: None,
            working_agreement_notes: vec![],
            sprint_zero_charter: "Research the existing X.".into(),
            backlog_seeds: vec!["wire up Y".into()],
        }
    }

    #[test]
    fn harness_roundtrips_through_display_and_fromstr() {
        for h in [
            Harness::ClaudeCode,
            Harness::CodexCli,
            Harness::OpenHarness,
            Harness::Antigravity,
        ] {
            assert_eq!(h.to_string().parse::<Harness>().unwrap(), h);
        }
    }

    #[test]
    fn merge_mode_roundtrips_through_display_and_fromstr() {
        for m in [MergeMode::Approve, MergeMode::Auto] {
            assert_eq!(m.to_string().parse::<MergeMode>().unwrap(), m);
        }
    }

    #[test]
    fn invalid_harness_errors() {
        assert!(matches!(
            "bogus".parse::<Harness>(),
            Err(SpecError::InvalidField { .. })
        ));
    }

    #[test]
    fn validate_rejects_empty_project() {
        let mut s = sample();
        s.frontmatter.project = "  ".into();
        assert!(matches!(validate(&s), Err(ValidationError::EmptyProject)));
    }

    #[test]
    fn validate_rejects_empty_goal() {
        let mut s = sample();
        s.goal = "".into();
        assert!(matches!(validate(&s), Err(ValidationError::EmptyGoal)));
    }

    #[test]
    fn validate_accepts_sample() {
        assert!(validate(&sample()).is_ok());
    }

    #[test]
    fn extract_section_finds_goal_between_headings() {
        let body = "\n## Goal\nShip it.\n\n## Success Criteria\n- [ ] a\n";
        assert_eq!(extract_section(body, "Goal").unwrap(), "Ship it.");
    }

    #[test]
    fn extract_section_handles_last_heading() {
        let body = "\n## Backlog Seeds\n- [ ] T-101 (backlog): x\n";
        assert_eq!(
            extract_section(body, "Backlog Seeds").unwrap(),
            "- [ ] T-101 (backlog): x"
        );
    }

    #[test]
    fn extract_section_missing_heading_is_none() {
        assert!(extract_section("## Goal\nx\n", "Nope").is_none());
    }

    #[test]
    fn summarize_goal_takes_first_sentence() {
        assert_eq!(
            summarize_goal("Ship the thing. It should work well."),
            "Ship the thing"
        );
    }

    #[test]
    fn summarize_goal_truncates_long_single_sentence() {
        let long = "x".repeat(200);
        let s = summarize_goal(&long);
        assert!(s.ends_with("..."));
        assert!(s.chars().count() <= 121);
    }

    #[test]
    fn frontmatter_roundtrips_through_yaml() {
        let spec = sample();
        let yaml = render_frontmatter(&spec.frontmatter).unwrap();
        let doc = frontmatter::join(&yaml, "\nbody\n");
        let parsed = load_for_prompt(&doc.replace("body\n", "## Goal\nShip the thing.\n")).unwrap();
        assert_eq!(parsed.frontmatter.project, "Demo");
        assert_eq!(parsed.frontmatter.harness, Harness::ClaudeCode);
        assert_eq!(parsed.frontmatter.merge_mode, MergeMode::Approve);
        assert_eq!(parsed.goal, "Ship the thing.");
    }
}
