//! `geck` — Sprint Zero launcher for Animus Sprint Loops.
//!
//! Generates `mission-spec.md` (the durable mission document — the drift
//! baseline every sprint compares against) and `launch-prompt.md` (the
//! complete prompt that starts Sprint 0 with full context), and seeds the
//! target project's `decisions.md` / `agent-tasks/` / `confidence.txt`.

mod wizard;

use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Parser, Subcommand};

use geck_core::profiles::ProfileManager;
use geck_core::scaffold::{self, BacklogSeed};
use geck_core::spec::{self, Harness, MergeMode, MissionSpec, SpecFrontmatter};

#[derive(Parser, Debug)]
#[command(
    name = "geck",
    version,
    about = "Sprint Zero launcher for Animus Sprint Loops",
    long_about = "Generate mission-spec.md + launch-prompt.md and seed a project so \
                  Sprint 0 starts with full mission context. Targets spec format v2.0."
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Print the mission-spec format version this binary targets.
    SpecVersion,

    /// List all built-in profiles.
    ListProfiles {
        /// Emit machine-readable JSON instead of a human table.
        #[arg(long)]
        json: bool,
    },

    /// Write mission-spec.md + launch-prompt.md and seed the project, or
    /// launch the interactive wizard when called with no other arguments.
    Launch(Box<LaunchArgs>),

    /// Re-render launch-prompt.md from an existing mission-spec.md.
    Prompt(PromptArgs),
}

#[derive(clap::Args, Debug)]
struct LaunchArgs {
    /// Project root to write into. Defaults to the current directory.
    #[arg(long, value_name = "PATH", default_value = ".")]
    path: PathBuf,

    /// Project name. Omit together with `--goal` to launch the wizard.
    #[arg(long)]
    project_name: Option<String>,

    /// The mission goal, in full — not a one-liner. Omit together with
    /// `--project-name` to launch the wizard.
    #[arg(long)]
    goal: Option<String>,

    /// Preset profile to merge into the spec (e.g. `cli_tool`).
    #[arg(long)]
    profile: Option<String>,

    /// Repeatable success criterion.
    #[arg(long = "criterion", value_name = "TEXT")]
    criteria: Vec<String>,

    /// Repeatable non-goal (the anti-drift fence).
    #[arg(long = "non-goal", value_name = "TEXT")]
    non_goals: Vec<String>,

    /// Free-text languages list.
    #[arg(long)]
    languages: Option<String>,

    /// Must-use constraints.
    #[arg(long)]
    must_use: Option<String>,

    /// Must-avoid constraints.
    #[arg(long)]
    must_avoid: Option<String>,

    /// Repeatable target platform.
    #[arg(long = "platform", value_name = "NAME")]
    platforms: Vec<String>,

    /// Agent runtime the launch prompt targets.
    #[arg(long, default_value = "claude-code")]
    harness: String,

    /// approve (human approves each sprint's PR) or auto (merge on green CI).
    #[arg(long, default_value = "approve")]
    merge_mode: String,

    /// Long-lived work branch sprints develop on.
    #[arg(long, default_value = "dev")]
    work_branch: String,

    /// What Sprint 0 specifically should research and build first.
    #[arg(long, default_value = "")]
    charter: String,

    /// Repeatable backlog seed (written as T-1xx (backlog) entries).
    #[arg(long = "backlog-seed", value_name = "TEXT")]
    backlog_seeds: Vec<String>,

    /// Skip seeding decisions.md / agent-tasks/ / confidence.txt.
    #[arg(long)]
    no_seed: bool,

    /// Print both artifacts to stdout instead of writing them to disk.
    #[arg(long)]
    stdout_only: bool,
}

#[derive(clap::Args, Debug)]
struct PromptArgs {
    /// Project root containing mission-spec.md. Defaults to the current directory.
    #[arg(long, value_name = "PATH", default_value = ".")]
    path: PathBuf,

    /// Override the harness recorded in mission-spec.md's frontmatter.
    #[arg(long)]
    harness: Option<String>,

    /// Write to this path instead of project-root/launch-prompt.md.
    #[arg(long, value_name = "PATH")]
    output: Option<PathBuf>,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    match cli.command {
        Some(Commands::SpecVersion) => {
            println!("{}", geck_core::SPEC_VERSION);
            ExitCode::SUCCESS
        }
        Some(Commands::ListProfiles { json }) => run_list_profiles(json),
        Some(Commands::Launch(args)) => run_launch(*args),
        Some(Commands::Prompt(args)) => run_prompt(args),
        None => {
            use clap::CommandFactory;
            let _ = Cli::command().print_help();
            println!();
            ExitCode::SUCCESS
        }
    }
}

fn run_list_profiles(as_json: bool) -> ExitCode {
    let m = ProfileManager::new();
    if as_json {
        let rows: Vec<_> = m
            .list_with_descriptions()
            .into_iter()
            .map(|(k, n, d)| serde_json::json!({"key": k, "name": n, "description": d}))
            .collect();
        println!("{}", serde_json::to_string_pretty(&rows).unwrap());
    } else {
        for (key, name, desc) in m.list_with_descriptions() {
            println!("{key:24} {name} — {desc}");
        }
    }
    ExitCode::SUCCESS
}

