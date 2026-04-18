//! Learning records (`GECK/learnings/LRN-NNN-*.md`).
//!
//! Format (GECK v1.3):
//!
//! ```markdown
//! ---
//! id: LRN-001
//! title: Cargo workspaces speed up edits
//! date: 2026-04-17
//! related-tasks: [TASK-001]
//! ---
//!
//! # Observation
//! ...
//! ```

use serde::{Deserialize, Serialize};

use crate::frontmatter::{self, FrontmatterError};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct LearningFrontmatter {
    pub id: String,
    pub title: String,
    pub date: String,
    #[serde(default, rename = "related-tasks")]
    pub related_tasks: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LearningRecord {
    pub frontmatter: LearningFrontmatter,
    pub body: String,
}

pub fn parse(input: &str) -> Result<LearningRecord, FrontmatterError> {
    let (yaml, body) = frontmatter::split(input)?;
    let fm: LearningFrontmatter = serde_yaml::from_str(yaml)?;
    Ok(LearningRecord {
        frontmatter: fm,
        body: body.to_string(),
    })
}

pub fn render(record: &LearningRecord) -> Result<String, serde_yaml::Error> {
    let yaml = serde_yaml::to_string(&record.frontmatter)?;
    Ok(frontmatter::join(&yaml, &record.body))
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = "---\nid: LRN-001\ntitle: Workspaces help\ndate: 2026-04-17\nrelated-tasks:\n- TASK-001\n- TASK-002\n---\n# Observation\n\nShared deps.\n";

    #[test]
    fn parses_sample() {
        let r = parse(SAMPLE).unwrap();
        assert_eq!(r.frontmatter.id, "LRN-001");
        assert_eq!(r.frontmatter.related_tasks.len(), 2);
        assert!(r.body.starts_with("# Observation"));
    }

    #[test]
    fn roundtrip_preserves_fields() {
        let r = parse(SAMPLE).unwrap();
        let rendered = render(&r).unwrap();
        let reparsed = parse(&rendered).unwrap();
        assert_eq!(r, reparsed);
    }
}
