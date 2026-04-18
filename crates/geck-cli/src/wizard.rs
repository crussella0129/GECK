//! Interactive `geck generate` wizard.
//!
//! Main-menu-driven: every section is visible on the menu at all times, and
//! the user edits them in any order. The menu also exposes Preview and Save
//! entries, so the flow is fully non-linear: hop between sections until
//! satisfied, preview, save.

use std::path::PathBuf;

use inquire::{Confirm, MultiSelect, Select, Text};

use geck_core::profiles::ProfileManager;
use geck_core::scaffold::{self, InitConfig};
use geck_core::templates::{RenderContext, TemplateEngine};

const PLATFORMS: &[&str] = &["Windows", "macOS", "Linux", "Docker", "iOS", "Android", "Web"];
const BUDGETS: &[&str] = &["small", "medium", "large"];

/// Interactive state the wizard edits. Mirrors the fields the Python wizard
/// collects, plus a chosen profile key.
#[derive(Debug, Default, Clone)]
pub struct WizardState {
    pub project_name: Option<String>,
    pub local_path: Option<String>,
    pub repo_url: Option<String>,
    pub profile: Option<String>,
    pub goal: Option<String>,
    pub context: Option<String>,
    pub success_criteria: Vec<String>,
    pub languages: Option<String>,
    pub must_use: Option<String>,
    pub must_avoid: Option<String>,
    pub platforms: Vec<String>,
    pub initial_task: Option<String>,
    pub context_budget: String,
}

impl WizardState {
    pub fn new() -> Self {
        Self {
            context_budget: "medium".to_string(),
            ..Default::default()
        }
    }

    fn to_config(&self) -> InitConfig {
        InitConfig {
            project_name: self.project_name.clone(),
            repo_url: self.repo_url.clone(),
            local_path: self.local_path.clone(),
            goal: self.goal.clone(),
            success_criteria: self.success_criteria.clone(),
            languages: self.languages.clone(),
            frameworks: Vec::new(),
            must_use: self.must_use.clone(),
            must_avoid: self.must_avoid.clone(),
            platforms: self.platforms.clone(),
            context: self.context.clone(),
            initial_task: self.initial_task.clone(),
            context_budget: Some(self.context_budget.clone()),
            ..Default::default()
        }
    }
}

pub enum WizardOutcome {
    WroteLlmInit(PathBuf),
    Scaffolded(PathBuf),
    Cancelled,
}

pub fn run() -> Result<WizardOutcome, WizardError> {
    println!();
    println!("============================================================");
    println!("  GECK Generator — Interactive Wizard");
    println!("============================================================");
    println!();

    let profiles = ProfileManager::new();
    let mut state = WizardState::new();

    loop {
        let menu = build_menu(&state);
        let choice = Select::new("Edit a section, preview, or save:", menu)
            .with_page_size(20)
            .prompt_skippable()?;
        let Some(choice) = choice else {
            return Ok(WizardOutcome::Cancelled);
        };

        match choice.action {
            Action::ProjectName => edit_project_name(&mut state)?,
            Action::LocalPath => edit_local_path(&mut state)?,
            Action::RepoUrl => edit_repo_url(&mut state)?,
            Action::Profile => edit_profile(&mut state, &profiles)?,
            Action::Goal => edit_goal(&mut state)?,
            Action::Context => edit_context(&mut state)?,
            Action::SuccessCriteria => edit_success_criteria(&mut state, &profiles)?,
            Action::Languages => edit_languages(&mut state, &profiles)?,
            Action::MustUse => edit_must_use(&mut state, &profiles)?,
            Action::MustAvoid => edit_must_avoid(&mut state, &profiles)?,
            Action::Platforms => edit_platforms(&mut state, &profiles)?,
            Action::InitialTask => edit_initial_task(&mut state)?,
            Action::ContextBudget => edit_context_budget(&mut state)?,
            Action::Preview => show_preview(&state, &profiles)?,
            Action::Save => {
                if let Some(outcome) = save(&state, &profiles)? {
                    return Ok(outcome);
                }
            }
            Action::Quit => return Ok(WizardOutcome::Cancelled),
        }
    }
}

#[derive(Debug, Clone, Copy)]
enum Action {
    ProjectName,
    LocalPath,
    RepoUrl,
    Profile,
    Goal,
    Context,
    SuccessCriteria,
    Languages,
    MustUse,
    MustAvoid,
    Platforms,
    InitialTask,
    ContextBudget,
    Preview,
    Save,
    Quit,
}

