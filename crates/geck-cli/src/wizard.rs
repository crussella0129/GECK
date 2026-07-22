//! Interactive `geck launch` wizard.
//!
//! Main-menu-driven: every section is visible on the menu at all times, and
//! the user edits them in any order. The menu also exposes Preview and Save
//! entries, so the flow is fully non-linear: hop between sections until
//! satisfied, preview both artifacts, save.

use std::path::PathBuf;

use inquire::{Confirm, MultiSelect, Select, Text};

use geck_core::profiles::ProfileManager;
use geck_core::scaffold::{self, BacklogSeed};
use geck_core::spec::{self, Harness, MergeMode, MissionSpec, SpecFrontmatter};

const PLATFORMS: &[&str] = &[
    "Windows", "macOS", "Linux", "Docker", "iOS", "Android", "Web",
];
const HARNESSES: &[(Harness, &str, &str)] = &[
    (
        Harness::ClaudeCode,
        "claude-code",
        "Anthropic Claude Code (plugin marketplace)",
    ),
    (
        Harness::CodexCli,
        "codex-cli",
        "OpenAI Codex CLI (skill bundle)",
    ),
    (
        Harness::OpenHarness,
        "open-harness",
        "OpenClaw, OpenCode, custom runners",
    ),
    (Harness::Antigravity, "antigravity", "Antigravity IDE"),
];
const MERGE_MODES: &[(MergeMode, &str, &str)] = &[
    (
        MergeMode::Approve,
        "approve",
        "a human approves each sprint's PR before merge (safer default)",
    ),
    (
        MergeMode::Auto,
        "auto",
        "merge on green CI proceeds autonomously (faster, less oversight)",
    ),
];

/// Interactive state the wizard edits.
#[derive(Debug, Clone)]
pub struct WizardState {
    pub project_name: Option<String>,
    pub local_path: Option<String>,
    pub repo_url: Option<String>,
    pub profile: Option<String>,
    pub goal: Option<String>,
    pub success_criteria: Vec<String>,
    pub non_goals: Vec<String>,
    pub languages: Option<String>,
    pub must_use: Option<String>,
    pub must_avoid: Option<String>,
    pub platforms: Vec<String>,
    pub harness: Harness,
    pub merge_mode: MergeMode,
    pub work_branch: String,
    pub sprint_zero_charter: Option<String>,
    pub backlog_seeds: Vec<String>,
    pub working_agreement_notes: Vec<String>,
    pub seed: bool,
}

impl WizardState {
    pub fn new() -> Self {
        Self {
            project_name: None,
            local_path: None,
            repo_url: None,
            profile: None,
            goal: None,
            success_criteria: Vec::new(),
            non_goals: Vec::new(),
            languages: None,
            must_use: None,
            must_avoid: None,
            platforms: Vec::new(),
            harness: Harness::ClaudeCode,
            merge_mode: MergeMode::Approve,
            work_branch: "dev".to_string(),
            sprint_zero_charter: None,
            backlog_seeds: Vec::new(),
            working_agreement_notes: Vec::new(),
            seed: true,
        }
    }

    fn to_spec(&self, profiles: &ProfileManager, created_date: &str) -> MissionSpec {
        let mut spec = MissionSpec {
            frontmatter: SpecFrontmatter {
                geck: geck_core::SPEC_VERSION.to_string(),
                project: self
                    .project_name
                    .clone()
                    .unwrap_or_else(|| "Untitled Project".into()),
                created: created_date.to_string(),
                profile: self.profile.clone(),
                harness: self.harness,
                merge_mode: self.merge_mode,
                work_branch: self.work_branch.clone(),
                repo: self.repo_url.clone(),
                sprint_loops_ref: Some(created_date.to_string()),
            },
            goal: self
                .goal
                .clone()
                .unwrap_or_else(|| "No goal specified.".into()),
            success_criteria: self.success_criteria.clone(),
            non_goals: self.non_goals.clone(),
            languages: self.languages.clone(),
            frameworks: Vec::new(),
            platforms: self.platforms.clone(),
            must_use: self.must_use.clone(),
            must_avoid: self.must_avoid.clone(),
            working_agreement_notes: self.working_agreement_notes.clone(),
            sprint_zero_charter: self.sprint_zero_charter.clone().unwrap_or_else(|| {
                "Research the existing codebase and confirm the approach in mission-spec.md.".into()
            }),
            backlog_seeds: self.backlog_seeds.clone(),
        };
        // Frameworks aren't user-edited directly — they come from the profile.
        if let Some(key) = &self.profile {
            if let Ok(p) = profiles.get(key) {
                spec.frameworks = p.frameworks.clone();
            }
        }
        spec
    }
}

