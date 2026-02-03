"""Preset profile definitions for GECK Generator."""

from typing import Any


# Exploration profiles for GECK Repor feature
REPOR_PROFILES: dict[str, dict[str, Any]] = {
    "feature_discovery": {
        "name": "Feature Discovery",
        "description": "Find reusable components and patterns",
        "goals": [
            "Identify reusable utility functions",
            "Find well-documented APIs",
            "Locate configurable components",
            "Discover extensible patterns",
        ],
    },
    "performance_optimization": {
        "name": "Performance Optimization",
        "description": "Identify performance patterns",
        "goals": [
            "Find caching implementations",
            "Locate async/concurrent patterns",
            "Identify optimization techniques",
            "Discover efficient algorithms",
        ],
    },
    "security_audit": {
        "name": "Security Audit",
        "description": "Look for security patterns and practices",
        "goals": [
            "Find authentication implementations",
            "Locate input validation patterns",
            "Identify secure configuration practices",
            "Discover access control mechanisms",
        ],
    },
    "testing_patterns": {
        "name": "Testing Patterns",
        "description": "Find testing strategies and coverage",
        "goals": [
            "Identify testing frameworks used",
            "Find mock/stub patterns",
            "Locate integration test setups",
            "Discover test organization patterns",
        ],
    },
    "architecture_review": {
        "name": "Architecture Review",
        "description": "Analyze code organization",
        "goals": [
            "Identify architectural patterns (MVC, etc.)",
            "Find module organization patterns",
            "Locate dependency injection usage",
            "Discover error handling strategies",
        ],
    },
}


# Profile categories for organized menu navigation
# Each category contains a list of profile keys
PROFILE_CATEGORIES: dict[str, dict[str, Any]] = {
    "web": {
        "name": "Web & Internet",
        "description": "Websites, web applications, APIs, and browser extensions",
        "profiles": ["website", "web_app", "api", "browser_extension"],
    },
    "applications": {
        "name": "Applications",
        "description": "Desktop, mobile, and command-line applications",
        "profiles": ["desktop_app", "mobile_app", "cli_tool"],
    },
    "automation": {
        "name": "Automation & Infrastructure",
        "description": "Scripts, DevOps, bots, and infrastructure as code",
        "profiles": ["automation_script", "devops", "bot"],
    },
    "libraries": {
        "name": "Libraries & Services",
        "description": "Reusable packages, plugins, and microservices",
        "profiles": ["library", "plugin", "microservice"],
    },
    "data": {
        "name": "Data & Documents",
        "description": "Data science, spreadsheets, and documentation",
        "profiles": ["data_science", "excel_sheets", "documentation"],
    },
    "creative": {
        "name": "Creative & Games",
        "description": "Games, graphics, and creative coding",
        "profiles": ["game", "shader_creative"],
    },
    "systems": {
        "name": "Systems & Hardware",
        "description": "OS development, embedded systems, and blockchain",
        "profiles": ["os_development", "embedded", "blockchain"],
    },
}


