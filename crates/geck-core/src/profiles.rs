//! Profile registry — port of `geck_generator/core/profiles.py`.
//!
//! Profile data ships as embedded JSON so Python and Rust share one source
//! of truth. [`ProfileManager`] parses on construction and exposes lookups
//! + merge-into-config semantics matching `apply_profile` in the Python impl.

use std::collections::BTreeMap;

use serde::{Deserialize, Serialize};
use thiserror::Error;

use crate::scaffold::InitConfig;

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

/// Exploration profile used by GECK Repor.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReporProfile {
    pub name: String,
    #[serde(default)]
    pub description: String,
    #[serde(default)]
    pub goals: Vec<String>,
}

#[derive(Debug, Deserialize)]
struct RawRegistry {
    profiles: BTreeMap<String, Profile>,
    categories: BTreeMap<String, Category>,
    repor_profiles: BTreeMap<String, ReporProfile>,
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
    repor: BTreeMap<String, ReporProfile>,
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
            repor: raw.repor_profiles,
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

    pub fn repor_profiles(&self) -> &BTreeMap<String, ReporProfile> {
        &self.repor
    }

    /// Merge a profile into a config. Profile values fill only missing fields —
    /// explicit fields on `config` are preserved. Matches the Python semantics.
    pub fn apply(&self, config: &mut InitConfig, profile_name: &str) -> Result<(), ProfileError> {
        let profile = self.get(profile_name)?;
        if config.languages.is_none() {
            config.languages = profile.languages.clone();
        }
        if config.frameworks.is_empty() {
            config.frameworks = profile.frameworks.clone();
        }
        if config.platforms.is_empty() {
            config.platforms = profile.platforms.clone();
        }
        if config.success_criteria.is_empty() {
            config.success_criteria = profile.suggested_criteria.clone();
        }
        if config.must_use.is_none() {
            config.must_use = profile.suggested_must_use.clone();
        }
        if config.must_avoid.is_none() {
            config.must_avoid = profile.suggested_must_avoid.clone();
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

    #[test]
    fn bundled_registry_parses() {
        let m = ProfileManager::new();
        assert!(m.list().contains(&"website"));
        assert!(m.list().contains(&"cli_tool"));
        assert!(m.categories().contains_key("web"));
        assert!(m.repor_profiles().contains_key("security_audit"));
    }

    #[test]
    fn unknown_profile_errors() {
        let m = ProfileManager::new();
        assert!(matches!(m.get("not-a-real-profile"), Err(ProfileError::Unknown(_))));
    }

    #[test]
    fn apply_fills_missing_fields() {
        let m = ProfileManager::new();
        let mut cfg = InitConfig::default();
        m.apply(&mut cfg, "cli_tool").unwrap();
        assert_eq!(cfg.languages.as_deref(), Some("Python 3.11+"));
        assert!(!cfg.frameworks.is_empty());
        assert!(cfg.platforms.contains(&"Linux".to_string()));
        assert!(!cfg.success_criteria.is_empty());
        assert!(cfg.must_use.is_some());
        assert!(cfg.must_avoid.is_some());
    }

    #[test]
    fn apply_preserves_explicit_fields() {
        let m = ProfileManager::new();
        let mut cfg = InitConfig {
            languages: Some("Rust".into()),
            frameworks: vec!["tokio".into()],
            ..Default::default()
        };
        m.apply(&mut cfg, "cli_tool").unwrap();
        assert_eq!(cfg.languages.as_deref(), Some("Rust"));
        assert_eq!(cfg.frameworks, vec!["tokio".to_string()]);
        // Empty fields still get filled from the profile
        assert!(!cfg.success_criteria.is_empty());
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