struct MenuItem {
    label: String,
    action: Action,
}

impl std::fmt::Display for MenuItem {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.label)
    }
}

fn build_menu(state: &WizardState) -> Vec<MenuItem> {
    let mut items = Vec::new();
    let mark = |filled: bool| if filled { "✓" } else { " " };
    let summarize_opt = |v: &Option<String>| -> String {
        match v {
            Some(s) if !s.trim().is_empty() => truncate(s, 40),
            _ => "(empty)".to_string(),
        }
    };
    let summarize_list = |v: &[String]| -> String {
        if v.is_empty() {
            "(empty)".to_string()
        } else {
            format!("{} item{}", v.len(), if v.len() == 1 { "" } else { "s" })
        }
    };

    items.push(MenuItem {
        label: format!(
            "[{}] Project name        — {}",
            mark(state.project_name.as_deref().map(str::trim).is_some_and(|s| !s.is_empty())),
            summarize_opt(&state.project_name)
        ),
        action: Action::ProjectName,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Local path          — {}",
            mark(state.local_path.is_some()),
            summarize_opt(&state.local_path)
        ),
        action: Action::LocalPath,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Repository URL      — {}",
            mark(state.repo_url.as_deref().map(str::trim).is_some_and(|s| !s.is_empty())),
            summarize_opt(&state.repo_url)
        ),
        action: Action::RepoUrl,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Profile             — {}",
            mark(state.profile.is_some()),
            state.profile.clone().unwrap_or_else(|| "(none)".into())
        ),
        action: Action::Profile,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Goal                — {}",
            mark(state.goal.as_deref().map(str::trim).is_some_and(|s| !s.is_empty())),
            summarize_opt(&state.goal)
        ),
        action: Action::Goal,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Context             — {}",
            mark(state.context.as_deref().map(str::trim).is_some_and(|s| !s.is_empty())),
            summarize_opt(&state.context)
        ),
        action: Action::Context,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Success criteria    — {}",
            mark(!state.success_criteria.is_empty()),
            summarize_list(&state.success_criteria)
        ),
        action: Action::SuccessCriteria,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Languages           — {}",
            mark(state.languages.as_deref().map(str::trim).is_some_and(|s| !s.is_empty())),
            summarize_opt(&state.languages)
        ),
        action: Action::Languages,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Must use            — {}",
            mark(state.must_use.as_deref().map(str::trim).is_some_and(|s| !s.is_empty())),
            summarize_opt(&state.must_use)
        ),
        action: Action::MustUse,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Must avoid          — {}",
            mark(state.must_avoid.as_deref().map(str::trim).is_some_and(|s| !s.is_empty())),
            summarize_opt(&state.must_avoid)
        ),
        action: Action::MustAvoid,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Platforms           — {}",
            mark(!state.platforms.is_empty()),
            if state.platforms.is_empty() {
                "(none)".to_string()
            } else {
                state.platforms.join(", ")
            }
        ),
        action: Action::Platforms,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Initial task        — {}",
            mark(state.initial_task.as_deref().map(str::trim).is_some_and(|s| !s.is_empty())),
            summarize_opt(&state.initial_task)
        ),
        action: Action::InitialTask,
    });
    items.push(MenuItem {
        label: format!(
            "[✓] Context budget       — {}",
            state.context_budget
        ),
        action: Action::ContextBudget,
    });
    items.push(MenuItem {
        label: "────────  Preview LLM_init.md".to_string(),
        action: Action::Preview,
    });
    items.push(MenuItem {
        label: "────────  Save…".to_string(),
        action: Action::Save,
    });
    items.push(MenuItem {
        label: "────────  Quit (discard)".to_string(),
        action: Action::Quit,
    });
    items
}