# Preset profiles for common project types
PROFILES: dict[str, dict[str, Any]] = {
    # ===== Web & Internet =====
    "website": {
        "name": "Website",
        "description": "Static or dynamic website focused on content delivery",
        "languages": "HTML, CSS, JavaScript/TypeScript",
        "frameworks": [
            "Astro", "Hugo", "Eleventy", "Jekyll", "Next.js", "Nuxt",
            "WordPress", "Tailwind CSS", "Bootstrap"
        ],
        "platforms": ["Web", "Linux", "Docker"],
        "suggested_criteria": [
            "All pages render correctly across browsers",
            "Site is responsive on mobile, tablet, and desktop",
            "Accessibility audit passes (WCAG 2.1 AA)",
            "Page load time meets performance targets",
            "SEO fundamentals are implemented correctly",
            "All links and navigation work correctly",
        ],
        "suggested_must_use": "Semantic HTML, responsive design, image optimization, meta tags",
        "suggested_must_avoid": "Inline styles for layout, blocking scripts in head, missing alt text, broken links",
    },
    "web_app": {
        "name": "Web App",
        "description": "Interactive browser-based application or SaaS tool",
        "languages": "JavaScript/TypeScript, Python 3.11+",
        "frameworks": [
            "React", "Vue", "Svelte", "Angular", "SolidJS",
            "Next.js", "Nuxt", "SvelteKit", "Redux", "Zustand"
        ],
        "platforms": ["Web", "Linux", "Windows", "macOS", "Docker"],
        "suggested_criteria": [
            "Application loads and initializes without errors",
            "User interactions respond correctly",
            "State management works across components",
            "Data persists correctly (local storage, backend)",
            "Application handles offline/error states gracefully",
            "Authentication and session management work correctly",
        ],
        "suggested_must_use": "Component architecture, state management, error boundaries, loading states",
        "suggested_must_avoid": "Direct DOM manipulation in frameworks, prop drilling, memory leaks in subscriptions, exposing sensitive data client-side",
    },
    "api": {
        "name": "API",
        "description": "REST, GraphQL, or gRPC API service",
        "languages": "Python 3.11+, TypeScript/Node.js, Go, Rust",
        "frameworks": [
            "FastAPI", "Flask", "Django REST Framework", "Express",
            "NestJS", "Hono", "GraphQL", "gRPC", "tRPC"
        ],
        "platforms": ["Linux", "Docker", "Kubernetes"],
        "suggested_criteria": [
            "All endpoints respond with correct status codes",
            "Request validation rejects malformed input",
            "Authentication and authorization work correctly",
            "Rate limiting protects against abuse",
            "API documentation is accurate and complete",
            "Error responses are consistent and informative",
        ],
        "suggested_must_use": "OpenAPI/Swagger documentation, proper HTTP methods and status codes, request validation, structured logging",
        "suggested_must_avoid": "SQL injection, exposing stack traces in production, missing authentication on protected routes, N+1 query problems",
    },
    "browser_extension": {
        "name": "Browser Extension",
        "description": "Chrome, Firefox, Safari, or Edge browser extension",
        "languages": "JavaScript/TypeScript, HTML, CSS",
        "frameworks": [
            "WebExtensions API", "Chrome Extensions API", "Plasmo", "WXT",
            "Chrome Storage API", "Browser Action API"
        ],
        "platforms": ["Chrome", "Firefox", "Safari", "Edge"],
        "suggested_criteria": [
            "Extension installs without errors",
            "Permissions are minimal and justified",
            "Content scripts work on target pages",
            "Background/service worker handles events correctly",
            "Popup and options UI work correctly",
            "Extension passes store review guidelines",
        ],
        "suggested_must_use": "Manifest V3 (Chrome), minimal permission scoping, content security policy, proper message passing",
        "suggested_must_avoid": "Excessive permissions, remote code execution, data collection without consent, blocking the main thread",
    },
    # ===== Applications =====
    "desktop_app": {
        "name": "Desktop Application",
        "description": "Native or cross-platform desktop application",
        "languages": "JavaScript/TypeScript, Rust, C++, C#, Python",
        "frameworks": [
            "Electron", "Tauri", "Qt", "WPF", "WinForms",
            "GTK", "PyQt", "wxWidgets", ".NET MAUI"
        ],
        "platforms": ["Windows", "macOS", "Linux"],
        "suggested_criteria": [
            "Application launches and displays correctly",
            "Window management works properly",
            "File operations complete correctly",
            "System integration works (tray, notifications, file associations)",
            "Application handles multiple monitors and DPI scaling",
            "Installation and updates work correctly",
        ],
        "suggested_must_use": "Native platform conventions, proper window lifecycle, system theme support, accessible UI",
        "suggested_must_avoid": "Excessive resource usage, blocking UI thread, platform-specific code without abstraction",
    },
    "mobile_app": {
        "name": "Mobile Application",
        "description": "iOS, Android, or cross-platform mobile app",
        "languages": "Swift, Kotlin, Dart, JavaScript/TypeScript, C#",
        "frameworks": [
            "SwiftUI", "UIKit", "Jetpack Compose", "Flutter",
            "React Native", "Expo", ".NET MAUI", "Capacitor"
        ],
        "platforms": ["iOS", "Android"],
        "suggested_criteria": [
            "App launches without crashes",
            "UI renders correctly across screen sizes",
            "Navigation flows work correctly",
            "Data persists correctly across app restarts",
            "App handles background/foreground transitions",
            "Push notifications work correctly (if applicable)",
        ],
        "suggested_must_use": "Platform design guidelines (HIG/Material), responsive layouts, proper lifecycle handling, accessibility",
        "suggested_must_avoid": "Blocking main/UI thread, excessive battery/memory usage, hardcoded dimensions, ignoring safe areas",
    },
    "cli_tool": {
        "name": "CLI Tool",
        "description": "Command-line interface application",
        "languages": "Python 3.11+",
        "frameworks": ["Click", "Typer", "argparse"],
        "platforms": ["Linux", "Windows", "macOS"],
        "suggested_criteria": [
            "All commands execute without errors",
            "Help text is accurate and complete",
            "Exit codes are correct",
            "Input validation works properly",
            "Error messages are clear and actionable",
        ],
        "suggested_must_use": "Type hints, proper exit codes",
        "suggested_must_avoid": "Hardcoded paths, platform-specific assumptions",
    },
    # ===== Data & Documents =====
    "data_science": {
        "name": "Data Science / ML",
        "description": "Data analysis, machine learning, or AI project",
        "languages": "Python 3.11+",
        "frameworks": ["pandas", "numpy", "scikit-learn", "pytorch", "tensorflow"],
        "platforms": ["Linux", "Windows", "macOS"],
        "suggested_criteria": [
            "Data pipeline runs end-to-end",
            "Model achieves target metrics",
            "Results are reproducible",
            "Data preprocessing handles edge cases",
            "Visualizations render correctly",
        ],
        "suggested_must_use": "Virtual environments, requirements.txt or pyproject.toml",
        "suggested_must_avoid": "Absolute paths to data, training on test data",
    },
    # ===== Automation & Infrastructure =====
    "automation_script": {
        "name": "Automation Script",
        "description": "Scripts for task automation and batch processing",
        "languages": "Python 3.11+, Bash, PowerShell",
        "frameworks": [],
        "platforms": ["Linux", "Windows", "macOS"],
        "suggested_criteria": [
            "Script completes without errors",
            "Output is in expected format",
            "Edge cases are handled",
            "Logging provides useful information",
            "Script is idempotent where appropriate",
        ],
        "suggested_must_use": "Logging, error handling, clear documentation",
        "suggested_must_avoid": "Destructive operations without confirmation, hardcoded secrets",
    },
    "devops": {
        "name": "DevOps / Infrastructure",
        "description": "Infrastructure as Code, CI/CD, and cloud automation",
        "languages": "HCL, YAML, Python, Bash, Go",
        "frameworks": [
            "Terraform", "Ansible", "Pulumi", "CloudFormation",
            "Kubernetes", "Docker", "GitHub Actions", "GitLab CI", "ArgoCD"
        ],
        "platforms": ["AWS", "GCP", "Azure", "Linux", "Docker", "Kubernetes"],
        "suggested_criteria": [
            "Infrastructure deploys successfully",
            "Configuration changes are idempotent",
            "Secrets are managed securely",
            "Rollback procedures work correctly",
            "Monitoring and alerting are configured",
            "CI/CD pipelines run successfully",
        ],
        "suggested_must_use": "Infrastructure as Code, version control for configs, secret management (Vault, etc.), least privilege IAM",
        "suggested_must_avoid": "Hardcoded credentials, manual configuration drift, single points of failure, over-provisioned resources",
    },
    "bot": {
        "name": "Chat Bot / Integration",
        "description": "Discord, Slack, Telegram, or other chat platform bot",
        "languages": "Python, JavaScript/TypeScript, Go",
        "frameworks": [
            "discord.py", "discord.js", "Slack Bolt", "python-telegram-bot",
            "Telegraf", "Pycord", "Nextcord"
        ],
        "platforms": ["Discord", "Slack", "Telegram", "Linux", "Docker"],
        "suggested_criteria": [
            "Bot connects and authenticates successfully",
            "Commands respond correctly",
            "Rate limiting is handled properly",
            "Permissions are respected",
            "Error responses are user-friendly",
            "Bot reconnects gracefully after disconnection",
        ],
        "suggested_must_use": "Command framework, proper rate limit handling, graceful shutdown, logging, /help command",
        "suggested_must_avoid": "Blocking event loop, tokens in source code, excessive API calls, ignoring platform ToS",
    },
    # ===== Libraries & Services =====
    "library": {
        "name": "Library / Package",
        "description": "Reusable library or package for any language",
        "languages": "Python 3.11+, TypeScript, Rust, Go",
        "frameworks": [],
        "platforms": ["Linux", "Windows", "macOS"],
        "suggested_criteria": [
            "All public APIs have documentation",
            "Unit tests pass with good coverage",
            "Package installs correctly via package manager",
            "Type definitions are complete and accurate",
            "README and docs are clear and complete",
        ],
        "suggested_must_use": "Type hints/definitions, docstrings, semantic versioning, proper package manifest",
        "suggested_must_avoid": "Breaking changes without major version bump, circular dependencies, excessive dependencies",
    },
    "plugin": {
        "name": "Plugin / Extension",
        "description": "Plugin or extension for an existing application",
        "languages": "JavaScript/TypeScript, Python, Lua, C#, PHP",
        "frameworks": [
            "VSCode Extension API", "JetBrains Plugin SDK", "Obsidian Plugin API",
            "WordPress Plugin API", "Neovim Lua API", "Unity Editor API"
        ],
        "platforms": ["Windows", "macOS", "Linux", "Web"],
        "suggested_criteria": [
            "Plugin installs without errors",
            "Plugin integrates with host API correctly",
            "Settings and configuration work properly",
            "Plugin doesn't break host application",
            "Uninstall cleans up properly",
            "Documentation explains usage clearly",
        ],
        "suggested_must_use": "Host application's API conventions, proper lifecycle hooks, settings persistence, error boundaries",
        "suggested_must_avoid": "Global namespace pollution, modifying host internals, excessive resource usage, breaking other plugins",
    },
    "microservice": {
        "name": "Microservice",
        "description": "Containerized microservice for distributed systems",
        "languages": "Python 3.11+",
        "frameworks": ["FastAPI", "Flask", "gRPC"],
        "platforms": ["Docker", "Kubernetes"],
        "suggested_criteria": [
            "Service starts and responds to health checks",
            "All endpoints function correctly",
            "Service handles failures gracefully",
            "Logging and metrics are properly configured",
            "Container builds and runs successfully",
        ],
        "suggested_must_use": "Health check endpoints, structured logging, environment variables for config",
        "suggested_must_avoid": "Storing state locally, hardcoded service URLs",
    },
    "excel_sheets": {
        "name": "Excel / Sheets Template",
        "description": "Spreadsheet-based applications with macros, formulas, and automation",
        "languages": "VBA, Power Query (M), Google Apps Script, Python, LibreOffice Basic",
        "frameworks": [
            "Excel VBA", "Power Query", "Power Pivot", "Office.js",
            "Google Apps Script", "Google Sheets API",
            "LibreOffice Calc", "openpyxl", "xlwings"
        ],
        "platforms": ["Windows", "macOS", "Web", "Linux"],
        "suggested_criteria": [
            "All formulas calculate correctly",
            "Macros/scripts execute without errors",
            "Data validation rules work as expected",
            "Template works across target platforms (Excel/Sheets/Calc)",
            "Large datasets perform within acceptable time",
            "Error handling provides clear user feedback",
        ],
        "suggested_must_use": "Named ranges, data validation, error handling in formulas (IFERROR), clear documentation/instructions sheet",
        "suggested_must_avoid": "Volatile functions unnecessarily (INDIRECT, OFFSET), circular references, hardcoded ranges in macros, unprotected sensitive data",
    },
    "documentation": {
        "name": "Documentation Site",
        "description": "Technical documentation, API docs, or knowledge base",
        "languages": "Markdown, MDX, reStructuredText, HTML",
        "frameworks": [
            "Docusaurus", "MkDocs", "Sphinx", "VitePress",
            "Astro", "GitBook", "ReadTheDocs", "Nextra"
        ],
        "platforms": ["Web", "Linux", "Docker"],
        "suggested_criteria": [
            "Site builds without errors",
            "Navigation is logical and complete",
            "Search works correctly",
            "Code examples are accurate and tested",
            "Images and diagrams render correctly",
            "Versioning works correctly (if applicable)",
        ],
        "suggested_must_use": "Consistent formatting, clear heading hierarchy, working links, code syntax highlighting, table of contents",
        "suggested_must_avoid": "Outdated information, broken links, untested code examples, inconsistent terminology, missing search",
    },
    # ===== Creative & Games =====
    "game": {
        "name": "Game Development",
        "description": "Video game or interactive entertainment project",
        "languages": "Python, C#, C++, GDScript, Lua",
        "frameworks": ["Pygame", "Godot", "Unity", "Unreal Engine", "Phaser", "LÖVE"],
        "platforms": ["Windows", "macOS", "Linux", "Web", "iOS", "Android"],
        "suggested_criteria": [
            "Game launches without errors",
            "Core gameplay loop functions correctly",
            "Player input is responsive and accurate",
            "Game state saves and loads correctly",
            "Performance meets target frame rate",
            "Audio plays correctly and synchronizes with visuals",
        ],
        "suggested_must_use": "Delta time for frame-independent movement, asset management, input abstraction layer",
        "suggested_must_avoid": "Frame-rate dependent physics, blocking operations in game loop, memory leaks in asset loading",
    },
    "shader_creative": {
        "name": "Shader / Creative Coding",
        "description": "Graphics programming, shaders, generative art, or creative coding",
        "languages": "GLSL, HLSL, WGSL, JavaScript, Python, Processing",
        "frameworks": [
            "Three.js", "p5.js", "Processing", "OpenGL", "WebGL",
            "WebGPU", "Shadertoy", "TouchDesigner", "OpenFrameworks"
        ],
        "platforms": ["Web", "Windows", "macOS", "Linux"],
        "suggested_criteria": [
            "Visuals render correctly",
            "Performance meets target frame rate",
            "Shaders compile without errors",
            "Parameters and uniforms work correctly",
            "Works across target GPUs/browsers",
            "Graceful fallback for unsupported hardware",
        ],
        "suggested_must_use": "GPU-efficient algorithms, proper uniform handling, responsive canvas sizing, requestAnimationFrame",
        "suggested_must_avoid": "Infinite loops in shaders, excessive texture samples, division by zero, GPU memory leaks",
    },
    # ===== Systems & Hardware =====
    "os_development": {
        "name": "OS / Systems Development",
        "description": "Operating system, kernel, driver, or low-level systems programming",
        "languages": "C, C++, Rust, Assembly",
        "frameworks": ["UEFI", "GRUB", "Limine", "seL4", "Zephyr RTOS"],
        "platforms": ["Linux", "Windows", "macOS", "Custom/Bare Metal"],
        "suggested_criteria": [
            "Kernel boots successfully on target hardware/emulator",
            "Memory management operates correctly without leaks",
            "Interrupt handlers respond within timing requirements",
            "System calls function correctly",
            "Hardware drivers initialize and operate properly",
            "System remains stable under load",
        ],
        "suggested_must_use": "Memory-safe patterns, proper synchronization primitives, hardware abstraction layers",
        "suggested_must_avoid": "Undefined behavior, unhandled interrupts, unbounded loops in kernel space, memory corruption",
    },
    "embedded": {
        "name": "Embedded / Maker",
        "description": "Arduino, Raspberry Pi, Jetson, ESP32, or other dev board projects",
        "languages": "C, C++ (Arduino), Python, MicroPython, CircuitPython, Rust (embedded-hal)",
        "frameworks": [
            # Core embedded frameworks
            "Arduino", "PlatformIO", "ESP-IDF", "Zephyr RTOS", "FreeRTOS",
            # Rust embedded
            "embedded-hal", "RTIC",
            # NVIDIA Jetson stack
            "JetPack SDK", "CUDA", "TensorRT", "PyTorch (Jetson)",
            # Edge AI / TinyML
            "TensorFlow Lite", "Edge Impulse", "TinyML",
            # Other
            "Raspberry Pi OS", "Pico SDK",
        ],
        "platforms": [
            "Arduino", "ESP32", "ESP8266", "STM32",
            "Raspberry Pi", "Raspberry Pi Pico (RP2040)",
            "NVIDIA Jetson (Nano, Orin, Thor)",
            "Nordic nRF52", "Teensy", "Linux",
        ],
        "suggested_criteria": [
            "Firmware compiles and uploads successfully",
            "Hardware peripherals initialize correctly",
            "Sensor readings are accurate within tolerance",
            "Communication protocols work reliably (I2C, SPI, UART, BLE, WiFi)",
            "Power consumption meets requirements",
            "System recovers gracefully from errors",
            "AI inference runs within latency/memory targets (if applicable)",
        ],
        "suggested_must_use": "Watchdog timers, proper pin initialization, interrupt-safe code, hardware abstraction layers, RTOS tasks for concurrency",
        "suggested_must_avoid": "Blocking delays in critical loops, floating/uninitialized inputs, unbounded memory allocation, ignoring hardware errata, busy-waiting when DMA/interrupts available, baud rate mismatches",
    },
    "blockchain": {
        "name": "Blockchain / DeFi",
        "description": "Cryptocurrency, smart contracts, or decentralized application development",
        "languages": "Solidity, Rust, Python, TypeScript, Move",
        "frameworks": ["Hardhat", "Foundry", "Anchor", "ethers.js", "web3.py", "OpenZeppelin"],
        "platforms": ["Ethereum", "Solana", "Polygon", "Arbitrum", "Linux", "Docker"],
        "suggested_criteria": [
            "Smart contracts compile without errors",
            "All contract tests pass",
            "No reentrancy vulnerabilities detected",
            "Gas optimization meets targets",
            "Contract upgrades work correctly",
            "Integration with wallets functions properly",
        ],
        "suggested_must_use": "Audited libraries (OpenZeppelin), comprehensive test coverage, formal verification where possible",
        "suggested_must_avoid": "Reentrancy patterns, unchecked external calls, floating pragma versions, storing sensitive data on-chain",
    },
}


