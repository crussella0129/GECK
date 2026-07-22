//! YAML frontmatter helpers shared by decisions and learnings.
//!
//! GECK records are markdown files that begin with a YAML block delimited by
//! `---` lines:
//!
//! ```markdown
//! ---
//! id: DEC-001
//! title: Adopt Rust for tooling
//! ---
//!
//! Body goes here.
//! ```

use thiserror::Error;

#[derive(Debug, Error)]
pub enum FrontmatterError {
    #[error("missing leading `---` delimiter")]
    MissingOpen,
    #[error("missing closing `---` delimiter")]
    MissingClose,
    #[error("failed to parse YAML frontmatter: {0}")]
    Yaml(#[from] serde_yaml::Error),
}

/// Split a markdown document into (yaml_frontmatter, body).
///
/// The opening `---` must be the very first line. The closing `---` must appear
/// on its own line. The body is returned verbatim, with a single leading
/// newline stripped if present.
pub fn split(input: &str) -> Result<(&str, &str), FrontmatterError> {
    let rest = input
        .strip_prefix("---\n")
        .ok_or(FrontmatterError::MissingOpen)?;
    let close = find_closing(rest).ok_or(FrontmatterError::MissingClose)?;
    let yaml = &rest[..close];
    let after = &rest[close..];
    let body = after
        .strip_prefix("---\n")
        .or_else(|| after.strip_prefix("---"))
        .unwrap_or(after);
    Ok((yaml, body))
}

fn find_closing(rest: &str) -> Option<usize> {
    let mut offset = 0;
    for line in rest.split_inclusive('\n') {
        let trimmed = line.trim_end_matches('\n');
        if trimmed == "---" {
            return Some(offset);
        }
        offset += line.len();
    }
    None
}

/// Render a header + body into a markdown document with YAML frontmatter.
///
/// Mirrors [`split`]: the body is written flush against the closing `---\n`,
/// so `join(split(doc))` roundtrips exactly for well-formed input.
pub fn join(yaml: &str, body: &str) -> String {
    let trimmed = yaml.trim_end_matches('\n');
    format!("---\n{trimmed}\n---\n{body}")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn splits_basic_document() {
        let doc = "---\nid: DEC-001\ntitle: hi\n---\nbody line\n";
        let (yaml, body) = split(doc).unwrap();
        assert_eq!(yaml, "id: DEC-001\ntitle: hi\n");
        assert_eq!(body, "body line\n");
    }

    #[test]
    fn errors_on_missing_open() {
        assert!(matches!(
            split("id: x\n").unwrap_err(),
            FrontmatterError::MissingOpen
        ));
    }

    #[test]
    fn errors_on_missing_close() {
        assert!(matches!(
            split("---\nid: x\nno terminator\n").unwrap_err(),
            FrontmatterError::MissingClose
        ));
    }

    #[test]
    fn join_roundtrip() {
        let doc = "---\nid: DEC-001\n---\nbody\n";
        let (yaml, body) = split(doc).unwrap();
        assert_eq!(join(yaml, body), doc);
    }
}
