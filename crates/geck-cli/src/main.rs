//! `geck` — CLI front-end for the GECK protocol toolchain.

mod wizard;

use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Parser, Subcommand};

use geck_core::profiles::ProfileManager;
use geck_core::scaffold::{self, InitConfig};
use geck_core::templates::{RenderContext, TemplateEngine, BUILTIN_NAMES};

#[derive(Parser, Debug)]
#[command(
    name = "geck",
    version,
    about = "GECK protocol toolchain (v1.3)",
    long_about = "Generate and manage GECK projects. Targets protocol version v1.3."
)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Print the GECK protocol version this binary targets.
    ProtocolVersion,

    /// List all built-in profiles.
    ListProfiles {
        /// Emit machine-readable JSON instead of a human table.
        #[arg(long)]
        json: bool,
    },

    /// List all built-in templates.
    ListTemplates,

    /// Render an LLM_init.md from flags to stdout, or launch the interactive
    /// wizard when called with no other arguments.
    Generate(GenerateArgs),

    /// Scaffold a full GECK/ folder in the given project directory.
    Init(InitArgs),
}

#[derive(clap::Args, Debug)]
struct GenerateArgs {
    /// Project name. Omit together with `--goal` to launch the wizard.
    #[arg(long)]
    project_name: Option<String>,

    /// One-line goal for the project. Omit together with `--project-name` to
    /// launch the wizard.
    #[arg(long)]
    goal: Option<String>,

    /// Preset profile to merge into the config (e.g. `cli_tool`).
    #[arg(long)]
    profile: Option<String>,

    /// Repeatable success criterion.
    #[arg(long = "criterion", value_name = "TEXT")]
    criteria: Vec<String>,

    /// Repeatable framework.
    #[arg(long = "framework", value_name = "NAME")]
    frameworks: Vec<String>,

    /// Repeatable target platform.
    #[arg(long = "platform", value_name = "NAME")]
    platforms: Vec<String>,

    /// Free-text languages list.
    #[arg(long)]
    languages: Option<String>,

    /// Must-use constraints.
    #[arg(long)]
    must_use: Option<String>,

    /// Must-avoid constraints.
    #[arg(long)]
    must_avoid: Option<String>,

    /// Context budget: small | medium | large.
    #[arg(long, default_value = "medium")]
    context_budget: String,

    /// Write to this path instead of stdout.
    #[arg(long, value_name = "PATH")]
    output: Option<PathBuf>,
}

#[derive(clap::Args, Debug)]
struct InitArgs {
    /// Project root (the folder that will get a `GECK/` subfolder).
    #[arg(value_name = "PROJECT_PATH")]
    path: PathBuf,

    /// Project name.
    #[arg(long)]
    project_name: String,

    /// One-line goal for the project.
    #[arg(long)]
    goal: String,

    /// Preset profile to merge in.
    #[arg(long)]
    profile: Option<String>,

    #[arg(long = "criterion", value_name = "TEXT")]
    criteria: Vec<String>,

    #[arg(long = "framework", value_name = "NAME")]
    frameworks: Vec<String>,

    #[arg(long = "platform", value_name = "NAME")]
    platforms: Vec<String>,

    #[arg(long)]
    context_budget: Option<String>,
}