class ProfileManager:
    """Manager for preset project profiles."""

    def __init__(self):
        """Initialize the profile manager with built-in profiles."""
        self._profiles = PROFILES.copy()
        self._categories = PROFILE_CATEGORIES.copy()
        self._custom_profiles: dict[str, dict[str, Any]] = {}

    def get_profile(self, name: str) -> dict[str, Any]:
        """
        Get a profile by name.

        Args:
            name: Profile name (e.g., 'web_app', 'cli_tool')

        Returns:
            Profile dictionary

        Raises:
            KeyError: If profile doesn't exist
        """
        if name in self._custom_profiles:
            return self._custom_profiles[name]
        if name in self._profiles:
            return self._profiles[name]
        raise KeyError(f"Profile '{name}' not found. Available: {self.list_profiles()}")

    def list_profiles(self) -> list[str]:
        """
        List all available profile names.

        Returns:
            List of profile names
        """
        return list(self._profiles.keys()) + list(self._custom_profiles.keys())

    def get_profile_names_with_descriptions(self) -> list[tuple[str, str, str]]:
        """
        Get profile names with their display names and descriptions.

        Returns:
            List of tuples: (key, display_name, description)
        """
        result = []
        for key, profile in self._profiles.items():
            result.append((key, profile["name"], profile.get("description", "")))
        for key, profile in self._custom_profiles.items():
            result.append((key, profile["name"], profile.get("description", "")))
        return result

    def apply_profile(self, base_config: dict[str, Any], profile_name: str) -> dict[str, Any]:
        """
        Apply a profile to a base configuration.

        Profile values fill in missing fields but don't override existing values.

        Args:
            base_config: Base configuration dictionary
            profile_name: Name of the profile to apply

        Returns:
            Merged configuration dictionary
        """
        profile = self.get_profile(profile_name)
        result = base_config.copy()

        # Map profile fields to config fields
        mappings = {
            "languages": "languages",
            "frameworks": "frameworks",
            "platforms": "platforms",
            "suggested_criteria": "success_criteria",
            "suggested_must_use": "must_use",
            "suggested_must_avoid": "must_avoid",
        }

        for profile_key, config_key in mappings.items():
            if profile_key in profile:
                if config_key not in result or not result[config_key]:
                    result[config_key] = profile[profile_key]

        # Add profile metadata
        result["_profile_name"] = profile_name
        result["_profile_display_name"] = profile.get("name", profile_name)

        return result

    def add_profile(self, name: str, profile: dict[str, Any]) -> None:
        """
        Add a custom profile.

        Args:
            name: Profile name/key
            profile: Profile configuration dictionary
        """
        if "name" not in profile:
            profile["name"] = name.replace("_", " ").title()
        self._custom_profiles[name] = profile

    def get_frameworks_for_profile(self, profile_name: str) -> list[str]:
        """
        Get the list of frameworks for a profile.

        Args:
            profile_name: Name of the profile

        Returns:
            List of framework names
        """
        profile = self.get_profile(profile_name)
        return profile.get("frameworks", [])

    # ===== Category Methods =====

    def list_categories(self) -> list[str]:
        """
        List all available category keys.

        Returns:
            List of category keys in display order
        """
        return list(self._categories.keys())

    def get_category(self, category_key: str) -> dict[str, Any]:
        """
        Get a category by key.

        Args:
            category_key: Category key (e.g., 'web', 'applications')

        Returns:
            Category dictionary with name, description, and profiles list

        Raises:
            KeyError: If category doesn't exist
        """
        if category_key in self._categories:
            return self._categories[category_key]
        raise KeyError(f"Category '{category_key}' not found. Available: {self.list_categories()}")

    def get_categories_with_profiles(self) -> list[dict[str, Any]]:
        """
        Get all categories with their profiles for menu display.

        Returns:
            List of dicts with category info and nested profile info:
            [
                {
                    "key": "web",
                    "name": "Web & Internet",
                    "description": "...",
                    "profiles": [
                        {"key": "website", "name": "Website", "description": "..."},
                        ...
                    ]
                },
                ...
            ]
        """
        result = []
        for cat_key, category in self._categories.items():
            cat_info = {
                "key": cat_key,
                "name": category["name"],
                "description": category.get("description", ""),
                "profiles": [],
            }
            for profile_key in category.get("profiles", []):
                if profile_key in self._profiles:
                    profile = self._profiles[profile_key]
                    cat_info["profiles"].append({
                        "key": profile_key,
                        "name": profile["name"],
                        "description": profile.get("description", ""),
                    })
            result.append(cat_info)
        return result

    def get_profiles_for_category(self, category_key: str) -> list[tuple[str, str, str]]:
        """
        Get profiles for a specific category.

        Args:
            category_key: Category key (e.g., 'web')

        Returns:
            List of tuples: (profile_key, display_name, description)
        """
        category = self.get_category(category_key)
        result = []
        for profile_key in category.get("profiles", []):
            if profile_key in self._profiles:
                profile = self._profiles[profile_key]
                result.append((
                    profile_key,
                    profile["name"],
                    profile.get("description", ""),
                ))
        return result

    def get_category_for_profile(self, profile_key: str) -> str | None:
        """
        Find which category a profile belongs to.

        Args:
            profile_key: Profile key (e.g., 'web_app')

        Returns:
            Category key if found, None otherwise
        """
        for cat_key, category in self._categories.items():
            if profile_key in category.get("profiles", []):
                return cat_key
        return None