impl Default for WizardState {
    fn default() -> Self {
        Self::new()
    }
}

pub enum WizardOutcome {
    Launched(PathBuf),
    Cancelled,
}

pub fn run() -> Result<WizardOutcome, WizardError> {
    println!();
    println!("============================================================");
    println!("  GECK — Sprint Zero Launcher");
    println!("============================================================");
    println!();

    let profiles = ProfileManager::new();
    let mut state = WizardState::new();

    loop {
        let menu = build_menu(&state);
        let choice = Select::new("Edit a section, preview, or save:", menu)
            .with_page_size(22)
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
            Action::SuccessCriteria => edit_success_criteria(&mut state, &profiles)?,
            Action::NonGoals => edit_string_list(&mut state.non_goals, "non-goal")?,
            Action::Languages => edit_languages(&mut state, &profiles)?,
            Action::MustUse => edit_must_use(&mut state, &profiles)?,
            Action::MustAvoid => edit_must_avoid(&mut state, &profiles)?,
            Action::Platforms => edit_platforms(&mut state, &profiles)?,
            Action::Harness => edit_harness(&mut state)?,
            Action::MergeMode => edit_merge_mode(&mut state)?,
            Action::WorkBranch => edit_work_branch(&mut state)?,
            Action::SprintZeroCharter => edit_sprint_zero_charter(&mut state)?,
            Action::BacklogSeeds => edit_string_list(&mut state.backlog_seeds, "backlog seed")?,
            Action::WorkingAgreementNotes => {
                edit_string_list(&mut state.working_agreement_notes, "extra stop-checkpoint")?
            }
            Action::ToggleSeed => state.seed = !state.seed,
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
    SuccessCriteria,
    NonGoals,
    Languages,
    MustUse,
    MustAvoid,
    Platforms,
    Harness,
    MergeMode,
    WorkBranch,
    SprintZeroCharter,
    BacklogSeeds,
    WorkingAgreementNotes,
    ToggleSeed,
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
            "[{}] Project name          — {}",
            mark(
                state
                    .project_name
                    .as_deref()
                    .map(str::trim)
                    .is_some_and(|s| !s.is_empty())
            ),
            summarize_opt(&state.project_name)
        ),
        action: Action::ProjectName,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Local path            — {}",
            mark(state.local_path.is_some()),
            summarize_opt(&state.local_path)
        ),
        action: Action::LocalPath,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Repository URL        — {}",
            mark(
                state
                    .repo_url
                    .as_deref()
                    .map(str::trim)
                    .is_some_and(|s| !s.is_empty())
            ),
            summarize_opt(&state.repo_url)
        ),
        action: Action::RepoUrl,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Profile               — {}",
            mark(state.profile.is_some()),
            state.profile.clone().unwrap_or_else(|| "(none)".into())
        ),
        action: Action::Profile,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Goal                  — {}",
            mark(
                state
                    .goal
                    .as_deref()
                    .map(str::trim)
                    .is_some_and(|s| !s.is_empty())
            ),
            summarize_opt(&state.goal)
        ),
        action: Action::Goal,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Success criteria      — {}",
            mark(!state.success_criteria.is_empty()),
            summarize_list(&state.success_criteria)
        ),
        action: Action::SuccessCriteria,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Non-goals             — {}",
            mark(!state.non_goals.is_empty()),
            summarize_list(&state.non_goals)
        ),
        action: Action::NonGoals,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Languages             — {}",
            mark(
                state
                    .languages
                    .as_deref()
                    .map(str::trim)
                    .is_some_and(|s| !s.is_empty())
            ),
            summarize_opt(&state.languages)
        ),
        action: Action::Languages,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Must use              — {}",
            mark(
                state
                    .must_use
                    .as_deref()
                    .map(str::trim)
                    .is_some_and(|s| !s.is_empty())
            ),
            summarize_opt(&state.must_use)
        ),
        action: Action::MustUse,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Must avoid            — {}",
            mark(
                state
                    .must_avoid
                    .as_deref()
                    .map(str::trim)
                    .is_some_and(|s| !s.is_empty())
            ),
            summarize_opt(&state.must_avoid)
        ),
        action: Action::MustAvoid,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Platforms             — {}",
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
        label: format!("[✓] Harness (agent runtime) — {}", state.harness),
        action: Action::Harness,
    });
    items.push(MenuItem {
        label: format!("[✓] Merge mode          — {}", state.merge_mode),
        action: Action::MergeMode,
    });
    items.push(MenuItem {
        label: format!("[✓] Work branch         — {}", state.work_branch),
        action: Action::WorkBranch,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Sprint 0 charter      — {}",
            mark(
                state
                    .sprint_zero_charter
                    .as_deref()
                    .map(str::trim)
                    .is_some_and(|s| !s.is_empty())
            ),
            summarize_opt(&state.sprint_zero_charter)
        ),
        action: Action::SprintZeroCharter,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Backlog seeds         — {}",
            mark(!state.backlog_seeds.is_empty()),
            summarize_list(&state.backlog_seeds)
        ),
        action: Action::BacklogSeeds,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Extra stop-checkpoints — {}",
            mark(!state.working_agreement_notes.is_empty()),
            summarize_list(&state.working_agreement_notes)
        ),
        action: Action::WorkingAgreementNotes,
    });
    items.push(MenuItem {
        label: format!(
            "[{}] Seed project (ADR-000 + backlog + confidence.txt)",
            mark(state.seed)
        ),
        action: Action::ToggleSeed,
    });
    items.push(MenuItem {
        label: "────────  Preview mission-spec.md + launch-prompt.md".to_string(),
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
        state.project_name = if trimmed.is_empty() {
            None
        } else {
            Some(trimmed.to_string())
        };
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
        state.local_path = if trimmed.is_empty() {
            None
        } else {
            Some(trimmed.to_string())
        };
        // Auto-detect repo URL / work branch from git, without overwriting
        // anything the user already typed in explicitly.
        if let Some(path) = &state.local_path {
            let env = scaffold::detect_environment(std::path::Path::new(path));
            if state.repo_url.is_none() {
                state.repo_url = env.git_remote;
            }
            if state.work_branch == "dev" {
                if let Some(b) = env.git_branch {
                    state.work_branch = b;
                }
            }
        }
    }
    Ok(())
}

