"""Interactive CLI using questionary for GECK Generator."""

from pathlib import Path
from typing import Any

import questionary
from questionary import Style

from geck_generator.core.generator import GECKGenerator
from geck_generator.core.profiles import ProfileManager
from geck_generator.utils.validators import (
    validate_url,
    validate_path,
    validate_project_name,
    validate_goal,
    suggest_repo_url,
)


# Custom style for the CLI
custom_style = Style([
    ("qmark", "fg:cyan bold"),
    ("question", "bold"),
    ("answer", "fg:green"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:green"),
    ("separator", "fg:gray"),
    ("instruction", "fg:gray"),
    ("text", ""),
])


def run_interactive() -> dict[str, Any]:
    """
    Run interactive CLI and return config dict.

    Returns:
        Configuration dictionary collected from user input
    """
    print("\n" + "=" * 60)
    print("  GECK Generator - Interactive Setup")
    print("=" * 60 + "\n")

    config: dict[str, Any] = {}
    profiles = ProfileManager()
    generator = GECKGenerator()

    # Step 1: Basic info
    print("📋 Step 1: Basic Project Information\n")

    config["project_name"] = questionary.text(
        "Project name:",
        validate=lambda x: validate_project_name(x)[0] or validate_project_name(x)[1],
        style=custom_style,
    ).ask()

    if config["project_name"] is None:
        raise KeyboardInterrupt("User cancelled")

    # Get local path with suggestion
    default_path = str(Path.cwd())
    config["local_path"] = questionary.path(
        "Local project path:",
        default=default_path,
        style=custom_style,
    ).ask()

    if config["local_path"] is None:
        raise KeyboardInterrupt("User cancelled")

    # Try to suggest repo URL
    suggested_url = suggest_repo_url(config["local_path"]) or ""
    config["repo_url"] = questionary.text(
        "Repository URL (optional):",
        default=suggested_url,
        validate=lambda x: validate_url(x)[0] or validate_url(x)[1],
        style=custom_style,
    ).ask()

    if config["repo_url"] is None:
        raise KeyboardInterrupt("User cancelled")

    # Step 2: Profile selection
    print("\n📦 Step 2: Project Profile\n")

    use_profile = questionary.confirm(
        "Would you like to use a preset profile?",
        default=True,
        style=custom_style,
    ).ask()

    if use_profile is None:
        raise KeyboardInterrupt("User cancelled")

    if use_profile:
        # First, select a category
        category_choices = []
        for cat in profiles.get_categories_with_profiles():
            category_choices.append(questionary.Choice(
                title=f"{cat['name']} - {cat['description']}",
                value=cat["key"],
            ))

        selected_category = questionary.select(
            "Select a category:",
            choices=category_choices,
            style=custom_style,
        ).ask()

        if selected_category is None:
            raise KeyboardInterrupt("User cancelled")

        # Then, select a profile within that category
        profile_choices = []
        for key, name, desc in profiles.get_profiles_for_category(selected_category):
            profile_choices.append(questionary.Choice(
                title=f"{name} - {desc}",
                value=key,
            ))

        config["profile"] = questionary.select(
            "Select a profile:",
            choices=profile_choices,
            style=custom_style,
        ).ask()

        if config["profile"] is None:
            raise KeyboardInterrupt("User cancelled")

        # Show what the profile provides
        profile_data = profiles.get_profile(config["profile"])
        print(f"\n  ✓ Using profile: {profile_data['name']}")
        print(f"    Languages: {profile_data.get('languages', 'N/A')}")
        if profile_data.get("frameworks"):
            print(f"    Frameworks: {', '.join(profile_data['frameworks'][:3])}...")
        print()
    else:
        config["profile"] = None

    # Step 3: Goal and context
    print("🎯 Step 3: Project Goal\n")

    config["goal"] = questionary.text(
        "Describe the project goal (what should exist when done):",
        multiline=True,
        validate=lambda x: validate_goal(x)[0] or validate_goal(x)[1],
        instruction="(Press Alt+Enter or Esc then Enter to finish)",
        style=custom_style,
    ).ask()

    if config["goal"] is None:
        raise KeyboardInterrupt("User cancelled")

    config["context"] = questionary.text(
        "Additional context (background info, optional):",
        multiline=True,
        instruction="(Press Alt+Enter or Esc then Enter to finish, or leave empty)",
        style=custom_style,
    ).ask()

    if config["context"] is None:
        config["context"] = ""

    # Step 4: Success criteria
    print("\n✅ Step 4: Success Criteria\n")

    # If using a profile, offer suggested criteria
    criteria = []
    if config.get("profile"):
        profile_data = profiles.get_profile(config["profile"])
        suggested = profile_data.get("suggested_criteria", [])
        if suggested:
            print("  Suggested criteria from profile:")
            for i, criterion in enumerate(suggested, 1):
                print(f"    {i}. {criterion}")
            print()

            use_suggested = questionary.confirm(
                "Use these suggested criteria as a starting point?",
                default=True,
                style=custom_style,
            ).ask()

            if use_suggested:
                criteria = suggested.copy()

    print("  Add your own success criteria (empty input to finish):")
    while True:
        criterion = questionary.text(
            f"  Criterion #{len(criteria) + 1}:",
            style=custom_style,
        ).ask()

        if criterion is None:
            break
        if not criterion.strip():
            break
        criteria.append(criterion.strip())

    config["success_criteria"] = criteria

    # Step 5: Constraints
    print("\n⚙️ Step 5: Constraints\n")

    # Languages (pre-fill from profile if available)
    default_languages = ""
    if config.get("profile"):
        default_languages = profiles.get_profile(config["profile"]).get("languages", "")

    config["languages"] = questionary.text(
        "Languages/Frameworks:",
        default=default_languages,
        style=custom_style,
    ).ask()

    if config["languages"] is None:
        config["languages"] = default_languages

    # Must use
    default_must_use = ""
    if config.get("profile"):
        default_must_use = profiles.get_profile(config["profile"]).get("suggested_must_use", "")

    config["must_use"] = questionary.text(
        "Must use (required tools/patterns):",
        default=default_must_use,
        style=custom_style,
    ).ask()

    # Must avoid
    default_must_avoid = ""
    if config.get("profile"):
        default_must_avoid = profiles.get_profile(config["profile"]).get("suggested_must_avoid", "")

    config["must_avoid"] = questionary.text(
        "Must avoid (forbidden patterns/tools):",
        default=default_must_avoid,
        style=custom_style,
    ).ask()

    # Platforms
    platform_choices = ["Windows", "macOS", "Linux", "Docker", "iOS", "Android", "Web"]
    default_platforms = []
    if config.get("profile"):
        default_platforms = profiles.get_profile(config["profile"]).get("platforms", [])

    config["platforms"] = questionary.checkbox(
        "Target platforms:",
        choices=[
            questionary.Choice(p, checked=(p in default_platforms))
            for p in platform_choices
        ],
        style=custom_style,
    ).ask()

    if config["platforms"] is None:
        config["platforms"] = default_platforms

    # Step 6: Initial task
    print("\n🚀 Step 6: Initial Task\n")

    config["initial_task"] = questionary.text(
        "What is the first task to work on?",
        multiline=True,
        instruction="(Press Alt+Enter or Esc then Enter to finish)",
        style=custom_style,
    ).ask()

    if config["initial_task"] is None:
        config["initial_task"] = ""

    # Preview
    print("\n" + "=" * 60)
    print("  Preview")
    print("=" * 60 + "\n")

    preview = generator.generate(config)
    print(preview)
    print("\n" + "=" * 60 + "\n")

    return config


def run_cli_and_save(init_geck: bool = False) -> Path | None:
    """
    Run the interactive CLI and save the result.

    Args:
        init_geck: If True, create full GECK folder structure

    Returns:
        Path to the created file/folder, or None if cancelled
    """
    try:
        config = run_interactive()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        return None

    generator = GECKGenerator()

    # Ask where to save
    if init_geck:
        # Create full GECK folder
        output_path = questionary.path(
            "Create GECK folder in which directory?",
            default=config.get("local_path", str(Path.cwd())),
            style=custom_style,
        ).ask()

        if output_path is None:
            print("Cancelled.")
            return None

        result_path = generator.init_geck_folder(output_path, config)
        project_path = Path(output_path)
        print(f"\n✅ Created GECK structure:")
        print(f"   - {project_path / 'LLM_init.md'}")
        print(f"   - {result_path}/")
        for f in sorted(result_path.iterdir()):
            print(f"     - {f.name}")
        return result_path
    else:
        # Just create LLM_init.md
        default_output = Path(config.get("local_path", ".")) / "LLM_init.md"
        output_path = questionary.path(
            "Save LLM_init.md to:",
            default=str(default_output),
            style=custom_style,
        ).ask()

        if output_path is None:
            print("Cancelled.")
            return None

        result_path = generator.generate_to_file(config, output_path)
        print(f"\n✅ Created: {result_path}")
        return result_path