class ReporProfileManager:
    """Manager for GECK Repor exploration profiles."""

    def __init__(self):
        """Initialize with built-in exploration profiles."""
        self._profiles = REPOR_PROFILES.copy()

    def get_profile(self, name: str) -> dict[str, Any]:
        """
        Get an exploration profile by name.

        Args:
            name: Profile name (e.g., 'feature_discovery')

        Returns:
            Profile dictionary

        Raises:
            KeyError: If profile doesn't exist
        """
        if name in self._profiles:
            return self._profiles[name]
        raise KeyError(f"Repor profile '{name}' not found. Available: {self.list_profiles()}")

    def list_profiles(self) -> list[str]:
        """
        List all available exploration profile names.

        Returns:
            List of profile names
        """
        return list(self._profiles.keys())

    def get_profile_choices(self) -> list[tuple[str, str, str]]:
        """
        Get profile choices for dropdown.

        Returns:
            List of tuples: (key, display_name, description)
        """
        result = [("none", "Custom / No Profile", "Enter your own exploration goals")]
        for key, profile in self._profiles.items():
            result.append((key, profile["name"], profile.get("description", "")))
        return result

    def get_goals_for_profile(self, profile_name: str) -> list[str]:
        """
        Get the exploration goals for a profile.

        Args:
            profile_name: Name of the profile

        Returns:
            List of goal strings
        """
        if profile_name == "none" or not profile_name:
            return []
        profile = self.get_profile(profile_name)
        return profile.get("goals", [])