fn edit_repo_url(state: &mut WizardState) -> Result<(), WizardError> {
    let val = Text::new("Repository URL (optional):")
        .with_default(state.repo_url.as_deref().unwrap_or(""))
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.repo_url = if trimmed.is_empty() {
            None
        } else {
            Some(trimmed.to_string())
        };
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
        .and_then(|k| {
            options
                .iter()
                .find(|o| o.starts_with(&format!("{k} —")))
                .cloned()
        })
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
        let prefill = Confirm::new("Pre-fill empty fields (languages, platforms, criteria, must-use, must-avoid) from this profile?")
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
    let val = Text::new("Goal (the full mission — not a one-liner):")
        .with_default(state.goal.as_deref().unwrap_or(""))
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.goal = if trimmed.is_empty() {
            None
        } else {
            Some(trimmed.to_string())
        };
    }
    Ok(())
}

fn edit_success_criteria(
    state: &mut WizardState,
    profiles: &ProfileManager,
) -> Result<(), WizardError> {
    loop {
        print_current_list("Current criteria", &state.success_criteria);

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
            "Clear all" => state.success_criteria.clear(),
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

/// Generic repeating list editor for non-goals, backlog seeds, and extra
/// stop-checkpoints — sections with no profile-suggested defaults.
fn edit_string_list(list: &mut Vec<String>, noun: &str) -> Result<(), WizardError> {
    loop {
        print_current_list(&format!("Current {noun}s"), list);

        let mut options = vec![format!("Add {noun}")];
        if !list.is_empty() {
            options.push(format!("Remove {noun}"));
            options.push("Clear all".to_string());
        }
        options.push("Back to menu".to_string());

        let pick = Select::new(&format!("{noun}s:",), options).prompt_skippable()?;
        let Some(pick) = pick else { return Ok(()) };
        if pick == format!("Add {noun}") {
            if let Some(v) = Text::new(&format!("New {noun}:")).prompt_skippable()? {
                let trimmed = v.trim();
                if !trimmed.is_empty() {
                    list.push(trimmed.to_string());
                }
            }
        } else if pick == format!("Remove {noun}") {
            let idx = Select::new("Remove which?", list.clone()).prompt_skippable()?;
            if let Some(item) = idx {
                list.retain(|c| c != &item);
            }
        } else if pick == "Clear all" {
            list.clear();
        } else {
            return Ok(());
        }
    }
}

fn print_current_list(label: &str, items: &[String]) {
    let current = if items.is_empty() {
        "  (none)".to_string()
    } else {
        items
            .iter()
            .enumerate()
            .map(|(i, c)| format!("  {}. {}", i + 1, c))
            .collect::<Vec<_>>()
            .join("\n")
    };
    println!("\n{label}:\n{current}\n");
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
        state.languages = if trimmed.is_empty() {
            None
        } else {
            Some(trimmed.to_string())
        };
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
        state.must_use = if trimmed.is_empty() {
            None
        } else {
            Some(trimmed.to_string())
        };
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
        state.must_avoid = if trimmed.is_empty() {
            None
        } else {
            Some(trimmed.to_string())
        };
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

fn edit_harness(state: &mut WizardState) -> Result<(), WizardError> {
    let options: Vec<String> = HARNESSES
        .iter()
        .map(|(_, key, desc)| format!("{key} — {desc}"))
        .collect();
    let cursor = HARNESSES
        .iter()
        .position(|(h, ..)| *h == state.harness)
        .unwrap_or(0);
    let pick = Select::new("Agent runtime (harness):", options)
        .with_starting_cursor(cursor)
        .prompt_skippable()?;
    if let Some(pick) = pick {
        if let Some((h, ..)) = HARNESSES
            .iter()
            .find(|(_, key, desc)| format!("{key} — {desc}") == pick)
        {
            state.harness = *h;
        }
    }
    Ok(())
}

fn edit_merge_mode(state: &mut WizardState) -> Result<(), WizardError> {
    let options: Vec<String> = MERGE_MODES
        .iter()
        .map(|(_, key, desc)| format!("{key} — {desc}"))
        .collect();
    let cursor = MERGE_MODES
        .iter()
        .position(|(m, ..)| *m == state.merge_mode)
        .unwrap_or(0);
    let pick = Select::new("Merge mode:", options)
        .with_starting_cursor(cursor)
        .prompt_skippable()?;
    if let Some(pick) = pick {
        if let Some((m, ..)) = MERGE_MODES
            .iter()
            .find(|(_, key, desc)| format!("{key} — {desc}") == pick)
        {
            state.merge_mode = *m;
        }
    }
    Ok(())
}

fn edit_work_branch(state: &mut WizardState) -> Result<(), WizardError> {
    let val = Text::new("Long-lived work branch sprints develop on:")
        .with_default(&state.work_branch)
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        if !trimmed.is_empty() {
            state.work_branch = trimmed.to_string();
        }
    }
    Ok(())
}

fn edit_sprint_zero_charter(state: &mut WizardState) -> Result<(), WizardError> {
    let val = Text::new("What should Sprint 0 specifically research and build first?")
        .with_default(state.sprint_zero_charter.as_deref().unwrap_or(""))
        .prompt_skippable()?;
    if let Some(v) = val {
        let trimmed = v.trim();
        state.sprint_zero_charter = if trimmed.is_empty() {
            None
        } else {
            Some(trimmed.to_string())
        };
    }
    Ok(())
}

fn show_preview(state: &WizardState, profiles: &ProfileManager) -> Result<(), WizardError> {
    let (spec_doc, prompt) = render_preview(state, profiles)?;
    println!();
    println!("────────────────────── mission-spec.md preview ──────────────────────");
    println!("{spec_doc}");
    println!("────────────────────── launch-prompt.md preview ─────────────────────");
    println!("{prompt}");
    println!("────────────────────────────────────────────────────────────────────");
    println!();
    let _ = Text::new("Press Enter to return to the menu…")
        .with_default("")
        .prompt_skippable()?;
    Ok(())
}

fn render_preview(
    state: &WizardState,
    profiles: &ProfileManager,
) -> Result<(String, String), WizardError> {
    let created = today();
    let spec = state.to_spec(profiles, &created);
    let backlog_seeds: Vec<BacklogSeed> = scaffold::assign_backlog_ids(&spec.backlog_seeds, "");
    let doc = scaffold::render_spec_document(&spec, &backlog_seeds)?;
    let prompt = scaffold::render_prompt(&spec)?;
    Ok((doc, prompt))
}

fn today() -> String {
    scaffold::today()
}

fn save(
    state: &WizardState,
    profiles: &ProfileManager,
) -> Result<Option<WizardOutcome>, WizardError> {
    if state
        .project_name
        .as_deref()
        .map(str::trim)
        .unwrap_or("")
        .is_empty()
    {
        println!("  ⚠ Project name is empty — set it before saving.");
        let _ = Text::new("Press Enter to return to the menu…")
            .with_default("")
            .prompt_skippable()?;
        return Ok(None);
    }
    if state
        .goal
        .as_deref()
        .map(str::trim)
        .unwrap_or("")
        .is_empty()
    {
        println!("  ⚠ Goal is empty — set it before saving.");
        let _ = Text::new("Press Enter to return to the menu…")
            .with_default("")
            .prompt_skippable()?;
        return Ok(None);
    }

    let default_dir = state
        .local_path
        .clone()
        .or_else(|| {
            std::env::current_dir()
                .ok()
                .and_then(|p| p.to_str().map(str::to_string))
        })
        .unwrap_or_else(|| ".".to_string());
    let path = Text::new("Launch into which project directory?")
        .with_default(&default_dir)
        .prompt_skippable()?;
    let Some(path) = path else { return Ok(None) };
    let pb = PathBuf::from(&path);

    let created = today();
    let spec = state.to_spec(profiles, &created);
    spec::validate(&spec)?;

    if state.seed {
        let report = scaffold::launch_project(&pb, &spec)?;
        println!("\n✓ wrote {}", report.spec_path.display());
        println!("✓ wrote {}", report.prompt_path.display());
        if report.seed.decisions_written {
            println!("✓ seeded decisions.md (ADR-000)");
        }
        for s in &report.seed.backlog_written {
            println!("✓ seeded agent-tasks.md: T-{} {}", s.id, s.description);
        }
        if report.seed.confidence_written {
            println!("✓ seeded confidence.txt (1.0)");
        }
        Ok(Some(WizardOutcome::Launched(report.spec_path)))
    } else {
        std::fs::create_dir_all(&pb)?;
        let backlog_seeds: Vec<BacklogSeed> = scaffold::assign_backlog_ids(&spec.backlog_seeds, "");
        let spec_path = scaffold::write_spec(&pb, &spec, &backlog_seeds)?;
        let prompt_path = scaffold::write_prompt(&pb, &spec)?;
        println!("\n✓ wrote {}", spec_path.display());
        println!("✓ wrote {} (seeding skipped)", prompt_path.display());
        Ok(Some(WizardOutcome::Launched(spec_path)))
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
    #[error("scaffold error: {0}")]
    Scaffold(#[from] geck_core::scaffold::ScaffoldError),
    #[error("validation error: {0}")]
    Validation(#[from] geck_core::spec::ValidationError),
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
}