fn main() -> ExitCode {
    let cli = Cli::parse();
    match cli.command {
        Some(Commands::ProtocolVersion) => {
            println!("{}", geck_core::PROTOCOL_VERSION);
            ExitCode::SUCCESS
        }
        Some(Commands::ListProfiles { json }) => run_list_profiles(json),
        Some(Commands::ListTemplates) => run_list_templates(),
        Some(Commands::Generate(args)) => run_generate(args),
        Some(Commands::Init(args)) => run_init(args),
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

fn run_list_templates() -> ExitCode {
    for name in BUILTIN_NAMES {
        println!("{name}");
    }
    ExitCode::SUCCESS
}

fn run_generate(args: GenerateArgs) -> ExitCode {
    // If neither project-name nor goal was supplied, launch the wizard.
    // Any non-default arg forces the non-interactive path and errors if
    // project-name/goal are still missing.
    let has_other_args = args.profile.is_some()
        || !args.criteria.is_empty()
        || !args.frameworks.is_empty()
        || !args.platforms.is_empty()
        || args.languages.is_some()
        || args.must_use.is_some()
        || args.must_avoid.is_some()
        || args.context_budget != "medium"
        || args.output.is_some();

    if args.project_name.is_none() && args.goal.is_none() && !has_other_args {
        return match wizard::run() {
            Ok(wizard::WizardOutcome::Cancelled) => {
                println!("wizard cancelled — nothing written");
                ExitCode::SUCCESS
            }
            Ok(_) => ExitCode::SUCCESS,
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

    let mut config = InitConfig {
        project_name: Some(project_name),
        goal: Some(goal),
        success_criteria: args.criteria,
        frameworks: args.frameworks,
        platforms: args.platforms,
        languages: args.languages,
        must_use: args.must_use,
        must_avoid: args.must_avoid,
        context_budget: Some(args.context_budget),
        ..Default::default()
    };

    if let Some(profile) = &args.profile {
        if let Err(e) = ProfileManager::new().apply(&mut config, profile) {
            eprintln!("geck: {e}");
            return ExitCode::FAILURE;
        }
    }

    let env = scaffold::detect_environment();
    let engine = TemplateEngine::new();
    let mut ctx = RenderContext::new();
    ctx.insert("project_name", config.project_name.as_deref().unwrap_or(""));
    ctx.insert("goal", config.goal.as_deref().unwrap_or(""));
    ctx.insert("created_date", &env.created_date);
    ctx.insert("success_criteria", &config.success_criteria);
    ctx.insert("frameworks", &config.frameworks);
    ctx.insert("platforms", &config.platforms);
    ctx.insert(
        "context_budget",
        config.context_budget.as_deref().unwrap_or("medium"),
    );
    if let Some(v) = &config.languages {
        ctx.insert("languages", v);
    }
    if let Some(v) = &config.must_use {
        ctx.insert("must_use", v);
    }
    if let Some(v) = &config.must_avoid {
        ctx.insert("must_avoid", v);
    }

    let rendered = match engine.render("llm_init", &ctx) {
        Ok(s) => s,
        Err(e) => {
            eprintln!("geck: {e}");
            return ExitCode::FAILURE;
        }
    };

    if let Some(path) = args.output {
        if let Some(parent) = path.parent() {
            if !parent.as_os_str().is_empty() {
                if let Err(e) = std::fs::create_dir_all(parent) {
                    eprintln!("geck: failed to create {}: {e}", parent.display());
                    return ExitCode::FAILURE;
                }
            }
        }
        if let Err(e) = std::fs::write(&path, rendered) {
            eprintln!("geck: failed to write {}: {e}", path.display());
            return ExitCode::FAILURE;
        }
    } else {
        print!("{rendered}");
    }
    ExitCode::SUCCESS
}

fn run_init(args: InitArgs) -> ExitCode {
    let mut config = InitConfig {
        project_name: Some(args.project_name),
        goal: Some(args.goal),
        success_criteria: args.criteria,
        frameworks: args.frameworks,
        platforms: args.platforms,
        context_budget: args.context_budget,
        ..Default::default()
    };

    if let Some(profile) = &args.profile {
        if let Err(e) = ProfileManager::new().apply(&mut config, profile) {
            eprintln!("geck: {e}");
            return ExitCode::FAILURE;
        }
    }

    let env = scaffold::detect_environment();
    match scaffold::init_geck_folder(&args.path, &config, &env) {
        Ok(p) => {
            println!("{}", p.display());
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("geck: {e}");
            ExitCode::FAILURE
        }
    }
}
