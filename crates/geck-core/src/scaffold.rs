//! GECK folder scaffold — parity with the Python `init_geck_folder`.
//!
//! Given a project root and an [`InitConfig`], creates the `GECK/` tree:
//! `LLM_init.md`, `GECK_Inst.md`, `env.md`, `tasks.md`, `log.md`,
//! `log_index.jsonl`, `decisions.md`, `decisions/`, `learnings.md`,
//! `learnings/`, `log_archive/`.

use std::collections::BTreeMap;
use std::fs;
use std::io;
use std::path::{Path, PathBuf};

use chrono::Local;
use tera::Context;
use thiserror::Error;

use crate::templates::{TemplateEngine, TemplateError};

pub const DEFAULT_CONTEXT_BUDGET: &str = "medium";
pub const DEFAULT_INITIAL_TASK: &str = "Compile task list from log and LLM_init entries";
pub const ALL_PLATFORMS: &[&str] = &[
    "Windows", "macOS", "Linux", "Docker", "iOS", "Android", "Web",
];

/// Configuration passed to [`init_geck_folder`].
///
/// Mirrors the Python config dict. Every field is optional; defaults fill in
/// during scaffolding.
#[derive(Debug, Clone, Default)]
pub struct InitConfig {
    pub project_name: Option<String>,
    pub repo_url: Option<String>,
    pub local_path: Option<String>,
    pub git_branch: Option<String>,
    pub goal: Option<String>,
    pub success_criteria: Vec<String>,
    pub languages: Option<String>,
    pub frameworks: Vec<String>,
    pub must_use: Option<String>,
    pub must_avoid: Option<String>,
    pub platforms: Vec<String>,
    pub context: Option<String>,
    pub initial_task: Option<String>,
    pub context_budget: Option<String>,
}

