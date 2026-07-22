//! geck-core — shared library for the GECK Sprint Zero launcher.
//!
//! GECK generates the two artifacts that start an Animus Sprint Loop with
//! full context: a durable `mission-spec.md` (the drift baseline every
//! sprint compares against) and the `launch-prompt.md` that wires it into
//! the loop.
//!
//! Module layout:
//! - [`spec`]: the [`spec::MissionSpec`] model, frontmatter round-trip, and validation.
//! - [`frontmatter`]: generic YAML-frontmatter split/join helpers.
//! - [`templates`]: embedded templates (spec, prompt, seeds) rendered via Tera.
//! - [`profiles`]: profile registry (languages/frameworks/criteria presets).
//! - [`scaffold`]: writes `mission-spec.md` + `launch-prompt.md` and seeds the project.

pub mod frontmatter;
pub mod profiles;
pub mod scaffold;
pub mod spec;
pub mod templates;

/// Mission-spec format version this library targets.
pub const SPEC_VERSION: &str = "2.0";

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn spec_version_is_2_0() {
        assert_eq!(SPEC_VERSION, "2.0");
    }
}
