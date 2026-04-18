//! Append-only JSONL log index for GECK v1.3.
//!
//! One record per line in `GECK/log_index.jsonl`. Each record summarizes a
//! coherent chunk of agent activity: touched tasks/decisions/learnings/files,
//! terminal turn state, and a one-line summary.

use serde::{Deserialize, Serialize};
use thiserror::Error;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "UPPERCASE")]
pub enum LogState {
    Continue,
    Wait,
    Rollback,
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct LogIndexRecord {
    pub id: u64,
    pub ts: String,
    #[serde(default)]
    pub tasks: Vec<String>,
    #[serde(default)]
    pub decisions: Vec<String>,
    #[serde(default)]
    pub learnings: Vec<String>,
    #[serde(default)]
    pub files: Vec<String>,
    pub state: LogState,
    pub summary: String,
}

#[derive(Debug, Error)]
pub enum LogIndexError {
    #[error("failed to parse JSONL line {line}: {source}")]
    Parse {
        line: usize,
        #[source]
        source: serde_json::Error,
    },
    #[error("failed to serialize record: {0}")]
    Serialize(#[from] serde_json::Error),
}

/// Parse a full `log_index.jsonl` file into records. Blank lines are ignored.
pub fn parse_jsonl(input: &str) -> Result<Vec<LogIndexRecord>, LogIndexError> {
    input
        .lines()
        .enumerate()
        .filter(|(_, l)| !l.trim().is_empty())
        .map(|(i, l)| {
            serde_json::from_str(l).map_err(|source| LogIndexError::Parse { line: i + 1, source })
        })
        .collect()
}

/// Render records as a `log_index.jsonl` body, one JSON object per line.
pub fn render_jsonl(records: &[LogIndexRecord]) -> Result<String, LogIndexError> {
    let mut out = String::new();
    for r in records {
        out.push_str(&serde_json::to_string(r)?);
        out.push('\n');
    }
    Ok(out)
}

#[cfg(test)]
mod tests {
    use super::*;

    const V13_INIT_LINE: &str = r#"{"id":0,"ts":"2026-04-17T00:00:00Z","tasks":[],"decisions":[],"learnings":[],"files":["GECK/*"],"state":"WAIT","summary":"GECK v1.3 initialized"}"#;

    #[test]
    fn parses_v13_init_record() {
        let records = parse_jsonl(V13_INIT_LINE).unwrap();
        assert_eq!(records.len(), 1);
        let r = &records[0];
        assert_eq!(r.id, 0);
        assert_eq!(r.state, LogState::Wait);
        assert_eq!(r.files, vec!["GECK/*"]);
        assert_eq!(r.summary, "GECK v1.3 initialized");
        assert!(r.tasks.is_empty());
    }

    #[test]
    fn roundtrip_preserves_record() {
        let records = parse_jsonl(V13_INIT_LINE).unwrap();
        let rendered = render_jsonl(&records).unwrap();
        let reparsed = parse_jsonl(&rendered).unwrap();
        assert_eq!(records, reparsed);
    }

    #[test]
    fn state_serializes_uppercase() {
        let r = LogIndexRecord {
            id: 7,
            ts: "2026-04-17T12:34:56Z".into(),
            tasks: vec!["TASK-001".into()],
            decisions: vec![],
            learnings: vec![],
            files: vec!["src/main.rs".into()],
            state: LogState::Continue,
            summary: "wired up cli".into(),
        };
        let s = serde_json::to_string(&r).unwrap();
        assert!(s.contains(r#""state":"CONTINUE""#), "got {s}");
    }

    #[test]
    fn ignores_blank_lines() {
        let body = format!("\n{V13_INIT_LINE}\n\n");
        let records = parse_jsonl(&body).unwrap();
        assert_eq!(records.len(), 1);
    }

    #[test]
    fn reports_line_number_on_parse_error() {
        let body = format!("{V13_INIT_LINE}\nnot json\n");
        let err = parse_jsonl(&body).unwrap_err();
        match err {
            LogIndexError::Parse { line, .. } => assert_eq!(line, 2),
            other => panic!("unexpected error: {other:?}"),
        }
    }
}
