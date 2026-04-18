//! Embedded GECK v1.3 templates, rendered via Tera.
//!
//! Mirrors the Python `TemplateEngine` surface: nine built-in templates plus
//! user-supplied custom templates registered by name.

use std::collections::HashMap;

use tera::{Context, Tera, Value};
use thiserror::Error;

pub use tera::Context as RenderContext;

/// Canonical names of the nine GECK v1.3 templates.
pub const BUILTIN_NAMES: &[&str] = &[
    "llm_init",
    "geck_inst",
    "env",
    "tasks",
    "log",
    "log_index",
    "decisions_index",
    "learnings_index",
    "repor",
];

const LLM_INIT: &str = include_str!("../templates/llm_init.tera");
const GECK_INST: &str = include_str!("../templates/geck_inst.tera");
const ENV: &str = include_str!("../templates/env.tera");
const TASKS: &str = include_str!("../templates/tasks.tera");
const LOG: &str = include_str!("../templates/log.tera");
const LOG_INDEX: &str = include_str!("../templates/log_index.tera");
const DECISIONS_INDEX: &str = include_str!("../templates/decisions_index.tera");
const LEARNINGS_INDEX: &str = include_str!("../templates/learnings_index.tera");
const REPOR: &str = include_str!("../templates/repor.tera");

#[derive(Debug, Error)]
pub enum TemplateError {
    #[error("unknown template: {0}")]
    Unknown(String),
    #[error("failed to render template {name}: {source}")]
    Render {
        name: String,
        #[source]
        source: tera::Error,
    },
    #[error("failed to register template {name}: {source}")]
    Register {
        name: String,
        #[source]
        source: tera::Error,
    },
}

pub struct TemplateEngine {
    tera: Tera,
}

impl TemplateEngine {
    pub fn new() -> Self {
        let mut tera = Tera::default();
        tera.register_filter("zfill", zfill_filter);
        for (name, body) in Self::builtins() {
            tera.add_raw_template(name, body)
                .expect("bundled template must parse");
        }
        Self { tera }
    }

    fn builtins() -> [(&'static str, &'static str); 9] {
        [
            ("llm_init", LLM_INIT),
            ("geck_inst", GECK_INST),
            ("env", ENV),
            ("tasks", TASKS),
            ("log", LOG),
            ("log_index", LOG_INDEX),
            ("decisions_index", DECISIONS_INDEX),
            ("learnings_index", LEARNINGS_INDEX),
            ("repor", REPOR),
        ]
    }

    pub fn render(&self, name: &str, ctx: &Context) -> Result<String, TemplateError> {
        if !self.tera.get_template_names().any(|n| n == name) {
            return Err(TemplateError::Unknown(name.to_string()));
        }
        self.tera
            .render(name, ctx)
            .map_err(|source| TemplateError::Render {
                name: name.to_string(),
                source,
            })
    }

    /// Register a user-supplied template. Overrides any existing template of
    /// the same name.
    pub fn add_template(&mut self, name: &str, body: &str) -> Result<(), TemplateError> {
        self.tera
            .add_raw_template(name, body)
            .map_err(|source| TemplateError::Register {
                name: name.to_string(),
                source,
            })
    }

    pub fn list_templates(&self) -> Vec<String> {
        let mut names: Vec<_> = self.tera.get_template_names().map(str::to_string).collect();
        names.sort();
        names
    }
}

impl Default for TemplateEngine {
    fn default() -> Self {
        Self::new()
    }
}