fn edit_project_name(state: &mut WizardState) -> Result<(), WizardError> {
    let val = Text::new("Project name:")
        .with_default(state.project_name.as_deref().unwrap_or(""))
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.project_name = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_local_path(state: &mut WizardState) -> Result<(), WizardError> {
    let cwd = std::env::current_dir()
        .ok()
        .and_then(|p| p.to_str().map(str::to_string))
        .unwrap_or_default();
    let default = state.local_path.clone().unwrap_or(cwd);
    let val = Text::new("Local project path:")
        .with_default(&default)
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.local_path = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_repo_url(state: &mut WizardState) -> Result<(), WizardError> {
    let val = Text::new("Repository URL (optional):")
        .with_default(state.repo_url.as_deref().unwrap_or(""))
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.repo_url = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_profile(state: &mut WizardState, profiles: &ProfileManager) -> Result<(), WizardError> {
    let mut options: Vec<String> = profiles
        .list_with_descriptions()
        .into_iter()
        .map(|(k, n, d)| format!("{k} — {n}: {d}"))
        .collect();
    options.insert(0, "(none)".to_string());

    let cur_label = state
        .profile
        .as_ref()
        .and_then(|k| options.iter().find(|o| o.starts_with(&format!("{k} —"))).cloned())
        .unwrap_or_else(|| "(none)".to_string());
    let starting_cursor = options.iter().position(|o| o == &cur_label).unwrap_or(0);

    let pick = Select::new("Profile:", options.clone())
        .with_starting_cursor(starting_cursor)
        .with_page_size(15)
        .prompt_skippable()?;
    let Some(pick) = pick else { return Ok(()) };

    if pick == "(none)" {
        state.profile = None;
        return Ok(());
    }
    let key = pick.split_once(" — ").map(|(k, _)| k.to_string());
    if let Some(key) = key {
        state.profile = Some(key.clone());
        // Offer to backfill empty fields from the profile.
        let prefill = Confirm::new("Pre-fill empty fields (languages, frameworks, platforms, criteria, must-use, must-avoid) from this profile?")
            .with_default(true)
            .prompt_skippable()?
            .unwrap_or(false);
        if prefill {
            let p = profiles.get(&key)?;
            if state.languages.is_none() {
                state.languages = p.languages.clone();
            }
            if state.platforms.is_empty() {
                state.platforms = p.platforms.clone();
            }
            if state.success_criteria.is_empty() {
                state.success_criteria = p.suggested_criteria.clone();
            }
            if state.must_use.is_none() {
                state.must_use = p.suggested_must_use.clone();
            }
            if state.must_avoid.is_none() {
                state.must_avoid = p.suggested_must_avoid.clone();
            }
        }
    }
    Ok(())
}

fn edit_goal(state: &mut WizardState) -> Result<(), WizardError> {
    let val = Text::new("Goal (one-line summary of what should exist when done):")
        .with_default(state.goal.as_deref().unwrap_or(""))
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.goal = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_context(state: &mut WizardState) -> Result<(), WizardError> {
    let val = Text::new("Additional context (optional):")
        .with_default(state.context.as_deref().unwrap_or(""))
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.context = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_success_criteria(
    state: &mut WizardState,
    profiles: &ProfileManager,
) -> Result<(), WizardError> {
    loop {
        let current = if state.success_criteria.is_empty() {
            "  (none)".to_string()
        } else {
            state
                .success_criteria
                .iter()
                .enumerate()
                .map(|(i, c)| format!("  {}. {}", i + 1, c))
                .collect::<Vec<_>>()
                .join("\n")
        };
        println!("\nCurrent criteria:\n{current}\n");

        let mut options = vec!["Add criterion".to_string()];
        if !state.success_criteria.is_empty() {
            options.push("Remove criterion".to_string());
            options.push("Clear all".to_string());
        }
        if state.profile.is_some() {
            options.push("Replace with profile's suggested criteria".to_string());
        }
        options.push("Back to menu".to_string());

        let pick = Select::new("Criteria:", options).prompt_skippable()?;
        let Some(pick) = pick else { return Ok(()) };
        match pick.as_str() {
            "Add criterion" => {
                if let Some(v) = Text::new("New criterion:").prompt_skippable()? {
                    let trimmed = v.trim();
                    if !trimmed.is_empty() {
                        state.success_criteria.push(trimmed.to_string());
                    }
                }
            }
            "Remove criterion" => {
                let idx = Select::new("Remove which?", state.success_criteria.clone())
                    .prompt_skippable()?;
                if let Some(item) = idx {
                    state.success_criteria.retain(|c| c != &item);
                }
            }
            "Clear all" => {
                state.success_criteria.clear();
            }
            "Replace with profile's suggested criteria" => {
                if let Some(key) = &state.profile {
                    state.success_criteria = profiles.get(key)?.suggested_criteria.clone();
                }
            }
            "Back to menu" => return Ok(()),
            _ => {}
        }
    }
}

fn edit_languages(state: &mut WizardState, profiles: &ProfileManager) -> Result<(), WizardError> {
    let default = state
        .languages
        .clone()
        .or_else(|| {
            state
                .profile
                .as_ref()
                .and_then(|k| profiles.get(k).ok())
                .and_then(|p| p.languages.clone())
        })
        .unwrap_or_default();
    let val = Text::new("Languages:")
        .with_default(&default)
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.languages = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_must_use(state: &mut WizardState, profiles: &ProfileManager) -> Result<(), WizardError> {
    let default = state
        .must_use
        .clone()
        .or_else(|| {
            state
                .profile
                .as_ref()
                .and_then(|k| profiles.get(k).ok())
                .and_then(|p| p.suggested_must_use.clone())
        })
        .unwrap_or_default();
    let val = Text::new("Must use (required tools / patterns):")
        .with_default(&default)
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.must_use = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_must_avoid(state: &mut WizardState, profiles: &ProfileManager) -> Result<(), WizardError> {
    let default = state
        .must_avoid
        .clone()
        .or_else(|| {
            state
                .profile
                .as_ref()
                .and_then(|k| profiles.get(k).ok())
                .and_then(|p| p.suggested_must_avoid.clone())
        })
        .unwrap_or_default();
    let val = Text::new("Must avoid (forbidden tools / patterns):")
        .with_default(&default)
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.must_avoid = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_platforms(state: &mut WizardState, profiles: &ProfileManager) -> Result<(), WizardError> {
    let mut preselected: Vec<usize> = Vec::new();
    let defaults: Vec<String> = if state.platforms.is_empty() {
        state
            .profile
            .as_ref()
            .and_then(|k| profiles.get(k).ok())
            .map(|p| p.platforms.clone())
            .unwrap_or_default()
    } else {
        state.platforms.clone()
    };
    for (i, p) in PLATFORMS.iter().enumerate() {
        if defaults.iter().any(|d| d == p) {
            preselected.push(i);
        }
    }
    let chosen = MultiSelect::new(
        "Target platforms (space to toggle, enter to confirm):",
        PLATFORMS.iter().map(|s| (*s).to_string()).collect(),
    )
    .with_default(&preselected)
    .prompt_skippable()?;
    if let Some(chosen) = chosen {
        state.platforms = chosen;
    }
    Ok(())
}

fn edit_initial_task(state: &mut WizardState) -> Result<(), WizardError> {
    let val = Text::new("First task to work on (optional):")
        .with_default(state.initial_task.as_deref().unwrap_or(""))
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.initial_task = if trimmed.is_empty() { None } else { Some(trimmed.to_string()) };
    }
    Ok(())
}

fn edit_context_budget(state: &mut WizardState) -> Result<(), WizardError> {
    let cursor = BUDGETS
        .iter()
        .position(|b| *b == state.context_budget)
        .unwrap_or(1);
    let pick = Select::new(
        "Context budget (drives LOG_ACTIVE_ENTRIES: small=3, medium=10, large=25):",
        BUDGETS.iter().map(|s| (*s).to_string()).collect(),
    )
    .with_starting_cursor(cursor)
    .prompt_skippable()?;
    if let Some(v) = pick {
        state.context_budget = v;
    }
    Ok(())
}

fn show_preview(state: &WizardState, profiles: &ProfileManager) -> Result<(), WizardError> {
    let rendered = render_llm_init(state, profiles)?;
    println!();
    println!("────────────────────── LLM_init.md preview ──────────────────────");
    println!("{}", rendered);
    println!("─────────────────────────────────────────────────────────────────");
    println!();
    let _ = Text::new("Press Enter to return to the menu…")
        .with_default("")
        .prompt_skippable()?;
    Ok(())
}

fn render_llm_init(
    state: &WizardState,
    profiles: &ProfileManager,
) -> Result<String, WizardError> {
    let mut config = state.to_config();
    if let Some(key) = &state.profile {
        // Merge profile frameworks unconditionally (user doesn't type frameworks).
        if let Ok(p) = profiles.get(key) {
            if config.frameworks.is_empty() {
                config.frameworks = p.frameworks.clone();
            }
        }
    }
    let engine = TemplateEngine::new();
    let env = scaffold::detect_environment();
    let mut ctx = RenderContext::new();
    ctx.insert(
        "project_name",
        config.project_name.as_deref().unwrap_or("Untitled Project"),
    );
    ctx.insert("goal", config.goal.as_deref().unwrap_or("No goal specified."));
    ctx.insert("created_date", &env.created_date);
    ctx.insert("success_criteria", &config.success_criteria);
    ctx.insert("frameworks", &config.frameworks);
    ctx.insert("platforms", &config.platforms);
    ctx.insert(
        "context_budget",
        config.context_budget.as_deref().unwrap_or("medium"),
    );
    if let Some(v) = &config.repo_url {
        ctx.insert("repo_url", v);
    }
    if let Some(v) = &config.local_path {
        ctx.insert("local_path", v);
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
    Ok(engine.render("llm_init", &ctx)?)
}

fn save(
    state: &WizardState,
    profiles: &ProfileManager,
) -> Result<Option<WizardOutcome>, WizardError> {
    // Minimum-viable check.
    if state.project_name.as_deref().map(str::trim).unwrap_or("").is_empty() {
        println!("  ⚠ Project name is empty — set it before saving.");
        let _ = Text::new("Press Enter to return to the menu…")
            .with_default("")
            .prompt_skippable()?;
        return Ok(None);
    }
    if state.goal.as_deref().map(str::trim).unwrap_or("").is_empty() {
        println!("  ⚠ Goal is empty — set it before saving.");
        let _ = Text::new("Press Enter to return to the menu…")
            .with_default("")
            .prompt_skippable()?;
        return Ok(None);
    }

    let options = vec![
        "Write LLM_init.md only".to_string(),
        "Scaffold full GECK/ folder".to_string(),
        "Back to menu".to_string(),
    ];
    let pick = Select::new("Save as:", options).prompt_skippable()?;
    let Some(pick) = pick else { return Ok(None) };

    let default_dir = state
        .local_path
        .clone()
        .or_else(|| {
            std::env::current_dir()
                .ok()
                .and_then(|p| p.to_str().map(str::to_string))
        })
        .unwrap_or_else(|| ".".to_string());

    match pick.as_str() {
        "Write LLM_init.md only" => {
            let default_path = format!("{}/LLM_init.md", default_dir.trim_end_matches('/'));
            let path = Text::new("Output path:")
                .with_default(&default_path)
                .prompt_skippable()?;
            let Some(path) = path else { return Ok(None) };
            let body = render_llm_init(state, profiles)?;
            let pb = PathBuf::from(path);
            if let Some(parent) = pb.parent() {
                if !parent.as_os_str().is_empty() {
                    std::fs::create_dir_all(parent)?;
                }
            }
            std::fs::write(&pb, body)?;
            println!("\n✓ wrote {}", pb.display());
            Ok(Some(WizardOutcome::WroteLlmInit(pb)))
        }
        "Scaffold full GECK/ folder" => {
            let path = Text::new("Scaffold into which project directory?")
                .with_default(&default_dir)
                .prompt_skippable()?;
            let Some(path) = path else { return Ok(None) };
            let pb = PathBuf::from(&path);
            let mut config = state.to_config();
            if let Some(key) = &state.profile {
                if let Ok(p) = profiles.get(key) {
                    if config.frameworks.is_empty() {
                        config.frameworks = p.frameworks.clone();
                    }
                }
            }
            let env = scaffold::detect_environment();
            let geck = scaffold::init_geck_folder(&pb, &config, &env)?;
            println!("\n✓ scaffolded {}", geck.display());
            Ok(Some(WizardOutcome::Scaffolded(geck)))
        }
        _ => Ok(None),
    }
}

fn truncate(s: &str, max: usize) -> String {
    let s = s.trim();
    if s.chars().count() <= max {
        return s.to_string();
    }
    let cut: String = s.chars().take(max.saturating_sub(1)).collect();
    format!("{cut}…")
}

#[derive(Debug, thiserror::Error)]
pub enum WizardError {
    #[error("prompt error: {0}")]
    Prompt(#[from] inquire::InquireError),
    #[error("profile error: {0}")]
    Profile(#[from] geck_core::profiles::ProfileError),
    #[error("template error: {0}")]
    Template(#[from] geck_core::templates::TemplateError),
    #[error("scaffold error: {0}")]
    Scaffold(#[from] geck_core::scaffold::ScaffoldError),
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
}
