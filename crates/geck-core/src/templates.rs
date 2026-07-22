//! Embedded launcher templates, rendered via Tera.
//!
//! Four built-in templates: the mission spec body, the launch prompt, and
//! the two seeding snippets (ADR-000, a backlog-seed line) appended into an
//! Animus Sprint Loops project.

use tera::{Context, Tera};
use thiserror::Error;

pub use tera::Context as RenderContext;

/// Canonical names of the four built-in templates.
pub const BUILTIN_NAMES: &[&str] = &["mission_spec", "launch_prompt", "adr_000", "backlog_seed"];

const MISSION_SPEC: &str = include_str!("../templates/mission_spec.tera");
const LAUNCH_PROMPT: &str = include_str!("../templates/launch_prompt.tera");
const ADR_000: &str = include_str!("../templates/adr_000.tera");
const BACKLOG_SEED: &str = include_str!("../templates/backlog_seed.tera");

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
        for (name, body) in Self::builtins() {
            tera.add_raw_template(name, body)
                .expect("bundled template must parse");
        }
        Self { tera }
    }

    fn builtins() -> [(&'static str, &'static str); 4] {
        [
            ("mission_spec", MISSION_SPEC),
            ("launch_prompt", LAUNCH_PROMPT),
            ("adr_000", ADR_000),
            ("backlog_seed", BACKLOG_SEED),
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn engine_registers_all_four_builtins() {
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
    fn adr_000_renders_with_date() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("date", "2026-07-21");
        let out = engine.render("adr_000", &ctx).unwrap();
        assert!(out.starts_with("## 2026-07-21 — Mission spec adopted"));
        assert!(out.contains("(sprint 0)"));
    }

    #[test]
    fn backlog_seed_renders_with_id_and_description() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("id", "101");
        ctx.insert("description", "wire up the thing");
        let out = engine.render("backlog_seed", &ctx).unwrap();
        assert_eq!(
            out.trim_end(),
            "- [ ] T-101 (backlog): wire up the thing — touches: TBD (identified during research)"
        );
    }

    #[test]
    fn mission_spec_renders_required_sections() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("goal", "Ship it.");
        ctx.insert("success_criteria", &vec!["passes tests"]);
        ctx.insert("non_goals", &Vec::<String>::new());
        ctx.insert("languages", &Option::<String>::None);
        ctx.insert("frameworks", &Vec::<String>::new());
        ctx.insert("platforms", &vec!["Linux"]);
        ctx.insert("must_use", &Option::<String>::None);
        ctx.insert("must_avoid", &Option::<String>::None);
        ctx.insert("merge_mode", "approve");
        ctx.insert("work_branch", "dev");
        ctx.insert("working_agreement_notes", &Vec::<String>::new());
        ctx.insert("sprint_zero_charter", "Research X.");
        ctx.insert("backlog_seeds", &vec!["T-101 (backlog): wire up Y"]);
        let out = engine.render("mission_spec", &ctx).unwrap();
        assert!(out.contains("# Mission: Demo"));
        assert!(out.contains("## Goal\n\nShip it."));
        assert!(out.contains("- [ ] passes tests"));
        assert!(out.contains("(none declared)"));
        assert!(out.contains("**Merge mode:** approve"));
        assert!(out.contains("T-101 (backlog): wire up Y"));
        assert!(out.contains("## Amendment Protocol"));
    }

    #[test]
    fn launch_prompt_renders_claude_code_variant() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("harness", "claude-code");
        ctx.insert("goal_summary", "Ship the thing");
        ctx.insert("work_branch", "dev");
        ctx.insert("merge_mode", "approve");
        ctx.insert("sprint_loops_ref", "2026-07-21");
        let out = engine.render("launch_prompt", &ctx).unwrap();
        assert!(out.contains("/plugin marketplace add crussella0129/sprint-loops"));
        assert!(out.contains("/sprint-loop start \"Ship the thing"));
        assert!(out.contains("Establish the work branch"));
    }

    #[test]
    fn launch_prompt_renders_codex_cli_variant() {
        let engine = TemplateEngine::new();
        let mut ctx = Context::new();
        ctx.insert("project_name", "Demo");
        ctx.insert("harness", "codex-cli");
        ctx.insert("goal_summary", "Ship the thing");
        ctx.insert("work_branch", "dev");
        ctx.insert("merge_mode", "auto");
        ctx.insert("sprint_loops_ref", "2026-07-21");
        let out = engine.render("launch_prompt", &ctx).unwrap();
        assert!(out.contains("cp -r codex-cli/skills/sprint-loops"));
        assert!(!out.contains("/plugin marketplace"));
    }

    #[test]
    fn custom_template_override() {
        let mut engine = TemplateEngine::new();
        engine.add_template("custom", "hello {{ who }}").unwrap();
        let mut ctx = Context::new();
        ctx.insert("who", "world");
        assert_eq!(engine.render("custom", &ctx).unwrap(), "hello world");
    }
}