fn run_launch(args: LaunchArgs) -> ExitCode {
    let has_other_args = args.profile.is_some()
        || !args.criteria.is_empty()
        || !args.non_goals.is_empty()
        || args.languages.is_some()
        || args.must_use.is_some()
        || args.must_avoid.is_some()
        || !args.platforms.is_empty()
        || args.harness != "claude-code"
        || args.merge_mode != "approve"
        || args.work_branch != "dev"
        || !args.charter.is_empty()
        || !args.backlog_seeds.is_empty()
        || args.no_seed
        || args.stdout_only;

    if args.project_name.is_none() && args.goal.is_none() && !has_other_args {
        return match wizard::run() {
            Ok(wizard::WizardOutcome::Cancelled) => {
                println!("wizard cancelled — nothing written");
                ExitCode::SUCCESS
            }
            Ok(wizard::WizardOutcome::Launched(spec_path)) => {
                println!("launched: {}", spec_path.display());
                ExitCode::SUCCESS
            }
            Err(e) => {
                eprintln!("geck: {e}");
                ExitCode::FAILURE
            }
        };
    }

    let (Some(project_name), Some(goal)) = (args.project_name, args.goal) else {
        eprintln!("geck: --project-name and --goal are required in non-interactive mode");
        eprintln!("       (omit both to launch the interactive wizard)");
        return ExitCode::FAILURE;
    };

    let harness: Harness = match args.harness.parse() {
        Ok(h) => h,
        Err(e) => {
            eprintln!("geck: {e}");
            return ExitCode::FAILURE;
        }
    };
    let merge_mode: MergeMode = match args.merge_mode.parse() {
        Ok(m) => m,
        Err(e) => {
            eprintln!("geck: {e}");
            return ExitCode::FAILURE;
        }
    };

    let env = scaffold::detect_environment(&args.path);
    let mut spec = MissionSpec {
        frontmatter: SpecFrontmatter {
            geck: geck_core::SPEC_VERSION.to_string(),
            project: project_name,
            created: env.created_date.clone(),
            profile: args.profile.clone(),
            harness,
            merge_mode,
            work_branch: args.work_branch,
            repo: env.git_remote.clone(),
            sprint_loops_ref: Some(env.created_date.clone()),
        },
        goal,
        success_criteria: args.criteria,
        non_goals: args.non_goals,
        languages: args.languages,
        frameworks: Vec::new(),
        platforms: args.platforms,
        must_use: args.must_use,
        must_avoid: args.must_avoid,
        working_agreement_notes: Vec::new(),
        sprint_zero_charter: args.charter,
        backlog_seeds: args.backlog_seeds,
    };

    if let Some(profile) = &args.profile {
        if let Err(e) = ProfileManager::new().apply(&mut spec, profile) {
            eprintln!("geck: {e}");
            return ExitCode::FAILURE;
        }
    }

    if let Err(e) = spec::validate(&spec) {
        eprintln!("geck: {e}");
        return ExitCode::FAILURE;
    }

    if args.stdout_only {
        let backlog_seeds: Vec<BacklogSeed> = scaffold::assign_backlog_ids(&spec.backlog_seeds, "");
        match (
            scaffold::render_spec_document(&spec, &backlog_seeds),
            scaffold::render_prompt(&spec),
        ) {
            (Ok(spec_doc), Ok(prompt)) => {
                println!("{spec_doc}\n---\n{prompt}");
                ExitCode::SUCCESS
            }
            (Err(e), _) | (_, Err(e)) => {
                eprintln!("geck: {e}");
                ExitCode::FAILURE
            }
        }
    } else {
        match scaffold::launch_project(&args.path, &spec) {
            Ok(report) => {
                print_launch_report(&report);
                ExitCode::SUCCESS
            }
            Err(e) => {
                eprintln!("geck: {e}");
                ExitCode::FAILURE
            }
        }
    }
}

fn print_launch_report(report: &geck_core::scaffold::LaunchReport) {
    println!("wrote {}", report.spec_path.display());
    println!("wrote {}", report.prompt_path.display());
    if report.seed.decisions_written {
        println!("seeded decisions.md (ADR-000)");
    } else {
        println!("decisions.md already has ADR-000 — skipped");
    }
    for seed in &report.seed.backlog_written {
        println!("seeded agent-tasks.md: T-{} {}", seed.id, seed.description);
    }
    for seed in &report.seed.backlog_skipped {
        println!("agent-tasks.md already has T-{} — skipped", seed.id);
    }
    if report.seed.confidence_written {
        println!("seeded confidence.txt (1.0)");
    }
}

fn run_prompt(args: PromptArgs) -> ExitCode {
    let spec_path = args.path.join("mission-spec.md");
    let document = match std::fs::read_to_string(&spec_path) {
        Ok(d) => d,
        Err(e) => {
            eprintln!("geck: failed to read {}: {e}", spec_path.display());
            return ExitCode::FAILURE;
        }
    };

    let mut source = match spec::load_for_prompt(&document) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("geck: {e}");
            return ExitCode::FAILURE;
        }
    };

    if let Some(h) = &args.harness {
        match h.parse::<Harness>() {
            Ok(h) => source.frontmatter.harness = h,
            Err(e) => {
                eprintln!("geck: {e}");
                return ExitCode::FAILURE;
            }
        }
    }

    let rendered = match scaffold::render_prompt_from_frontmatter(&source.frontmatter, &source.goal)
    {
        Ok(r) => r,
        Err(e) => {
            eprintln!("geck: {e}");
            return ExitCode::FAILURE;
        }
    };

    match args.output {
        Some(path) => {
            if let Err(e) = std::fs::write(&path, rendered) {
                eprintln!("geck: failed to write {}: {e}", path.display());
                return ExitCode::FAILURE;
            }
            println!("wrote {}", path.display());
        }
        None => {
            let out = args.path.join("launch-prompt.md");
            if let Err(e) = std::fs::write(&out, &rendered) {
                eprintln!("geck: failed to write {}: {e}", out.display());
                return ExitCode::FAILURE;
            }
            println!("wrote {}", out.display());
        }
    }
    ExitCode::SUCCESS
}
