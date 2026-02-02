"""Tests for geck_generator.core.profiles module."""

import pytest

from geck_generator.core.profiles import (
    ProfileManager,
    ReporProfileManager,
    PROFILES,
    REPOR_PROFILES,
)


class TestProfileManager:
    """Tests for the ProfileManager class."""

    def test_init_loads_builtin_profiles(self, profile_manager):
        """ProfileManager should load built-in profiles on init."""
        profiles = profile_manager.list_profiles()
        assert len(profiles) > 0
        assert "web_app" in profiles
        assert "cli_tool" in profiles

    def test_get_profile_returns_dict(self, profile_manager):
        """get_profile should return a profile dictionary."""
        profile = profile_manager.get_profile("web_app")
        assert isinstance(profile, dict)
        assert "name" in profile
        assert "description" in profile

    def test_get_profile_raises_keyerror_for_unknown(self, profile_manager):
        """get_profile should raise KeyError for unknown profiles."""
        with pytest.raises(KeyError):
            profile_manager.get_profile("nonexistent_profile")

    def test_list_profiles_returns_list(self, profile_manager):
        """list_profiles should return a list of profile names."""
        profiles = profile_manager.list_profiles()
        assert isinstance(profiles, list)
        assert all(isinstance(p, str) for p in profiles)

    def test_get_profile_names_with_descriptions(self, profile_manager):
        """get_profile_names_with_descriptions should return tuples."""
        result = profile_manager.get_profile_names_with_descriptions()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 3
            key, name, desc = item
            assert isinstance(key, str)
            assert isinstance(name, str)

    def test_apply_profile_merges_config(self, profile_manager):
        """apply_profile should merge profile values into config."""
        base_config = {"project_name": "Test"}
        result = profile_manager.apply_profile(base_config, "web_app")

        # Should preserve original values
        assert result["project_name"] == "Test"

        # Should add profile metadata
        assert "_profile_name" in result
        assert result["_profile_name"] == "web_app"

    def test_apply_profile_doesnt_override_existing(self, profile_manager):
        """apply_profile should not override existing config values."""
        base_config = {
            "project_name": "Test",
            "languages": "Rust",  # Different from profile default
        }
        result = profile_manager.apply_profile(base_config, "web_app")

        # Should keep the existing value
        assert result["languages"] == "Rust"

    def test_add_profile(self, profile_manager):
        """add_profile should add a custom profile."""
        custom_profile = {
            "name": "Custom Test",
            "description": "A custom test profile",
            "languages": "Go",
        }
        profile_manager.add_profile("custom_test", custom_profile)

        assert "custom_test" in profile_manager.list_profiles()
        retrieved = profile_manager.get_profile("custom_test")
        assert retrieved["languages"] == "Go"

    def test_get_frameworks_for_profile(self, profile_manager):
        """get_frameworks_for_profile should return framework list."""
        frameworks = profile_manager.get_frameworks_for_profile("web_app")
        assert isinstance(frameworks, list)
        assert len(frameworks) > 0

    def test_all_builtin_profiles_have_required_fields(self, profile_manager):
        """All built-in profiles should have required fields."""
        required_fields = ["name", "description"]

        for profile_key in profile_manager.list_profiles():
            profile = profile_manager.get_profile(profile_key)
            for field in required_fields:
                assert field in profile, f"Profile '{profile_key}' missing '{field}'"


class TestReporProfileManager:
    """Tests for the ReporProfileManager class."""

    def test_init_loads_repor_profiles(self, repor_profile_manager):
        """ReporProfileManager should load exploration profiles."""
        profiles = repor_profile_manager.list_profiles()
        assert len(profiles) > 0
        assert "feature_discovery" in profiles
        assert "security_audit" in profiles

    def test_get_profile_returns_dict(self, repor_profile_manager):
        """get_profile should return a profile dictionary."""
        profile = repor_profile_manager.get_profile("feature_discovery")
        assert isinstance(profile, dict)
        assert "name" in profile
        assert "goals" in profile

    def test_get_profile_raises_keyerror_for_unknown(self, repor_profile_manager):
        """get_profile should raise KeyError for unknown profiles."""
        with pytest.raises(KeyError):
            repor_profile_manager.get_profile("nonexistent")

    def test_get_profile_choices_returns_list_with_none(self, repor_profile_manager):
        """get_profile_choices should include 'none' option first."""
        choices = repor_profile_manager.get_profile_choices()
        assert isinstance(choices, list)
        assert len(choices) > 0

        # First choice should be the 'none' option
        first = choices[0]
        assert first[0] == "none"

    def test_get_goals_for_profile(self, repor_profile_manager):
        """get_goals_for_profile should return goals list."""
        goals = repor_profile_manager.get_goals_for_profile("security_audit")
        assert isinstance(goals, list)
        assert len(goals) > 0
        assert all(isinstance(g, str) for g in goals)

    def test_get_goals_for_none_returns_empty(self, repor_profile_manager):
        """get_goals_for_profile with 'none' should return empty list."""
        goals = repor_profile_manager.get_goals_for_profile("none")
        assert goals == []

    def test_all_repor_profiles_have_goals(self, repor_profile_manager):
        """All repor profiles should have goals defined."""
        for profile_key in repor_profile_manager.list_profiles():
            profile = repor_profile_manager.get_profile(profile_key)
            assert "goals" in profile
            assert len(profile["goals"]) > 0


class TestProfileConstants:
    """Tests for profile constant definitions."""

    def test_profiles_dict_not_empty(self):
        """PROFILES constant should not be empty."""
        assert len(PROFILES) > 0

    def test_repor_profiles_dict_not_empty(self):
        """REPOR_PROFILES constant should not be empty."""
        assert len(REPOR_PROFILES) > 0

    def test_profiles_have_consistent_structure(self):
        """All PROFILES should have consistent structure."""
        for key, profile in PROFILES.items():
            assert "name" in profile, f"Profile '{key}' missing 'name'"
            assert isinstance(profile["name"], str)

    def test_repor_profiles_have_consistent_structure(self):
        """All REPOR_PROFILES should have consistent structure."""
        for key, profile in REPOR_PROFILES.items():
            assert "name" in profile, f"Repor profile '{key}' missing 'name'"
            assert "goals" in profile, f"Repor profile '{key}' missing 'goals'"
            assert isinstance(profile["goals"], list)