/// Injected environment facts. [`detect_environment`] fills this from the host;
/// callers pass their own for deterministic tests.
#[derive(Debug, Clone)]
pub struct EnvInfo {
    pub os_info: String,
    pub shell_info: String,
    pub runtime_versions: BTreeMap<String, String>,
    /// Human-readable timestamp ("YYYY-MM-DD HH:MM:SS"). Used in markdown.
    pub timestamp: String,
    /// ISO-8601 timestamp used in `log_index.jsonl`.
    pub iso_timestamp: String,
    /// Date stamp ("YYYY-MM-DD") used in the LLM_init header.
    pub created_date: String,
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

/// Create the GECK v1.3 folder tree under `project_path` and return the path
/// to the new `GECK/` folder.
pub fn init_geck_folder(
    project_path: &Path,
    config: &InitConfig,
    env: &EnvInfo,
) -> Result<PathBuf, ScaffoldError> {
    let engine = TemplateEngine::new();
    let geck = project_path.join("GECK");

    for sub in ["", "decisions", "learnings", "log_archive"] {
        let p = if sub.is_empty() { geck.clone() } else { geck.join(sub) };
        fs::create_dir_all(&p).map_err(|source| ScaffoldError::Io { path: p, source })?;
    }

    let project_name = config
        .project_name
        .clone()
        .unwrap_or_else(|| "Untitled Project".to_string());
    let goal = config.goal.clone().unwrap_or_else(|| "No goal specified.".to_string());
    let context_budget = config
        .context_budget
        .clone()
        .unwrap_or_else(|| DEFAULT_CONTEXT_BUDGET.to_string());

    let initial_tasks = derive_initial_tasks(config);

    write_rendered(
        &engine,
        "llm_init",
        &llm_init_context(config, &project_name, &goal, &context_budget, &env.created_date),
        &geck.join("LLM_init.md"),
    )?;

    write_rendered(&engine, "geck_inst", &Context::new(), &geck.join("GECK_Inst.md"))?;

    write_rendered(
        &engine,
        "env",
        &env_context(&project_name, env, &config.platforms),
        &geck.join("env.md"),
    )?;

    let mut tasks_ctx = Context::new();
    tasks_ctx.insert("project_name", &project_name);
    tasks_ctx.insert("timestamp", &env.timestamp);
    tasks_ctx.insert("initial_tasks", &initial_tasks);
    write_rendered(&engine, "tasks", &tasks_ctx, &geck.join("tasks.md"))?;

    let mut log_ctx = Context::new();
    log_ctx.insert("project_name", &project_name);
    log_ctx.insert("timestamp", &env.timestamp);
    write_rendered(&engine, "log", &log_ctx, &geck.join("log.md"))?;

    let mut log_index_ctx = Context::new();
    log_index_ctx.insert("timestamp", &env.iso_timestamp);
    write_rendered(&engine, "log_index", &log_index_ctx, &geck.join("log_index.jsonl"))?;

    let mut idx_ctx = Context::new();
    idx_ctx.insert("project_name", &project_name);
    write_rendered(&engine, "decisions_index", &idx_ctx, &geck.join("decisions.md"))?;
    write_rendered(&engine, "learnings_index", &idx_ctx, &geck.join("learnings.md"))?;

    Ok(geck)
}

fn write_rendered(
    engine: &TemplateEngine,
    name: &str,
    ctx: &Context,
    path: &Path,
) -> Result<(), ScaffoldError> {
    let body = engine.render(name, ctx)?;
    fs::write(path, body).map_err(|source| ScaffoldError::Io {
        path: path.to_path_buf(),
        source,
    })
}

fn llm_init_context(
    config: &InitConfig,
    project_name: &str,
    goal: &str,
    context_budget: &str,
    created_date: &str,
) -> Context {
    let mut ctx = Context::new();
    ctx.insert("project_name", project_name);
    ctx.insert("goal", goal);
    ctx.insert("context_budget", context_budget);
    ctx.insert("created_date", created_date);
    ctx.insert("success_criteria", &config.success_criteria);
    ctx.insert("frameworks", &config.frameworks);
    ctx.insert("platforms", &config.platforms);
    if let Some(v) = &config.repo_url {
        ctx.insert("repo_url", v);
    }
    if let Some(v) = &config.local_path {
        ctx.insert("local_path", v);
    }
    if let Some(v) = &config.git_branch {
        ctx.insert("git_branch", v);
    }
    if let Some(v) = &config.languages {
        ctx.insert("languages", v);
    }
    if let Some(v) = &config.must_use {
        ctx.insert("must_use", v);
    }
    if let Some(v) = &config.must_avoid {
        ctx.insert("must_avoid", v);
    }
    if let Some(v) = &config.context {
        ctx.insert("context", v);
    }
    if let Some(v) = &config.initial_task {
        ctx.insert("initial_task", v);
    }
    ctx
}

fn env_context(project_name: &str, env: &EnvInfo, target_platforms: &[String]) -> Context {
    let mut ctx = Context::new();
    ctx.insert("project_name", project_name);
    ctx.insert("timestamp", &env.timestamp);
    ctx.insert("os_info", &env.os_info);
    ctx.insert("shell_info", &env.shell_info);
    ctx.insert("runtime_versions", &env.runtime_versions);
    ctx.insert("all_platforms", ALL_PLATFORMS);
    ctx.insert("target_platforms", target_platforms);
    ctx
}

fn derive_initial_tasks(config: &InitConfig) -> Vec<String> {
    let mut tasks = vec![DEFAULT_INITIAL_TASK.to_string()];
    if let Some(initial) = &config.initial_task {
        let trimmed = initial.trim();
        if !trimmed.is_empty() {
            tasks.push(trimmed.to_string());
        }
    }
    for c in &config.success_criteria {
        let trimmed = c.trim();
        if !trimmed.is_empty() {
            tasks.push(trimmed.to_string());
        }
    }
    tasks
}

/// Snapshot the host environment for scaffolding. Best-effort: missing tools
/// are simply omitted from the runtime table.
pub fn detect_environment() -> EnvInfo {
    let now = Local::now();
    EnvInfo {
        os_info: format!("{} {}", std::env::consts::OS, std::env::consts::ARCH),
        shell_info: std::env::var("SHELL")
            .ok()
            .and_then(|s| {
                Path::new(&s)
                    .file_name()
                    .and_then(|f| f.to_str().map(str::to_string))
            })
            .unwrap_or_else(|| "unknown".to_string()),
        runtime_versions: BTreeMap::new(),
        timestamp: now.format("%Y-%m-%d %H:%M:%S").to_string(),
        iso_timestamp: now.format("%Y-%m-%dT%H:%M:%S").to_string(),
        created_date: now.format("%Y-%m-%d").to_string(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn fixture_env() -> EnvInfo {
        let mut runtimes = BTreeMap::new();
        runtimes.insert("Rust".to_string(), "1.75".to_string());
        EnvInfo {
            os_info: "linux x86_64".to_string(),
            shell_info: "bash".to_string(),
            runtime_versions: runtimes,
            timestamp: "2026-04-18 00:00:00".to_string(),
            iso_timestamp: "2026-04-18T00:00:00".to_string(),
            created_date: "2026-04-18".to_string(),
        }
    }

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
    fn init_creates_full_tree() {
        let root = tmpdir();
        let config = InitConfig {
            project_name: Some("Demo".into()),
            goal: Some("Ship it".into()),
            success_criteria: vec!["passes tests".into()],
            ..Default::default()
        };
        let geck = init_geck_folder(&root, &config, &fixture_env()).unwrap();

        assert!(geck.join("LLM_init.md").is_file());
        assert!(geck.join("GECK_Inst.md").is_file());
        assert!(geck.join("env.md").is_file());
        assert!(geck.join("tasks.md").is_file());
        assert!(geck.join("log.md").is_file());
        assert!(geck.join("log_index.jsonl").is_file());
        assert!(geck.join("decisions.md").is_file());
        assert!(geck.join("learnings.md").is_file());
        assert!(geck.join("decisions").is_dir());
        assert!(geck.join("learnings").is_dir());
        assert!(geck.join("log_archive").is_dir());

        fs::remove_dir_all(&root).ok();
    }

    #[test]
    fn init_llm_init_reflects_config() {
        let root = tmpdir();
        let config = InitConfig {
            project_name: Some("Demo".into()),
            goal: Some("Ship it".into()),
            success_criteria: vec!["passes tests".into(), "green CI".into()],
            frameworks: vec!["tokio".into(), "tera".into()],
            context_budget: Some("large".into()),
            git_branch: Some("main".into()),
            ..Default::default()
        };
        let geck = init_geck_folder(&root, &config, &fixture_env()).unwrap();
        let body = fs::read_to_string(geck.join("LLM_init.md")).unwrap();
        assert!(body.contains("# Project: Demo"));
        assert!(body.contains("**Branch:** main"));
        assert!(body.contains("**Context Budget:** large"));
        assert!(body.contains("- **Frameworks:** tokio, tera"));
        assert!(body.contains("- [ ] passes tests"));
        assert!(body.contains("- [ ] green CI"));
        fs::remove_dir_all(&root).ok();
    }

    #[test]
    fn init_tasks_md_lists_default_plus_initial_plus_criteria() {
        let root = tmpdir();
        let config = InitConfig {
            project_name: Some("Demo".into()),
            initial_task: Some("kickoff thing".into()),
            success_criteria: vec!["crit A".into(), "crit B".into()],
            ..Default::default()
        };
        let geck = init_geck_folder(&root, &config, &fixture_env()).unwrap();
        let body = fs::read_to_string(geck.join("tasks.md")).unwrap();
        assert!(body.contains("TASK-001"));
        assert!(body.contains(DEFAULT_INITIAL_TASK));
        assert!(body.contains("TASK-002"));
        assert!(body.contains("kickoff thing"));
        assert!(body.contains("TASK-003"));
        assert!(body.contains("crit A"));
        assert!(body.contains("TASK-004"));
        assert!(body.contains("crit B"));
        fs::remove_dir_all(&root).ok();
    }

    #[test]
    fn log_index_jsonl_is_single_valid_line() {
        let root = tmpdir();
        let config = InitConfig {
            project_name: Some("Demo".into()),
            ..Default::default()
        };
        let geck = init_geck_folder(&root, &config, &fixture_env()).unwrap();
        let body = fs::read_to_string(geck.join("log_index.jsonl")).unwrap();
        let lines: Vec<&str> = body.lines().filter(|l| !l.is_empty()).collect();
        assert_eq!(lines.len(), 1);
        let parsed: serde_json::Value = serde_json::from_str(lines[0]).unwrap();
        assert_eq!(parsed["id"], 0);
        assert_eq!(parsed["state"], "WAIT");
        assert_eq!(parsed["ts"], "2026-04-18T00:00:00");
        fs::remove_dir_all(&root).ok();
    }
}
