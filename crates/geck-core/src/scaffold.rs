//! Writes `mission-spec.md` + `launch-prompt.md` and seeds the target
//! project's Sprint Loops state (`decisions.md` ADR-000, backlog seeds in
//! `agent-tasks/agent-tasks.md`, `confidence.txt`).
//!
//! Seeding is idempotent: re-running `launch_project` on an already-launched
//! project never duplicates ADR-000 or a backlog line, and never touches
//! `sprints/` — that directory belongs to the Sprint Loops protocol, not
//! GECK.

use std::fs;
use std::io;
use std::path::{Path, PathBuf};
use std::process::Command;

use chrono::Local;
use tera::Context;
use thiserror::Error;

use crate::spec::{summarize_goal, MissionSpec};
use crate::templates::{TemplateEngine, TemplateError};

/// Marker substring identifying an already-adopted mission spec ADR. Kept in
/// sync with the literal title text `adr_000.tera` renders.
const ADR_000_MARKER: &str = "Mission spec adopted: mission-spec.md is the drift baseline";

/// Injected environment facts. [`detect_environment`] fills this from the
/// host; callers pass their own for deterministic tests.
#[derive(Debug, Clone, Default)]
pub struct EnvInfo {
    /// ISO-8601 date ("YYYY-MM-DD") used as the spec's `created` field and
    /// the ADR-000 date.
    pub created_date: String,
    /// `git remote get-url origin`, if the project is a git repo with one.
    pub git_remote: Option<String>,
    /// `git rev-parse --abbrev-ref HEAD`, if the project is a git repo.
    pub git_branch: Option<String>,
}

