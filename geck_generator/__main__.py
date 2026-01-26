"""Entry point for GECK Generator: python -m geck_generator"""

import argparse
import sys
from pathlib import Path

from geck_generator import __version__


def main():
    """Main entry point for GECK Generator."""
    parser = argparse.ArgumentParser(
        description="GECK Generator - Generate LLM_init.md files for GECK v1.2 projects",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m geck_generator --cli              # Interactive CLI
  python -m geck_generator --gui              # GUI application
  python -m geck_generator --profile web_app -o ./project/LLM_init.md
  python -m geck_generator --cli --init-geck  # Create full GECK folder
  python -m geck_generator --list-profiles    # Show available profiles

Shortcut Management:
  python -m geck_generator --install-shortcut        # Create desktop & menu shortcuts
  python -m geck_generator --install-shortcut desktop  # Desktop only
  python -m geck_generator --install-shortcut menu     # Start menu only
  python -m geck_generator --uninstall-shortcut      # Remove all shortcuts
  python -m geck_generator --shortcut-info           # Show shortcut locations
        """,
    )

    parser.add_argument(
        "--version", action="version", version=f"GECK Generator {__version__}"
    )

    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run interactive CLI prompts",
    )

    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run GUI application",
    )

    parser.add_argument(
        "--profile",
        type=str,
        metavar="NAME",
        help="Generate from a preset profile (use --list-profiles to see options)",
    )

    parser.add_argument(
        "--template",
        type=str,
        metavar="PATH",
        help="Path to a custom Jinja2 template file",
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        metavar="PATH",
        help="Output file path for generated content",
    )

    parser.add_argument(
        "--init-geck",
        action="store_true",
        help="Initialize full LLM_GECK folder structure (use with --cli)",
    )

    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List all available preset profiles",
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List all available templates",
    )

    parser.add_argument(
        "--project-name",
        type=str,
        metavar="NAME",
        help="Project name (for --profile mode)",
    )

    parser.add_argument(
        "--goal",
        type=str,
        metavar="TEXT",
        help="Project goal (for --profile mode)",
    )

    # Shortcut management arguments
    parser.add_argument(
        "--install-shortcut",
        choices=["desktop", "menu", "both"],
        nargs="?",
        const="both",
        metavar="LOCATION",
        help="Create desktop/menu shortcut (desktop, menu, or both)",
    )

    parser.add_argument(
        "--uninstall-shortcut",
        action="store_true",
        help="Remove all GECK Generator shortcuts",
    )

    parser.add_argument(
        "--shortcut-info",
        action="store_true",
        help="Show shortcut locations for current platform",
    )

    args = parser.parse_args()

    # Handle --shortcut-info
    if args.shortcut_info:
        from geck_generator.utils.shortcuts import get_shortcut_info
        info = get_shortcut_info()
        print(f"\nShortcut Information ({info['platform']}):")
        print("-" * 50)
        print(f"  Desktop location: {info['desktop']}")
        print(f"  Menu location:    {info['menu']}")
        print(f"  Shortcut type:    {info['shortcut_type']}")
        print()
        return 0

    # Handle --install-shortcut
    if args.install_shortcut:
        from geck_generator.utils.shortcuts import create_shortcuts, get_platform
        try:
            print(f"\nCreating shortcuts on {get_platform()}...")
            created = create_shortcuts(args.install_shortcut)
            if created:
                print("\nShortcuts created successfully:")
                for path in created:
                    print(f"  - {path}")
                print("\nYou can now launch GECK Generator from your desktop or start menu.")
            else:
                print("No shortcuts were created.")
            return 0
        except Exception as e:
            print(f"Error creating shortcuts: {e}")
            return 1

    # Handle --uninstall-shortcut
    if args.uninstall_shortcut:
        from geck_generator.utils.shortcuts import remove_shortcuts
        try:
            removed = remove_shortcuts()
            if removed:
                print("\nShortcuts removed:")
                for path in removed:
                    print(f"  - {path}")
            else:
                print("No shortcuts found to remove.")
            return 0
        except Exception as e:
            print(f"Error removing shortcuts: {e}")
            return 1

    # Handle --list-profiles
    if args.list_profiles:
        from geck_generator.core.profiles import ProfileManager
        profiles = ProfileManager()
        print("\nAvailable Profiles:")
        print("-" * 60)
        for key, name, desc in profiles.get_profile_names_with_descriptions():
            print(f"  {key:20s} {name}")
            if desc:
                print(f"                       {desc}")
        print()
        return 0

    # Handle --list-templates
    if args.list_templates:
        from geck_generator.core.templates import TemplateEngine
        engine = TemplateEngine()
        print("\nAvailable Templates:")
        print("-" * 40)
        for name in engine.list_templates():
            print(f"  {name}")
        print()
        return 0

    # Handle --gui
    if args.gui:
        try:
            from geck_generator.gui.app import run_gui
            run_gui()
            return 0
        except ImportError as e:
            print(f"Error: Could not load GUI. {e}")
            print("Make sure tkinter is installed.")
            return 1

    # Handle --cli
    if args.cli:
        try:
            from geck_generator.cli.interactive import run_cli_and_save
            result = run_cli_and_save(init_geck=args.init_geck)
            return 0 if result else 1
        except ImportError as e:
            print(f"Error: Could not load CLI. {e}")
            print("Install questionary: pip install questionary")
            return 1
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            return 1

    # Handle --profile (quick generation)
    if args.profile:
        from geck_generator.core.generator import GECKGenerator
        from geck_generator.core.profiles import ProfileManager

        generator = GECKGenerator()
        profiles = ProfileManager()

        # Check if profile exists
        try:
            profiles.get_profile(args.profile)
        except KeyError as e:
            print(f"Error: {e}")
            return 1

        # Get project name and goal
        project_name = args.project_name
        goal = args.goal

        if not project_name:
            project_name = input("Project name: ").strip()
            if not project_name:
                print("Error: Project name is required")
                return 1

        if not goal:
            goal = input("Project goal: ").strip()
            if not goal:
                print("Error: Project goal is required")
                return 1

        # Generate
        config = {
            "profile": args.profile,
            "project_name": project_name,
            "goal": goal,
        }

        content = generator.generate(config)

        # Output
        if args.output:
            output_path = Path(args.output)
            generator.generate_to_file(config, output_path)
            print(f"Generated: {output_path}")
        else:
            print(content)

        return 0

    # Handle --template (custom template)
    if args.template:
        from geck_generator.core.generator import GECKGenerator

        generator = GECKGenerator()
        template_path = Path(args.template)

        if not template_path.exists():
            print(f"Error: Template file not found: {template_path}")
            return 1

        # Collect variables interactively
        print("Enter template variables (empty to skip):")
        variables = {}

        # Common variables
        for var in ["project_name", "goal", "context"]:
            value = input(f"  {var}: ").strip()
            if value:
                variables[var] = value

        content = generator.generate_from_template_file(template_path, variables)

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(content, encoding="utf-8")
            print(f"Generated: {output_path}")
        else:
            print(content)

        return 0

    # No arguments provided - show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
