//! geck-core — shared library for GECK protocol v1.3 tooling.
//!
//! Module layout (modules are stubs in Phase 1; filled in subsequent phases):
//! - [`tasks`]: typed task records (`TASK-NNN`).
//! - [`log_index`]: JSONL log-index records.
//! - [`decisions`] / [`learnings`]: per-record artifacts with YAML frontmatter.
//! - [`templates`]: embedded v1.3 templates rendered via Tera.
//! - [`profiles`]: profile registry mirrored from the Python reference impl.
//! - [`scaffold`]: GECK folder initialization.
//! - [`validate`]: config validation.

pub mod tasks;
pub mod log_index;
pub mod decisions;
pub mod learnings;
pub mod frontmatter;
pub mod templates;
pub mod profiles;
pub mod scaffold;
pub mod validate;

/// GECK protocol version this library targets.
pub const PROTOCOL_VERSION: &str = "1.3";

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn protocol_version_is_v13() {
        assert_eq!(PROTOCOL_VERSION, "1.3");
    }
}