#[derive(Debug, Error)]
pub enum ScaffoldError {
    #[error("template error: {0}")]
    Template(#[from] TemplateError),
    #[error("I/O error at {path}: {source}")]
    Io {
        path: PathBuf,
        #[source]
        source: io::Error,
    },
}

/// A single backlog seed with its assigned `T-1xx` id and whether it was
/// newly appended to `agent-tasks.md` (vs. already present from a prior run).
#[derive(Debug, Clone)]
pub struct BacklogSeed {
    pub id: u32,
    pub description: String,
    pub already_present: bool,
}

/// What [`seed_project`] actually wrote, for the CLI to summarize.
#[derive(Debug, Clone, Default)]
pub struct SeedReport {
    pub decisions_written: bool,
    pub backlog_written: Vec<BacklogSeed>,
    pub backlog_skipped: Vec<BacklogSeed>,
    pub confidence_written: bool,
}

/// Everything [`launch_project`] wrote.
#[derive(Debug, Clone)]
pub struct LaunchReport {
    pub spec_path: PathBuf,
    pub prompt_path: PathBuf,
    pub seed: SeedReport,
}

/// Snapshot git + date facts for scaffolding. Best-effort: a missing `git`
/// binary, a non-repo `project_path`, or `project_path` merely being nested
/// somewhere *under* an ambient parent repo (rather than being that repo's
/// own root) all leave the git fields `None` — git's directory-upward search
/// would otherwise attribute an unrelated ancestor repo's remote to a
/// brand-new, not-yet-`git init`'d project directory.
pub fn detect_environment(project_path: &Path) -> EnvInfo {
    let is_repo_root = git_output(project_path, &["rev-parse", "--show-toplevel"])
        .map(PathBuf::from)
        .and_then(|toplevel| {
            Some((
                toplevel.canonicalize().ok()?,
                project_path.canonicalize().ok()?,
            ))
        })
        .is_some_and(|(toplevel, project)| toplevel == project);

    if !is_repo_root {
        return EnvInfo {
            created_date: today(),
            git_remote: None,
            git_branch: None,
        };
    }

    EnvInfo {
        created_date: today(),
        git_remote: git_output(project_path, &["remote", "get-url", "origin"]),
        git_branch: git_output(project_path, &["rev-parse", "--abbrev-ref", "HEAD"])
            .filter(|b| b != "HEAD"),
    }
}

/// Today's date as `YYYY-MM-DD`, for callers that need it without a full
/// [`EnvInfo`] (e.g. the wizard's live preview, which shouldn't shell out to
/// git on every keystroke-equivalent render).
pub fn today() -> String {
    Local::now().format("%Y-%m-%d").to_string()
}

fn git_output(project_path: &Path, args: &[&str]) -> Option<String> {
    let out = Command::new("git")
        .args(args)
        .current_dir(project_path)
        .output()
        .ok()?;
    if !out.status.success() {
        return None;
    }
    let s = String::from_utf8(out.stdout).ok()?.trim().to_string();
    if s.is_empty() {
        None
    } else {
        Some(s)
    }
}

/// Assign stable `T-1xx` ids to a set of backlog seed descriptions, given
/// the current contents of `agent-tasks.md` (empty string if the file
/// doesn't exist yet). Descriptions already present verbatim in `existing`
/// are matched to their prior id and marked `already_present`; new
/// descriptions get the next id after the highest `T-1xx` id found.
pub fn assign_backlog_ids(descriptions: &[String], existing: &str) -> Vec<BacklogSeed> {
    let mut next_id = existing
        .lines()
        .filter_map(|line| {
            let idx = line.find("T-1")?;
            let digits: String = line[idx + 2..]
                .chars()
                .take_while(|c| c.is_ascii_digit())
                .collect();
            digits.parse::<u32>().ok()
        })
        .max()
        .map(|max| max + 1)
        .unwrap_or(101);

    descriptions
        .iter()
        .map(|description| {
            let already_present = existing.contains(description.as_str());
            let id = if already_present {
                find_existing_id(existing, description).unwrap_or(next_id)
            } else {
                let assigned = next_id;
                next_id += 1;
                assigned
            };
            BacklogSeed {
                id,
                description: description.clone(),
                already_present,
            }
        })
        .collect()
}

fn find_existing_id(existing: &str, description: &str) -> Option<u32> {
    let line = existing.lines().find(|l| l.contains(description))?;
    let idx = line.find("T-1")?;
    let digits: String = line[idx + 2..]
        .chars()
        .take_while(|c| c.is_ascii_digit())
        .collect();
    digits.parse().ok()
}

/// Render the full `mission-spec.md` document (frontmatter + body) as a
/// string, without writing anything — used both by [`write_spec`] and by
/// callers that want to preview the artifact before saving.
pub fn render_spec_document(
    spec: &MissionSpec,
    backlog_seeds: &[BacklogSeed],
) -> Result<String, ScaffoldError> {
    let engine = TemplateEngine::new();
    let frontmatter_yaml =
        crate::spec::render_frontmatter(&spec.frontmatter).map_err(|e| ScaffoldError::Io {
            path: PathBuf::from("mission-spec.md"),
            source: io::Error::new(io::ErrorKind::InvalidData, e.to_string()),
        })?;
    let body = engine.render("mission_spec", &mission_spec_context(spec, backlog_seeds))?;
    Ok(crate::frontmatter::join(
        &frontmatter_yaml,
        body.trim_start_matches('\n'),
    ))
}

/// Render `mission-spec.md` (frontmatter + body) and write it to
/// `project_path/mission-spec.md`.
pub fn write_spec(
    project_path: &Path,
    spec: &MissionSpec,
    backlog_seeds: &[BacklogSeed],
) -> Result<PathBuf, ScaffoldError> {
    let path = project_path.join("mission-spec.md");
    let document = render_spec_document(spec, backlog_seeds)?;
    fs::write(&path, document).map_err(|source| ScaffoldError::Io {
        path: path.clone(),
        source,
    })?;
    Ok(path)
}

fn mission_spec_context(spec: &MissionSpec, backlog_seeds: &[BacklogSeed]) -> Context {
    let mut ctx = Context::new();
    ctx.insert("project_name", &spec.frontmatter.project);
    ctx.insert("goal", &spec.goal);
    ctx.insert("success_criteria", &spec.success_criteria);
    ctx.insert("non_goals", &spec.non_goals);
    ctx.insert("languages", &spec.languages);
    ctx.insert("frameworks", &spec.frameworks);
    ctx.insert("platforms", &spec.platforms);
    ctx.insert("must_use", &spec.must_use);
    ctx.insert("must_avoid", &spec.must_avoid);
    ctx.insert("merge_mode", &spec.frontmatter.merge_mode.to_string());
    ctx.insert("work_branch", &spec.frontmatter.work_branch);
    ctx.insert("working_agreement_notes", &spec.working_agreement_notes);
    ctx.insert("sprint_zero_charter", &spec.sprint_zero_charter);
    let formatted: Vec<String> = backlog_seeds
        .iter()
        .map(|s| format!("T-{} (backlog): {}", s.id, s.description))
        .collect();
    ctx.insert("backlog_seeds", &formatted);
    ctx
}

/// Render `launch-prompt.md` as a string, without writing anything.
pub fn render_prompt(spec: &MissionSpec) -> Result<String, ScaffoldError> {
    let engine = TemplateEngine::new();
    Ok(engine.render("launch_prompt", &launch_prompt_context(spec, &spec.goal))?)
}

/// Render `launch-prompt.md` and write it to `project_path/launch-prompt.md`.
pub fn write_prompt(project_path: &Path, spec: &MissionSpec) -> Result<PathBuf, ScaffoldError> {
    let path = project_path.join("launch-prompt.md");
    let rendered = render_prompt(spec)?;
    fs::write(&path, rendered).map_err(|source| ScaffoldError::Io {
        path: path.clone(),
        source,
    })?;
    Ok(path)
}

/// Render the launch prompt to a string without writing it (used by
/// `geck prompt`, which reconstructs only `PromptSource` from an existing
/// spec rather than a full [`MissionSpec`]).
pub fn render_prompt_from_frontmatter(
    frontmatter: &crate::spec::SpecFrontmatter,
    goal: &str,
) -> Result<String, ScaffoldError> {
    let engine = TemplateEngine::new();
    let mut ctx = Context::new();
    ctx.insert("project_name", &frontmatter.project);
    ctx.insert("harness", &frontmatter.harness.to_string());
    ctx.insert("goal_summary", &summarize_goal(goal));
    ctx.insert("work_branch", &frontmatter.work_branch);
    ctx.insert("merge_mode", &frontmatter.merge_mode.to_string());
    ctx.insert(
        "sprint_loops_ref",
        frontmatter.sprint_loops_ref.as_deref().unwrap_or("unknown"),
    );
    Ok(engine.render("launch_prompt", &ctx)?)
}

fn launch_prompt_context(spec: &MissionSpec, goal: &str) -> Context {
    let mut ctx = Context::new();
    ctx.insert("project_name", &spec.frontmatter.project);
    ctx.insert("harness", &spec.frontmatter.harness.to_string());
    ctx.insert("goal_summary", &summarize_goal(goal));
    ctx.insert("work_branch", &spec.frontmatter.work_branch);
    ctx.insert("merge_mode", &spec.frontmatter.merge_mode.to_string());
    ctx.insert(
        "sprint_loops_ref",
        spec.frontmatter
            .sprint_loops_ref
            .as_deref()
            .unwrap_or("unknown"),
    );
    ctx
}

/// Idempotently seed `decisions.md`, `agent-tasks/agent-tasks.md`, and
/// `confidence.txt` at `project_path`. Never touches `sprints/`.
pub fn seed_project(
    project_path: &Path,
    backlog_seeds: &[BacklogSeed],
    env: &EnvInfo,
) -> Result<SeedReport, ScaffoldError> {
    let mut report = SeedReport::default();
    let engine = TemplateEngine::new();

    // decisions.md — append ADR-000 once.
    let decisions_path = project_path.join("decisions.md");
    let existing_decisions = fs::read_to_string(&decisions_path).unwrap_or_default();
    if !existing_decisions.contains(ADR_000_MARKER) {
        let mut ctx = Context::new();
        ctx.insert("date", &env.created_date);
        let adr = engine.render("adr_000", &ctx)?;
        let mut content = if existing_decisions.is_empty() {
            "# Architectural Decisions\n\n".to_string()
        } else {
            let mut s = existing_decisions;
            if !s.ends_with('\n') {
                s.push('\n');
            }
            s.push('\n');
            s
        };
        content.push_str(&adr);
        fs::write(&decisions_path, content).map_err(|source| ScaffoldError::Io {
            path: decisions_path.clone(),
            source,
        })?;
        report.decisions_written = true;
    }

    // agent-tasks/agent-tasks.md — append only the seeds not already present.
    let agent_tasks_dir = project_path.join("agent-tasks");
    let agent_tasks_path = agent_tasks_dir.join("agent-tasks.md");
    fs::create_dir_all(&agent_tasks_dir).map_err(|source| ScaffoldError::Io {
        path: agent_tasks_dir.clone(),
        source,
    })?;
    let existing_tasks = fs::read_to_string(&agent_tasks_path).unwrap_or_default();
    let mut tasks_content = if existing_tasks.is_empty() {
        "# Agent Tasks (Persistent Backlog)\n\n".to_string()
    } else {
        existing_tasks
    };
    for seed in backlog_seeds {
        if seed.already_present {
            report.backlog_skipped.push(seed.clone());
            continue;
        }
        let mut ctx = Context::new();
        ctx.insert("id", &seed.id.to_string());
        ctx.insert("description", &seed.description);
        let line = engine.render("backlog_seed", &ctx)?;
        if !tasks_content.ends_with('\n') {
            tasks_content.push('\n');
        }
        tasks_content.push_str(&line);
        report.backlog_written.push(seed.clone());
    }
    fs::write(&agent_tasks_path, tasks_content).map_err(|source| ScaffoldError::Io {
        path: agent_tasks_path.clone(),
        source,
    })?;

    // completed-tasks.md — create if missing (Sprint Loops expects the pair).
    let completed_path = agent_tasks_dir.join("completed-tasks.md");
    if !completed_path.is_file() {
        fs::write(&completed_path, "# Completed Tasks Log (Append-Only)\n").map_err(|source| {
            ScaffoldError::Io {
                path: completed_path.clone(),
                source,
            }
        })?;
    }

    // confidence.txt — create at 1.0 if missing.
    let confidence_path = project_path.join("confidence.txt");
    if !confidence_path.is_file() {
        fs::write(&confidence_path, "1.0").map_err(|source| ScaffoldError::Io {
            path: confidence_path.clone(),
            source,
        })?;
        report.confidence_written = true;
    }

    Ok(report)
}

/// The full `geck launch` flow: write the spec, seed the project, write the
/// prompt. Backlog ids are assigned once (against the current
/// `agent-tasks.md`) and shared by the spec body and the seeded file so
/// both artifacts agree on `T-1xx` numbering.
pub fn launch_project(
    project_path: &Path,
    spec: &MissionSpec,
) -> Result<LaunchReport, ScaffoldError> {
    let env = detect_environment(project_path);
    let existing_tasks =
        fs::read_to_string(project_path.join("agent-tasks").join("agent-tasks.md"))
            .unwrap_or_default();
    let backlog_seeds = assign_backlog_ids(&spec.backlog_seeds, &existing_tasks);

    let spec_path = write_spec(project_path, spec, &backlog_seeds)?;
    let seed = seed_project(project_path, &backlog_seeds, &env)?;
    let prompt_path = write_prompt(project_path, spec)?;

    Ok(LaunchReport {
        spec_path,
        prompt_path,
        seed,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::spec::{Harness, MergeMode, SpecFrontmatter};

    fn tmpdir() -> PathBuf {
        let mut p = std::env::temp_dir();
        p.push(format!(
            "geck-scaffold-{}-{}",
            std::process::id(),
            chrono::Local::now().timestamp_nanos_opt().unwrap_or(0),
        ));
        fs::create_dir_all(&p).unwrap();
        p
    }

    #[test]
    fn detect_environment_reports_remote_at_repo_root() {
        let root = tmpdir();
        Command::new("git")
            .args(["init", "-q"])
            .current_dir(&root)
            .status()
            .unwrap();
        Command::new("git")
            .args(["remote", "add", "origin", "https://example.com/x.git"])
            .current_dir(&root)
            .status()
            .unwrap();

        let env = detect_environment(&root);
        assert_eq!(env.git_remote.as_deref(), Some("https://example.com/x.git"));

        fs::remove_dir_all(&root).ok();
    }

    #[test]
    fn detect_environment_ignores_ambient_parent_repo_remote() {
        // Regression test: a fresh, not-yet-`git init`'d subdirectory nested
        // under an unrelated ancestor repo must NOT inherit that ancestor's
        // remote — git's directory-upward search would otherwise attribute
        // it, silently mislabeling the new project's mission-spec.md.
        let root = tmpdir();
        Command::new("git")
            .args(["init", "-q"])
            .current_dir(&root)
            .status()
            .unwrap();
        Command::new("git")
            .args([
                "remote",
                "add",
                "origin",
                "https://example.com/unrelated-ancestor.git",
            ])
            .current_dir(&root)
            .status()
            .unwrap();

        let nested = root.join("not-yet-a-repo").join("new-project");
        fs::create_dir_all(&nested).unwrap();

        let env = detect_environment(&nested);
        assert_eq!(env.git_remote, None);
        assert_eq!(env.git_branch, None);

        fs::remove_dir_all(&root).ok();
    }

    fn sample_spec() -> MissionSpec {
        MissionSpec {
            frontmatter: SpecFrontmatter {
                geck: "2.0".into(),
                project: "Demo".into(),
                created: "2026-07-21".into(),
                profile: Some("cli_tool".into()),
                harness: Harness::ClaudeCode,
                merge_mode: MergeMode::Approve,
                work_branch: "dev".into(),
                repo: None,
                sprint_loops_ref: Some("2026-07-21".into()),
            },
            goal: "Ship the thing. It should work well.".into(),
            success_criteria: vec!["passes tests".into()],
            non_goals: vec![],
            languages: Some("Rust".into()),
            frameworks: vec![],
            platforms: vec!["Linux".into()],
            must_use: None,
            must_avoid: None,
            working_agreement_notes: vec![],
            sprint_zero_charter: "Research the existing X.".into(),
            backlog_seeds: vec!["wire up Y".into(), "wire up Z".into()],
        }
    }

    #[test]
    fn assign_backlog_ids_starts_at_101_when_empty() {
        let seeds = assign_backlog_ids(&["a".into(), "b".into()], "");
        assert_eq!(seeds[0].id, 101);
        assert_eq!(seeds[1].id, 102);
        assert!(!seeds[0].already_present);
    }

    #[test]
    fn assign_backlog_ids_continues_after_existing_max() {
        let existing = "- [ ] T-101 (backlog): old one — touches: TBD\n";
        let seeds = assign_backlog_ids(&["new one".into()], existing);
        assert_eq!(seeds[0].id, 102);
    }

    #[test]
    fn assign_backlog_ids_matches_existing_description() {
        let existing = "- [ ] T-105 (backlog): already here — touches: TBD\n";
        let seeds = assign_backlog_ids(&["already here".into()], existing);
        assert_eq!(seeds[0].id, 105);
        assert!(seeds[0].already_present);
    }

    #[test]
    fn launch_project_writes_spec_prompt_and_seeds() {
        let root = tmpdir();
        let report = launch_project(&root, &sample_spec()).unwrap();

        assert!(report.spec_path.is_file());
        assert!(report.prompt_path.is_file());
        assert!(root.join("decisions.md").is_file());
        assert!(root.join("agent-tasks/agent-tasks.md").is_file());
        assert!(root.join("agent-tasks/completed-tasks.md").is_file());
        assert!(root.join("confidence.txt").is_file());
        assert_eq!(
            fs::read_to_string(root.join("confidence.txt")).unwrap(),
            "1.0"
        );

        let spec_body = fs::read_to_string(&report.spec_path).unwrap();
        assert!(spec_body.starts_with("---\n"));
        assert!(spec_body.contains("project: Demo"));
        assert!(spec_body.contains("# Mission: Demo"));
        assert!(spec_body.contains("T-101 (backlog): wire up Y"));

        let prompt = fs::read_to_string(&report.prompt_path).unwrap();
        assert!(prompt.contains("/sprint-loop start \"Ship the thing"));

        let decisions = fs::read_to_string(root.join("decisions.md")).unwrap();
        assert!(decisions.contains(ADR_000_MARKER));

        let tasks = fs::read_to_string(root.join("agent-tasks/agent-tasks.md")).unwrap();
        assert!(tasks.contains("T-101 (backlog): wire up Y"));
        assert!(tasks.contains("T-102 (backlog): wire up Z"));

        fs::remove_dir_all(&root).ok();
    }

    #[test]
    fn launch_project_is_idempotent_on_second_run() {
        let root = tmpdir();
        launch_project(&root, &sample_spec()).unwrap();
        let decisions_first = fs::read_to_string(root.join("decisions.md")).unwrap();
        let tasks_first = fs::read_to_string(root.join("agent-tasks/agent-tasks.md")).unwrap();
        let confidence_first = fs::read_to_string(root.join("confidence.txt")).unwrap();

        let second = launch_project(&root, &sample_spec()).unwrap();
        assert!(!second.seed.decisions_written);
        assert_eq!(second.seed.backlog_skipped.len(), 2);
        assert!(second.seed.backlog_written.is_empty());
        assert!(!second.seed.confidence_written);

        let decisions_second = fs::read_to_string(root.join("decisions.md")).unwrap();
        let tasks_second = fs::read_to_string(root.join("agent-tasks/agent-tasks.md")).unwrap();
        let confidence_second = fs::read_to_string(root.join("confidence.txt")).unwrap();
        assert_eq!(decisions_first, decisions_second);
        assert_eq!(tasks_first, tasks_second);
        assert_eq!(confidence_first, confidence_second);

        fs::remove_dir_all(&root).ok();
    }

    #[test]
    fn seed_project_preserves_existing_decisions_content() {
        let root = tmpdir();
        fs::write(
            root.join("decisions.md"),
            "# Architectural Decisions\n\n## 2026-01-01 — prior decision (sprint 0)\n- **Context:** x\n",
        )
        .unwrap();
        let env = EnvInfo {
            created_date: "2026-07-21".into(),
            git_remote: None,
            git_branch: None,
        };
        seed_project(&root, &[], &env).unwrap();
        let content = fs::read_to_string(root.join("decisions.md")).unwrap();
        assert!(content.contains("prior decision"));
        assert!(content.contains(ADR_000_MARKER));
        fs::remove_dir_all(&root).ok();
    }
}
