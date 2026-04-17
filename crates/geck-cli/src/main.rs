//! `geck` — CLI front-end for the GECK protocol toolchain.

use clap::{Parser, Subcommand};

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
}

fn main() {
    let cli = Cli::parse();
    match cli.command {
        Some(Commands::ProtocolVersion) => {
            println!("{}", geck_core::PROTOCOL_VERSION);
        }
        None => {
            // No subcommand → print help.
            use clap::CommandFactory;
            let _ = Cli::command().print_help();
            println!();
        }
    }
}
