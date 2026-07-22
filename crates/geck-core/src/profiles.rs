//! Profile registry — presets that seed a [`MissionSpec`]'s constraints and
//! suggested success criteria for a common project shape (web app, CLI
//! tool, data science, etc.).

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::spec::MissionSpec;

const PROFILES_JSON: &str = include_str!("../data/profiles.json");

/// Single project profile (web_app, cli_tool, etc.).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Profile {
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub languages: Option<String>,
    #[serde(default)]
    pub frameworks: Vec<String>,
    #[serde(default)]
    pub platforms: Vec<String>,
    #[serde(default)]
    pub suggested_criteria: Vec<String>,
    #[serde(default)]
    pub suggested_must_use: Option<String>,
    #[serde(default)]
    pub suggested_must_avoid: Option<String>,
}

/// Category grouping for menu navigation.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Category {
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub profiles: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct RawRegistry {
    profiles: BTreeMap<String, Profile>,
    categories: BTreeMap<String, Category>,
}

#[derive(Debug, Error)]
pub enum ProfileError {
    #[error("profile not found: {0}")]
    Unknown(String),
    #[error("invalid profile data: {0}")]
    Invalid(#[from] serde_json::Error),
}

pub struct ProfileManager {
    profiles: BTreeMap<String, Profile>,
    categories: BTreeMap<String, Category>,
}

impl ProfileManager {
    pub fn new() -> Self {
        Self::from_json(PROFILES_JSON).expect("bundled profiles.json must parse")
    }

    pub fn from_json(src: &str) -> Result<Self, ProfileError> {
        let raw: RawRegistry = serde_json::from_str(src)?;
        Ok(Self {
            profiles: raw.profiles,
            categories: raw.categories,
        })
    }

    pub fn get(&self, name: &str) -> Result<&Profile, ProfileError> {
        self.profiles
            .get(name)
            .ok_or_else(|| ProfileError::Unknown(name.to_string()))
    }

    pub fn list(&self) -> Vec<&str> {
        self.profiles.keys().map(String::as_str).collect()
    }

    pub fn list_with_descriptions(&self) -> Vec<(&str, &str, &str)> {
        self.profiles
            .iter()
            .map(|(k, p)| (k.as_str(), p.name.as_str(), p.description.as_str()))
            .collect()
    }

    pub fn categories(&self) -> &BTreeMap<String, Category> {
        &self.categories
    }

    /// Merge a profile into a spec's constraints. Profile values fill only
    /// missing fields — explicit fields on `spec` are preserved.
    pub fn apply(&self, spec: &mut MissionSpec, profile_name: &str) -> Result<(), ProfileError> {
        let profile = self.get(profile_name)?;
        if spec.languages.is_none() {
            spec.languages = profile.languages.clone();
        }
        if spec.frameworks.is_empty() {
            spec.frameworks = profile.frameworks.clone();
        }
        if spec.platforms.is_empty() {
            spec.platforms = profile.platforms.clone();
        }
        if spec.success_criteria.is_empty() {
            spec.success_criteria = profile.suggested_criteria.clone();
        }
        if spec.must_use.is_none() {
            spec.must_use = profile.suggested_must_use.clone();
        }
        if spec.must_avoid.is_none() {
            spec.must_avoid = profile.suggested_must_avoid.clone();
        }
        Ok(())
    }
}

impl Default for ProfileManager {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::spec::{Harness, MergeMode, SpecFrontmatter};

    fn empty_spec() -> MissionSpec {
        MissionSpec {
            frontmatter: SpecFrontmatter {
                geck: "2.0".into(),
                project: "Demo".into(),
                created: "2026-07-21".into(),
                profile: None,
                harness: Harness::ClaudeCode,
                merge_mode: MergeMode::Approve,
                work_branch: "dev".into(),
                repo: None,
                sprint_loops_ref: None,
            },
            goal: "x".into(),
            success_criteria: vec![],
            non_goals: vec![],
            languages: None,
            frameworks: vec![],
            platforms: vec![],
            must_use: None,
            must_avoid: None,
            working_agreement_notes: vec![],
            sprint_zero_charter: String::new(),
            backlog_seeds: vec![],
        }
    }

    #[test]
    fn bundled_registry_parses() {
        let m = ProfileManager::new();
        assert!(m.list().contains(&"website"));
        assert!(m.list().contains(&"cli_tool"));
        assert!(m.categories().contains_key("web"));
    }

    #[test]
    fn unknown_profile_errors() {
        let m = ProfileManager::new();
        assert!(matches!(
            m.get("not-a-real-profile"),
            Err(ProfileError::Unknown(_))
        ));
    }

    #[test]
    fn apply_fills_missing_fields() {
        let m = ProfileManager::new();
        let mut spec = empty_spec();
        m.apply(&mut spec, "cli_tool").unwrap();
        assert_eq!(spec.languages.as_deref(), Some("Python 3.11+"));
        assert!(!spec.frameworks.is_empty());
        assert!(spec.platforms.contains(&"Linux".to_string()));
        assert!(!spec.success_criteria.is_empty());
        assert!(spec.must_use.is_some());
        assert!(spec.must_avoid.is_some());
    }

    #[test]
    fn apply_preserves_explicit_fields() {
        let m = ProfileManager::new();
        let mut spec = empty_spec();
        spec.languages = Some("Rust".into());
        spec.frameworks = vec!["tokio".into()];
        m.apply(&mut spec, "cli_tool").unwrap();
        assert_eq!(spec.languages.as_deref(), Some("Rust"));
        assert_eq!(spec.frameworks, vec!["tokio".to_string()]);
        // Empty fields still get filled from the profile
        assert!(!spec.success_criteria.is_empty());
    }

    #[test]
    fn website_profile_has_expected_shape() {
        let m = ProfileManager::new();
        let p = m.get("website").unwrap();
        assert_eq!(p.name, "Website");
        assert!(p.frameworks.contains(&"Astro".to_string()));
        assert!(p.platforms.contains(&"Web".to_string()));
    }
}
