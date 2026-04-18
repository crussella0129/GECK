//! Decision records (`GECK/decisions/DEC-NNN-*.md`).
//!
//! Format (GECK v1.3):
//!
//! ```markdown
//! ---
//! id: DEC-001
//! title: Adopt Rust for tooling
//! date: 2026-04-17
//! status: accepted
//! related-tasks: [TASK-001]
//! related-decisions: []
//! superseded-by: null
//! ---
//!
//! # Context
//! ...
//! ```

use serde::{Deserialize, Serialize};

use crate::frontmatter::{self, FrontmatterError};

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum DecisionStatus {
    Proposed,
    Accepted,
    Rejected,
    Superseded,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct DecisionFrontmatter {
    pub id: String,
    pub title: String,
    pub date: String,
    pub status: DecisionStatus,
    #[serde(default, rename = "related-tasks")]
    pub related_tasks: Vec<String>,
    #[serde(default, rename = "related-decisions")]
    pub related_decisions: Vec<String>,
    #[serde(default, rename = "superseded-by")]
    pub superseded_by: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DecisionRecord {
    pub frontmatter: DecisionFrontmatter,
    pub body: String,
}

pub fn parse(input: &str) -> Result<DecisionRecord, FrontmatterError> {
    let (yaml, body) = frontmatter::split(input)?;
    let fm: DecisionFrontmatter = serde_yaml::from_str(yaml)?;
    Ok(DecisionRecord {
        frontmatter: fm,
        body: body.to_string(),
    })
}

pub fn render(record: &DecisionRecord) -> Result<String, serde_yaml::Error> {
    let yaml = serde_yaml::to_string(&record.frontmatter)?;
    Ok(frontmatter::join(&yaml, &record.body))
}

#[cfg(test)]
mod tests {
    use super::*;

    const SAMPLE: &str = "---\nid: DEC-001\ntitle: Adopt Rust\ndate: 2026-04-17\nstatus: accepted\nrelated-tasks:\n- TASK-001\nrelated-decisions: []\nsuperseded-by: null\n---\n# Context\n\nGo fast.\n";

    #[test]
    fn parses_sample() {
        let r = parse(SAMPLE).unwrap();
        assert_eq!(r.frontmatter.id, "DEC-001");
        assert_eq!(r.frontmatter.status, DecisionStatus::Accepted);
        assert_eq!(r.frontmatter.related_tasks, vec!["TASK-001"]);
        assert_eq!(r.frontmatter.superseded_by, None);
        assert!(r.body.starts_with("# Context"));
    }

    #[test]
    fn roundtrip_preserves_fields() {
        let r = parse(SAMPLE).unwrap();
        let rendered = render(&r).unwrap();
        let reparsed = parse(&rendered).unwrap();
        assert_eq!(r, reparsed);
    }
}