/// `{{ n | zfill(width=3) }}` — pads an integer to `width` chars with leading zeros.
fn zfill_filter(value: &Value, args: &HashMap<String, Value>) -> tera::Result<Value> {
    let n = value
        .as_i64()
        .or_else(|| value.as_u64().map(|x| x as i64))
        .ok_or_else(|| tera::Error::msg(format!("zfill: expected integer, got {value:?}")))?;
    let width = args
        .get("width")
        .and_then(Value::as_u64)
        .unwrap_or(3) as usize;
    Ok(Value::String(format!("{n:0>width$}")))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn engine_registers_all_nine_builtins() {
        let engine = TemplateEngine::new();
        let names = engine.list_templates();
        for &n in BUILTIN_NAMES {
            assert!(names.contains(&n.to_string()), "missing {n}");
        }
    }

    #[test]
    fn unknown_template_errors() {
        let engine = TemplateEngine::new();
        let err = engine.render("nope", &Context::new()).unwrap_err();
        assert!(matches!(err, TemplateError::Unknown(_)));
    }

    #[test]
    fn static_index_templates_render() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");

        let dec = engine.render("decisions_index", &ctx).unwrap();
        assert!(dec.starts_with("# Decisions — Demo"));
        assert!(dec.contains("(no decisions yet)"));

        let lrn = engine.render("learnings_index", &ctx).unwrap();
        assert!(lrn.starts_with("# Learnings — Demo"));
        assert!(lrn.contains("(no learnings yet)"));
    }

    #[test]
    fn log_index_emits_valid_jsonl() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("timestamp", "2026-04-18T00:00:00");
        let rendered = engine.render("log_index", &ctx).unwrap();
        let line = rendered.trim_end();
        let parsed: serde_json::Value = serde_json::from_str(line).unwrap();
        assert_eq!(parsed["id"], 0);
        assert_eq!(parsed["state"], "WAIT");
        assert_eq!(parsed["ts"], "2026-04-18T00:00:00");
        assert_eq!(parsed["files"], serde_json::json!(["GECK/*"]));
    }

    #[test]
    fn log_renders_entry_zero() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("timestamp", "2026-04-18 00:00:00");
        let out = engine.render("log", &ctx).unwrap();
        assert!(out.contains("# Session Log — Demo"));
        assert!(out.contains("## Entry #0 — 2026-04-18 00:00:00 — touched: (init)"));
        assert!(out.contains("- State: WAIT"));
    }

    #[test]
    fn tasks_uses_zfill_for_task_ids() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("timestamp", "2026-04-18 00:00:00");
        ctx.insert("initial_tasks", &vec!["first", "second"]);
        let out = engine.render("tasks", &ctx).unwrap();
        assert!(out.contains("- [ ] TASK-001 | TYPE: feature | SCOPE: medium | OWNER: agent"));
        assert!(out.contains("- [ ] TASK-002 | TYPE: feature | SCOPE: medium | OWNER: agent"));
        assert!(out.contains("  - first"));
        assert!(out.contains("  - second"));
    }

    #[test]
    fn tasks_falls_back_to_default_task() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("timestamp", "2026-04-18 00:00:00");
        ctx.insert("initial_tasks", &Vec::<String>::new());
        let out = engine.render("tasks", &ctx).unwrap();
        assert!(out.contains("TASK-001 | TYPE: feature | SCOPE: medium | OWNER: agent"));
        assert!(out.contains("Review project goals and begin implementation"));
    }

    #[test]
    fn llm_init_defaults_fill_missing_fields() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("created_date", "2026-04-18");
        ctx.insert("goal", "Ship it");
        ctx.insert("success_criteria", &vec!["passes tests"]);
        let out = engine.render("llm_init", &ctx).unwrap();
        assert!(out.contains("# Project: Demo"));
        assert!(out.contains("**Repository:** Not specified"));
        assert!(out.contains("**Context Budget:** medium"));
        assert!(out.contains("- [ ] passes tests"));
        assert!(out.contains("- **Frameworks:** Not specified"));
    }

    #[test]
    fn llm_init_uses_git_branch_when_provided() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("created_date", "2026-04-18");
        ctx.insert("goal", "x");
        ctx.insert("success_criteria", &Vec::<String>::new());
        ctx.insert("git_branch", "feat/rust-port");
        let out = engine.render("llm_init", &ctx).unwrap();
        assert!(out.contains("**Branch:** feat/rust-port"));
    }

    #[test]
    fn env_renders_runtime_table_and_platforms() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("timestamp", "2026-04-18 00:00:00");
        ctx.insert("os_info", "Linux 6.8");
        ctx.insert("shell_info", "bash");
        let mut runtimes: std::collections::BTreeMap<&str, &str> =
            std::collections::BTreeMap::new();
        runtimes.insert("Rust", "1.75");
        ctx.insert("runtime_versions", &runtimes);
        ctx.insert(
            "all_platforms",
            &vec!["Windows", "macOS", "Linux"],
        );
        ctx.insert("target_platforms", &vec!["Linux"]);
        let out = engine.render("env", &ctx).unwrap();
        assert!(out.contains("| Rust | 1.75 |"));
        assert!(out.contains("- [ ] Windows"));
        assert!(out.contains("- [ ] macOS"));
        assert!(out.contains("- [x] Linux"));
    }

    #[test]
    fn geck_inst_is_static_and_contains_protocol_marker() {
        let engine = TemplateEngine::new();
        let out = engine.render("geck_inst", &Context::new()).unwrap();
        assert!(out.contains("**Protocol Version:** 1.3"));
        assert!(out.contains("## On Session Start"));
    }

    #[test]
    fn custom_template_override() {
        let mut engine = TemplateEngine::new();
        engine
            .add_template("custom", "hello {{ who }}")
            .unwrap();
        let mut ctx = Context::new();
        ctx.insert("who", "world");
        assert_eq!(engine.render("custom", &ctx).unwrap(), "hello world");
    }
}
