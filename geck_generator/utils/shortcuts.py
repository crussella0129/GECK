"""Cross-platform shortcut creation for GECK Generator."""

import os
import sys
import stat
import subprocess
from pathlib import Path
from typing import Literal

ShortcutLocation = Literal["desktop", "menu", "both"]


def get_python_executable() -> str:
    """Get the path to the Python executable."""
    return sys.executable


def get_package_dir() -> Path:
    """Get the geck_generator package directory."""
    return Path(__file__).parent.parent


def get_icon_path() -> Path | None:
    """Get the path to the application icon if it exists."""
    package_dir = get_package_dir()

    # Check for icon in various formats
    for icon_name in ["icon.ico", "icon.png", "icon.svg"]:
        icon_path = package_dir / "assets" / icon_name
        if icon_path.exists():
            return icon_path

    return None


# =============================================================================
# Windows Shortcut Creation
# =============================================================================

def _create_windows_shortcut(
    name: str,
    target: str,
    arguments: str,
    location: Path,
    working_dir: Path,
    description: str = "",
    icon_path: str | None = None,
) -> Path:
    """Create a Windows .lnk shortcut using PowerShell."""
    shortcut_path = location / f"{name}.lnk"

    # PowerShell script to create shortcut
    ps_script = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{target}"
$Shortcut.Arguments = "{arguments}"
$Shortcut.Description = "{description}"
$Shortcut.WorkingDirectory = "{working_dir}"
'''

    if icon_path:
        ps_script += f'$Shortcut.IconLocation = "{icon_path}"\n'

    ps_script += "$Shortcut.Save()"

    # Run PowerShell script
    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to create shortcut: {result.stderr}")

    return shortcut_path


def create_windows_shortcuts(location: ShortcutLocation = "both") -> list[Path]:
    """
    Create Windows shortcuts for GECK Generator.

    Args:
        location: Where to create shortcuts ("desktop", "menu", or "both")

    Returns:
        List of created shortcut paths
    """
    created = []
    python_exe = get_python_executable()
    icon = get_icon_path()

    # Determine locations
    desktop = Path(os.environ.get("USERPROFILE", "~")).expanduser() / "Desktop"
    start_menu = (
        Path(os.environ.get("APPDATA", "~")).expanduser()
        / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    )

    locations_to_create = []
    if location in ("desktop", "both"):
        locations_to_create.append(desktop)
    if location in ("menu", "both"):
        locations_to_create.append(start_menu)

    # Get the package's parent directory (where geck_generator folder is located)
    package_parent = get_package_dir().parent

    for loc in locations_to_create:
        loc.mkdir(parents=True, exist_ok=True)

        shortcut = _create_windows_shortcut(
            name="GECK Generator",
            target=python_exe,
            arguments="-m geck_generator --gui",
            location=loc,
            working_dir=package_parent,
            description="Generate LLM_init.md files for GECK projects",
            icon_path=str(icon) if icon else None,
        )
        created.append(shortcut)

    return created


# =============================================================================
# Linux Shortcut Creation
# =============================================================================

LINUX_DESKTOP_ENTRY = """\
[Desktop Entry]
Version=1.0
Type=Application
Name=GECK Generator
Comment=Generate LLM_init.md files for GECK projects
Exec={python_exe} -m geck_generator --gui
Path={working_dir}
Icon={icon_path}
Terminal=false
Categories=Development;Utility;
StartupNotify=true
"""


def create_linux_shortcuts(location: ShortcutLocation = "both") -> list[Path]:
    """
    Create Linux .desktop shortcuts for GECK Generator.

    Args:
        location: Where to create shortcuts ("desktop", "menu", or "both")

    Returns:
        List of created shortcut paths
    """
    created = []
    python_exe = get_python_executable()
    icon = get_icon_path()

    # Use a default icon if none exists
    icon_path = str(icon) if icon else "utilities-terminal"

    # Get the package's parent directory (where geck_generator folder is located)
    package_parent = get_package_dir().parent

    desktop_entry = LINUX_DESKTOP_ENTRY.format(
        python_exe=python_exe,
        icon_path=icon_path,
        working_dir=package_parent,
    )

    # Determine locations
    home = Path.home()
    desktop = home / "Desktop"
    applications = home / ".local" / "share" / "applications"

    locations_to_create = []
    if location in ("desktop", "both"):
        locations_to_create.append(desktop)
    if location in ("menu", "both"):
        locations_to_create.append(applications)

    for loc in locations_to_create:
        loc.mkdir(parents=True, exist_ok=True)

        shortcut_path = loc / "geck-generator.desktop"
        shortcut_path.write_text(desktop_entry, encoding="utf-8")

        # Make executable
        shortcut_path.chmod(shortcut_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        created.append(shortcut_path)

    # Update desktop database if available
    try:
        subprocess.run(
            ["update-desktop-database", str(applications)],
            capture_output=True,
            timeout=10,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        pass  # Not critical if this fails

    return created


# =============================================================================
# macOS Shortcut Creation
# =============================================================================

MACOS_APP_SCRIPT = """\
#!/bin/bash
cd "{working_dir}"
"{python_exe}" -m geck_generator --gui
"""

MACOS_INFO_PLIST = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launch.sh</string>
    <key>CFBundleIdentifier</key>
    <string>com.geck.generator</string>
    <key>CFBundleName</key>
    <string>GECK Generator</string>
    <key>CFBundleDisplayName</key>
    <string>GECK Generator</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.10</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""


def create_macos_shortcuts(location: ShortcutLocation = "both") -> list[Path]:
    """
    Create macOS .app bundle for GECK Generator.

    Args:
        location: Where to create shortcuts ("desktop", "menu"/"applications", or "both")

    Returns:
        List of created shortcut paths
    """
    created = []
    python_exe = get_python_executable()
    # Get the package's parent directory (where geck_generator folder is located)
    package_parent = get_package_dir().parent

    # Determine locations
    home = Path.home()
    desktop = home / "Desktop"
    applications = home / "Applications"

    locations_to_create = []
    if location in ("desktop", "both"):
        locations_to_create.append(desktop)
    if location in ("menu", "both"):
        locations_to_create.append(applications)

    for loc in locations_to_create:
        loc.mkdir(parents=True, exist_ok=True)

        # Create .app bundle structure
        app_path = loc / "GECK Generator.app"
        contents = app_path / "Contents"
        macos = contents / "MacOS"
        resources = contents / "Resources"

        # Remove existing if present
        if app_path.exists():
            import shutil
            shutil.rmtree(app_path)

        macos.mkdir(parents=True)
        resources.mkdir(parents=True)

        # Write Info.plist
        (contents / "Info.plist").write_text(MACOS_INFO_PLIST, encoding="utf-8")

        # Write launch script
        launch_script = macos / "launch.sh"
        launch_script.write_text(
            MACOS_APP_SCRIPT.format(python_exe=python_exe, working_dir=package_parent),
            encoding="utf-8"
        )
        launch_script.chmod(launch_script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        # Copy icon if available
        icon = get_icon_path()
        if icon and icon.suffix == ".png":
            # Convert PNG to ICNS would require additional tools
            # For now, just copy the PNG
            import shutil
            shutil.copy(icon, resources / "icon.png")

        created.append(app_path)

    return created


# =============================================================================
# Cross-Platform API
# =============================================================================

def get_platform() -> str:
    """Get the current platform name."""
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    else:
        return "linux"


def create_shortcuts(location: ShortcutLocation = "both") -> list[Path]:
    """
    Create shortcuts for the current platform.

    Args:
        location: Where to create shortcuts
            - "desktop": Only desktop shortcut
            - "menu": Only start menu/applications menu
            - "both": Both locations (default)

    Returns:
        List of created shortcut paths
    """
    platform = get_platform()

    if platform == "windows":
        return create_windows_shortcuts(location)
    elif platform == "macos":
        return create_macos_shortcuts(location)
    else:
        return create_linux_shortcuts(location)


def remove_shortcuts() -> list[Path]:
    """
    Remove all GECK Generator shortcuts.

    Returns:
        List of removed shortcut paths
    """
    removed = []
    platform = get_platform()
    home = Path.home()

    if platform == "windows":
        paths = [
            home / "Desktop" / "GECK Generator.lnk",
            Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "GECK Generator.lnk",
        ]
    elif platform == "macos":
        paths = [
            home / "Desktop" / "GECK Generator.app",
            home / "Applications" / "GECK Generator.app",
        ]
    else:
        paths = [
            home / "Desktop" / "geck-generator.desktop",
            home / ".local" / "share" / "applications" / "geck-generator.desktop",
        ]

    import shutil
    for path in paths:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            removed.append(path)

    return removed


def get_shortcut_info() -> dict:
    """
    Get information about shortcut locations for the current platform.

    Returns:
        Dictionary with platform info and shortcut locations
    """
    platform = get_platform()
    home = Path.home()

    if platform == "windows":
        return {
            "platform": "Windows",
            "desktop": home / "Desktop",
            "menu": Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
            "shortcut_type": ".lnk file",
        }
    elif platform == "macos":
        return {
            "platform": "macOS",
            "desktop": home / "Desktop",
            "menu": home / "Applications",
            "shortcut_type": ".app bundle",
        }
    else:
        return {
            "platform": "Linux",
            "desktop": home / "Desktop",
            "menu": home / ".local" / "share" / "applications",
            "shortcut_type": ".desktop file",
        }
