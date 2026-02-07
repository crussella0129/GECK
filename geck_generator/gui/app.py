"""Tkinter GUI application for GECK Generator."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Any
import sys

from geck_generator.core.generator import GECKGenerator
from geck_generator.core.profiles import ProfileManager, ReporProfileManager
from geck_generator.utils.git_utils import (
    is_git_repo,
    suggest_repo_url,
    get_current_branch,
    get_branches,
    has_uncommitted_changes,
    checkout_branch,
    fetch_all,
)


def get_icon_path() -> Path | None:
    """Get the path to the application icon (.png preferred, .ico fallback)."""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
    else:
        base_path = Path(__file__).parent.parent

    resources = base_path / "resources"
    for ext in ("png", "ico"):
        icon_path = resources / f"geck_icon.{ext}"
        if icon_path.exists():
            return icon_path

    return None


class GECKGeneratorGUI:
    """Tkinter-based GUI for GECK Generator."""

    def __init__(self, root: tk.Tk):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("GECK Generator")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        self.generator = GECKGenerator()
        self.profiles = ProfileManager()
        self.repor_profiles = ReporProfileManager()

        # Variables for Bootstrapper
        self.project_name_var = tk.StringVar()
        self.repo_url_var = tk.StringVar()
        self.local_path_var = tk.StringVar(value=str(Path.cwd()))
        self.profile_var = tk.StringVar(value="none")
        self.languages_var = tk.StringVar()
        self.must_use_var = tk.StringVar()
        self.must_avoid_var = tk.StringVar()
        self.criteria_list: list[str] = []
        self.platforms_vars: dict[str, tk.BooleanVar] = {}

        # Variables for Repor
        self.repor_working_dir_var = tk.StringVar(value=str(Path.cwd()))
        self.repor_repos_list: list[str] = []
        self.repor_goals_list: list[str] = []
        self.repor_profile_var = tk.StringVar(value="none")

        # Git branch variables - Bootstrapper
        self.boot_branch_var = tk.StringVar()
        self.boot_branches: list[str] = []
        self.boot_is_git_repo = False
        self.boot_git_frame: ttk.LabelFrame | None = None

        # Git branch variables - Repor
        self.repor_branch_var = tk.StringVar()
        self.repor_branches: list[str] = []
        self.repor_is_git_repo = False
        self.repor_git_frame: ttk.LabelFrame | None = None

        # Frame references
        self.main_menu_frame: ttk.Frame | None = None
        self.bootstrapper_frame: ttk.Frame | None = None
        self.repor_frame: ttk.Frame | None = None

        self.setup_ui()

        # Check initial paths for git repos after UI is built
        initial_path = self.local_path_var.get()
        if initial_path and is_git_repo(initial_path):
            self._check_boot_git(initial_path)
        initial_repor_path = self.repor_working_dir_var.get()
        if initial_repor_path and is_git_repo(initial_repor_path):
            self._update_repor_git_ui(initial_repor_path)

    def setup_ui(self):
        """Set up the main UI components."""
        # Create menu bar
        self.setup_menu()

        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create all frames (initially hidden)
        self.setup_main_menu()
        self.setup_bootstrapper_ui()
        self.setup_repor_ui()

        # Show main menu initially
        self.show_main_menu()

    def setup_menu(self):
        """Set up the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Main Menu", command=self.show_main_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Create Desktop Shortcut", command=self.create_desktop_shortcut)
        tools_menu.add_command(label="Create Start Menu Shortcut", command=self.create_menu_shortcut)
        tools_menu.add_command(label="Create Both Shortcuts", command=self.create_both_shortcuts)
        tools_menu.add_separator()
        tools_menu.add_command(label="Remove All Shortcuts", command=self.remove_shortcuts)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_main_menu(self):
        """Set up the main menu / welcome screen."""
        self.main_menu_frame = ttk.Frame(self.main_container, padding=40)

        # Title
        title_label = ttk.Label(
            self.main_menu_frame,
            text="GECK Generator",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack(pady=(0, 40))

        # Buttons container
        buttons_frame = ttk.Frame(self.main_menu_frame)
        buttons_frame.pack(fill=tk.BOTH, expand=True)

        # GECK Bootstrapper button
        bootstrapper_frame = ttk.LabelFrame(
            buttons_frame,
            text="GECK Bootstrapper",
            padding=20
        )
        bootstrapper_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            bootstrapper_frame,
            text="Create LLM_init.md and GECK folder for new projects",
            font=("Segoe UI", 10)
        ).pack(pady=(0, 10))

        ttk.Button(
            bootstrapper_frame,
            text="Open Bootstrapper",
            command=self.show_bootstrapper,
            width=25
        ).pack()

        # GECK Repor button
        repor_frame = ttk.LabelFrame(
            buttons_frame,
            text="GECK Repor",
            padding=20
        )
        repor_frame.pack(fill=tk.X, pady=10)

        ttk.Label(
            repor_frame,
            text="Explore external repos to find improvements",
            font=("Segoe UI", 10)
        ).pack(pady=(0, 10))

        ttk.Button(
            repor_frame,
            text="Open Repor",
            command=self.show_repor,
            width=25
        ).pack()

    def setup_bootstrapper_ui(self):
        """Set up the Bootstrapper interface."""
        self.bootstrapper_frame = ttk.Frame(self.main_container)

        # Bottom button bar - pack FIRST with side=BOTTOM so it's always visible
        self.button_frame = ttk.Frame(self.bootstrapper_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))

        # Create notebook (tabs) - pack after button frame so it fills remaining space
        self.notebook = ttk.Notebook(self.bootstrapper_frame)
        self.notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Basic Info
        self.basic_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.basic_frame, text="Basic Info")
        self.setup_basic_tab()

        # Tab 2: Profile & Constraints
        self.profile_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.profile_frame, text="Profile & Constraints")
        self.setup_profile_tab()

        # Tab 3: Goals & Criteria
        self.goals_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.goals_frame, text="Goals & Criteria")
        self.setup_goals_tab()

        # Tab 4: Preview & Generate
        self.preview_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.preview_frame, text="Preview & Generate")
        self.setup_preview_tab()

        ttk.Button(
            self.button_frame, text="Preview", command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            self.button_frame, text="Bootstrap GECK Project", command=self.bootstrap_geck_project
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            self.button_frame, text="Back to Main Menu", command=self.show_main_menu
        ).pack(side=tk.RIGHT, padx=5)

    def setup_repor_ui(self):
        """Set up the Repor interface."""
        self.repor_frame = ttk.Frame(self.main_container)

        # Create scrollable canvas
        canvas = tk.Canvas(self.repor_frame)
        scrollbar = ttk.Scrollbar(self.repor_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=10)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bind mousewheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # Section 1: Working Directory
        self._repor_wd_frame = ttk.LabelFrame(scrollable_frame, text="Working Directory", padding=10)
        self._repor_wd_frame.pack(fill=tk.X, pady=5)
        wd_frame = self._repor_wd_frame

        wd_entry_frame = ttk.Frame(wd_frame)
        wd_entry_frame.pack(fill=tk.X)

        ttk.Entry(wd_entry_frame, textvariable=self.repor_working_dir_var, width=60).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(wd_entry_frame, text="Browse...", command=self.browse_repor_working_dir).pack(
            side=tk.LEFT, padx=(5, 0)
        )

        # Git Branch (initially hidden)
        self.repor_git_frame = ttk.LabelFrame(scrollable_frame, text="Git Branch", padding=5)
        # Not packed yet - shown only when a git repo is selected

        repor_branch_row = ttk.Frame(self.repor_git_frame)
        repor_branch_row.pack(fill=tk.X)

        self.repor_branch_combo = ttk.Combobox(
            repor_branch_row, textvariable=self.repor_branch_var, state="readonly", width=35
        )
        self.repor_branch_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(repor_branch_row, text="Checkout", command=self._repor_checkout_branch).pack(
            side=tk.LEFT, padx=(5, 0)
        )
        ttk.Button(repor_branch_row, text="Fetch Latest", command=self._repor_fetch_branches).pack(
            side=tk.LEFT, padx=(5, 0)
        )

        self.repor_git_status_var = tk.StringVar()
        self.repor_git_status_label = ttk.Label(
            self.repor_git_frame, textvariable=self.repor_git_status_var, foreground="gray"
        )
        self.repor_git_status_label.pack(anchor=tk.W, pady=(2, 0))

        # Section 2: Git Repositories
        repos_frame = ttk.LabelFrame(scrollable_frame, text="Git Repositories to Explore", padding=10)
        repos_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Repos listbox
        repos_list_frame = ttk.Frame(repos_frame)
        repos_list_frame.pack(fill=tk.BOTH, expand=True)

        self.repor_repos_listbox = tk.Listbox(repos_list_frame, height=6)
        self.repor_repos_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        repos_scrollbar = ttk.Scrollbar(repos_list_frame, orient=tk.VERTICAL)
        repos_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.repor_repos_listbox.config(yscrollcommand=repos_scrollbar.set)
        repos_scrollbar.config(command=self.repor_repos_listbox.yview)

        # Add/Remove repos
        repos_btn_frame = ttk.Frame(repos_frame)
        repos_btn_frame.pack(fill=tk.X, pady=5)

        self.new_repo_var = tk.StringVar()
        ttk.Entry(repos_btn_frame, textvariable=self.new_repo_var, width=50).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(repos_btn_frame, text="Add", command=self.add_repor_repo).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(repos_btn_frame, text="Remove", command=self.remove_repor_repo).pack(
            side=tk.LEFT
        )

        ttk.Label(repos_frame, text="Accepts GitHub, GitLab, or .git URLs", foreground="gray").pack(
            anchor=tk.W
        )

        # Section 3: Additional Goals
        goals_frame = ttk.LabelFrame(scrollable_frame, text="Additional Exploration Goals (Optional)", padding=10)
        goals_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Goals listbox
        goals_list_frame = ttk.Frame(goals_frame)
        goals_list_frame.pack(fill=tk.BOTH, expand=True)

        self.repor_goals_listbox = tk.Listbox(goals_list_frame, height=6)
        self.repor_goals_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        goals_scrollbar = ttk.Scrollbar(goals_list_frame, orient=tk.VERTICAL)
        goals_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.repor_goals_listbox.config(yscrollcommand=goals_scrollbar.set)
        goals_scrollbar.config(command=self.repor_goals_listbox.yview)

        # Add/Remove goals
        goals_btn_frame = ttk.Frame(goals_frame)
        goals_btn_frame.pack(fill=tk.X, pady=5)

        self.new_repor_goal_var = tk.StringVar()
        ttk.Entry(goals_btn_frame, textvariable=self.new_repor_goal_var, width=50).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(goals_btn_frame, text="Add", command=self.add_repor_goal).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(goals_btn_frame, text="Remove", command=self.remove_repor_goal).pack(
            side=tk.LEFT
        )

        ttk.Label(goals_frame, text="Specific instructions for what to look for", foreground="gray").pack(
            anchor=tk.W
        )

        # Section 4: Exploration Profile
        profile_frame = ttk.LabelFrame(scrollable_frame, text="Exploration Profile", padding=10)
        profile_frame.pack(fill=tk.X, pady=5)

        # Build profile choices
        profile_choices = self.repor_profiles.get_profile_choices()
        profile_values = [f"{name}" for _, name, _ in profile_choices]

        ttk.Label(profile_frame, text="Select Profile:").pack(anchor=tk.W)
        self.repor_profile_combo = ttk.Combobox(
            profile_frame,
            values=profile_values,
            state="readonly",
            width=40
        )
        self.repor_profile_combo.current(0)
        self.repor_profile_combo.pack(anchor=tk.W, pady=5)
        self.repor_profile_combo.bind("<<ComboboxSelected>>", self.on_repor_profile_change)

        # Store mapping of display name to key
        self._repor_profile_map = {name: key for key, name, _ in profile_choices}

        # Bottom button bar
        repor_button_frame = ttk.Frame(scrollable_frame)
        repor_button_frame.pack(fill=tk.X, pady=20)

        ttk.Button(
            repor_button_frame,
            text="Create GECK Repor Agent Instructions",
            command=self.create_repor_instructions
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            repor_button_frame,
            text="Back to Main Menu",
            command=self.show_main_menu
        ).pack(side=tk.RIGHT, padx=5)

    # Navigation methods
    def show_main_menu(self):
        """Show the main menu screen."""
        if self.bootstrapper_frame:
            self.bootstrapper_frame.pack_forget()
        if self.repor_frame:
            self.repor_frame.pack_forget()
        if self.main_menu_frame:
            self.main_menu_frame.pack(fill=tk.BOTH, expand=True)

    def show_bootstrapper(self):
        """Show the Bootstrapper interface."""
        if self.main_menu_frame:
            self.main_menu_frame.pack_forget()
        if self.repor_frame:
            self.repor_frame.pack_forget()
        if self.bootstrapper_frame:
            self.bootstrapper_frame.pack(fill=tk.BOTH, expand=True)

    def show_repor(self):
        """Show the Repor interface."""
        if self.main_menu_frame:
            self.main_menu_frame.pack_forget()
        if self.bootstrapper_frame:
            self.bootstrapper_frame.pack_forget()
        if self.repor_frame:
            self.repor_frame.pack(fill=tk.BOTH, expand=True)

    # Shortcut methods
    def create_desktop_shortcut(self):
        """Create a desktop shortcut."""
        self._create_shortcut("desktop")

    def create_menu_shortcut(self):
        """Create a start menu shortcut."""
        self._create_shortcut("menu")

    def create_both_shortcuts(self):
        """Create both desktop and menu shortcuts."""
        self._create_shortcut("both")

    def _create_shortcut(self, location: str):
        """Create shortcuts at the specified location."""
        try:
            from geck_generator.utils.shortcuts import create_shortcuts, get_platform
            created = create_shortcuts(location)
            if created:
                paths = "\n".join(f"  - {p}" for p in created)
                messagebox.showinfo(
                    "Shortcuts Created",
                    f"Shortcuts created successfully on {get_platform()}:\n\n{paths}"
                )
            else:
                messagebox.showwarning("No Shortcuts", "No shortcuts were created.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create shortcuts:\n{e}")

    def remove_shortcuts(self):
        """Remove all GECK Generator shortcuts."""
        try:
            from geck_generator.utils.shortcuts import remove_shortcuts
            removed = remove_shortcuts()
            if removed:
                paths = "\n".join(f"  - {p}" for p in removed)
                messagebox.showinfo(
                    "Shortcuts Removed",
                    f"Shortcuts removed:\n\n{paths}"
                )
            else:
                messagebox.showinfo("No Shortcuts", "No shortcuts found to remove.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove shortcuts:\n{e}")

    def show_about(self):
        """Show the about dialog."""
        from geck_generator import __version__
        messagebox.showinfo(
            "About GECK Generator",
            f"GECK Generator v{__version__}\n\n"
            "Generate LLM_init.md files for GECK v1.2 projects.\n\n"
            "Features:\n"
            "  - GECK Bootstrapper: Create project structures\n"
            "  - GECK Repor: Explore external repos\n"
            "  - Interactive CLI\n"
            "  - Preset Profiles"
        )

    # Bootstrapper tab setup methods
    def setup_basic_tab(self):
        """Set up the Basic Info tab."""
        # Project Name
        ttk.Label(self.basic_frame, text="Project Name:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(self.basic_frame, textvariable=self.project_name_var, width=50).grid(
            row=0, column=1, sticky=tk.EW, pady=5, padx=5
        )

        # Repository URL
        ttk.Label(self.basic_frame, text="Repository URL:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(self.basic_frame, textvariable=self.repo_url_var, width=50).grid(
            row=1, column=1, sticky=tk.EW, pady=5, padx=5
        )

        # Local Path
        ttk.Label(self.basic_frame, text="Local Path:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        path_frame = ttk.Frame(self.basic_frame)
        path_frame.grid(row=2, column=1, sticky=tk.EW, pady=5, padx=5)
        ttk.Entry(path_frame, textvariable=self.local_path_var, width=40).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(path_frame, text="Browse...", command=self.browse_path).pack(
            side=tk.LEFT, padx=(5, 0)
        )

        # Git Branch (row 3) - initially hidden
        self.boot_git_frame = ttk.LabelFrame(self.basic_frame, text="Git Branch", padding=5)
        # Not gridded yet - shown only when a git repo is selected

        branch_row = ttk.Frame(self.boot_git_frame)
        branch_row.pack(fill=tk.X)

        self.boot_branch_combo = ttk.Combobox(
            branch_row, textvariable=self.boot_branch_var, state="readonly", width=35
        )
        self.boot_branch_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(branch_row, text="Checkout", command=self._boot_checkout_branch).pack(
            side=tk.LEFT, padx=(5, 0)
        )
        ttk.Button(branch_row, text="Fetch Latest", command=self._boot_fetch_branches).pack(
            side=tk.LEFT, padx=(5, 0)
        )

        self.boot_git_status_var = tk.StringVar()
        self.boot_git_status_label = ttk.Label(
            self.boot_git_frame, textvariable=self.boot_git_status_var, foreground="gray"
        )
        self.boot_git_status_label.pack(anchor=tk.W, pady=(2, 0))

        # Configure column weights
        self.basic_frame.columnconfigure(1, weight=1)

    def setup_profile_tab(self):
        """Set up the Profile & Constraints tab."""
        # Profile selection with category-based navigation
        profile_label_frame = ttk.LabelFrame(
            self.profile_frame, text="Project Profile", padding=10
        )
        profile_label_frame.pack(fill=tk.X, pady=5)

        # Category selection
        category_frame = ttk.Frame(profile_label_frame)
        category_frame.pack(fill=tk.X, pady=5)

        ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT, padx=(0, 10))

        # Build category choices with "None" option
        self.category_choices = [("-- No Profile --", "none")]
        for cat in self.profiles.get_categories_with_profiles():
            self.category_choices.append((cat["name"], cat["key"]))

        self.category_var = tk.StringVar(value="none")
        self.category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            values=[c[0] for c in self.category_choices],
            state="readonly",
            width=30,
        )
        self.category_combo.current(0)
        self.category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.category_combo.bind("<<ComboboxSelected>>", self.on_category_change)

        # Profile selection within category
        profile_select_frame = ttk.Frame(profile_label_frame)
        profile_select_frame.pack(fill=tk.X, pady=5)

        ttk.Label(profile_select_frame, text="Profile:").pack(side=tk.LEFT, padx=(0, 10))

        self.profile_choices = [("-- Select Category First --", "none")]
        self.profile_combo = ttk.Combobox(
            profile_select_frame,
            textvariable=self.profile_var,
            values=[p[0] for p in self.profile_choices],
            state="readonly",
            width=30,
        )
        self.profile_combo.current(0)
        self.profile_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.profile_combo.bind("<<ComboboxSelected>>", self.on_profile_combo_change)

        # Profile description label
        self.profile_desc_var = tk.StringVar(value="")
        self.profile_desc_label = ttk.Label(
            profile_label_frame,
            textvariable=self.profile_desc_var,
            wraplength=500,
            foreground="gray",
        )
        self.profile_desc_label.pack(anchor=tk.W, pady=(5, 0))

        # Constraints
        constraints_frame = ttk.LabelFrame(
            self.profile_frame, text="Constraints", padding=10
        )
        constraints_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Languages
        ttk.Label(constraints_frame, text="Languages/Frameworks:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(constraints_frame, textvariable=self.languages_var, width=50).grid(
            row=0, column=1, sticky=tk.EW, pady=5, padx=5
        )

        # Must use
        ttk.Label(constraints_frame, text="Must Use:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(constraints_frame, textvariable=self.must_use_var, width=50).grid(
            row=1, column=1, sticky=tk.EW, pady=5, padx=5
        )

        # Must avoid
        ttk.Label(constraints_frame, text="Must Avoid:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(constraints_frame, textvariable=self.must_avoid_var, width=50).grid(
            row=2, column=1, sticky=tk.EW, pady=5, padx=5
        )

        # Platforms
        ttk.Label(constraints_frame, text="Target Platforms:").grid(
            row=3, column=0, sticky=tk.NW, pady=5
        )
        platforms_frame = ttk.Frame(constraints_frame)
        platforms_frame.grid(row=3, column=1, sticky=tk.W, pady=5, padx=5)

        platform_options = ["Windows", "macOS", "Linux", "Docker", "iOS", "Android", "Web"]
        for i, platform in enumerate(platform_options):
            var = tk.BooleanVar()
            self.platforms_vars[platform] = var
            cb = ttk.Checkbutton(platforms_frame, text=platform, variable=var)
            cb.grid(row=i // 4, column=i % 4, sticky=tk.W, padx=5)

        constraints_frame.columnconfigure(1, weight=1)

    def setup_goals_tab(self):
        """Set up the Goals & Criteria tab."""
        # Goal
        goal_frame = ttk.LabelFrame(self.goals_frame, text="Project Goal", padding=10)
        goal_frame.pack(fill=tk.X, pady=5)

        ttk.Label(goal_frame, text="Describe what should exist when the project is complete:").pack(
            anchor=tk.W
        )
        self.goal_text = scrolledtext.ScrolledText(goal_frame, height=4, wrap=tk.WORD)
        self.goal_text.pack(fill=tk.X, expand=True, pady=5)

        # Context
        context_frame = ttk.LabelFrame(self.goals_frame, text="Context (Optional)", padding=10)
        context_frame.pack(fill=tk.X, pady=5)

        ttk.Label(context_frame, text="Background information:").pack(anchor=tk.W)
        self.context_text = scrolledtext.ScrolledText(context_frame, height=3, wrap=tk.WORD)
        self.context_text.pack(fill=tk.X, expand=True, pady=5)

        # Initial Task
        task_frame = ttk.LabelFrame(self.goals_frame, text="Initial Task (Optional)", padding=10)
        task_frame.pack(fill=tk.X, pady=5)

        ttk.Label(task_frame, text="Additional first task to work on:").pack(anchor=tk.W)
        self.initial_task_text = scrolledtext.ScrolledText(task_frame, height=2, wrap=tk.WORD)
        self.initial_task_text.pack(fill=tk.X, expand=True, pady=5)

        # Info about default task
        default_task_info = ttk.Label(
            task_frame,
            text='Note: "Compile task list from log and LLM_init entries" is always included as the first task.',
            foreground="gray",
            wraplength=500,
        )
        default_task_info.pack(anchor=tk.W, pady=(5, 0))

        # Success Criteria
        criteria_frame = ttk.LabelFrame(
            self.goals_frame, text="Success Criteria", padding=10
        )
        criteria_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Criteria list
        list_frame = ttk.Frame(criteria_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.criteria_listbox = tk.Listbox(list_frame, height=6)
        self.criteria_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.criteria_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.criteria_listbox.yview)

        # Add/Remove buttons
        btn_frame = ttk.Frame(criteria_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.new_criterion_var = tk.StringVar()
        ttk.Entry(btn_frame, textvariable=self.new_criterion_var, width=40).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(btn_frame, text="Add", command=self.add_criterion).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(btn_frame, text="Remove", command=self.remove_criterion).pack(
            side=tk.LEFT
        )

    def setup_preview_tab(self):
        """Set up the Preview & Generate tab."""
        ttk.Label(self.preview_frame, text="Generated LLM_init.md:").pack(anchor=tk.W)

        self.preview_text = scrolledtext.ScrolledText(
            self.preview_frame, height=25, wrap=tk.WORD
        )
        self.preview_text.pack(fill=tk.BOTH, expand=True, pady=5)

        ttk.Button(
            self.preview_frame, text="Refresh Preview", command=self.update_preview
        ).pack(pady=5)

    # Bootstrapper action methods
    def browse_path(self):
        """Open file dialog to browse for a directory."""
        path = filedialog.askdirectory(initialdir=self.local_path_var.get())
        if path:
            self.local_path_var.set(path)
            self._check_boot_git(path)

    def _check_boot_git(self, path: str):
        """Check if path is a git repo and update UI accordingly."""
        if is_git_repo(path):
            url = suggest_repo_url(path)
            if url and not self.repo_url_var.get():
                self.repo_url_var.set(url)
            self._update_boot_git_ui(path)
        else:
            self._hide_boot_git_ui()

    def on_category_change(self, event=None):
        """Handle category selection change."""
        # Find the selected category key
        selected_text = self.category_combo.get()
        category_key = "none"
        for name, key in self.category_choices:
            if name == selected_text:
                category_key = key
                break

        # Update profile dropdown based on category
        if category_key == "none":
            self.profile_choices = [("-- No Profile --", "none")]
            self.profile_var.set("none")
            self.profile_desc_var.set("")
        else:
            profiles = self.profiles.get_profiles_for_category(category_key)
            self.profile_choices = [(name, key) for key, name, desc in profiles]
            if self.profile_choices:
                # Select first profile in category
                self.profile_var.set(self.profile_choices[0][1])

        # Update profile combobox values
        self.profile_combo["values"] = [p[0] for p in self.profile_choices]
        if self.profile_choices:
            self.profile_combo.current(0)

        # Trigger profile change to update fields
        self.on_profile_combo_change()

    def on_profile_combo_change(self, event=None):
        """Handle profile selection change from combobox."""
        # Find the selected profile key
        selected_text = self.profile_combo.get()
        profile_key = "none"
        for name, key in self.profile_choices:
            if name == selected_text:
                profile_key = key
                break

        self.profile_var.set(profile_key)

        if profile_key == "none":
            self.profile_desc_var.set("")
            return

        profile = self.profiles.get_profile(profile_key)

        # Update description
        self.profile_desc_var.set(profile.get("description", ""))

        # Update languages
        if profile.get("languages"):
            self.languages_var.set(profile["languages"])

        # Update must use/avoid
        if profile.get("suggested_must_use"):
            self.must_use_var.set(profile["suggested_must_use"])
        if profile.get("suggested_must_avoid"):
            self.must_avoid_var.set(profile["suggested_must_avoid"])

        # Update platforms
        for platform in self.platforms_vars:
            self.platforms_vars[platform].set(
                platform in profile.get("platforms", [])
            )

        # Update suggested criteria
        if profile.get("suggested_criteria"):
            self.criteria_list = profile["suggested_criteria"].copy()
            self.update_criteria_listbox()

    def add_criterion(self):
        """Add a new success criterion."""
        criterion = self.new_criterion_var.get().strip()
        if criterion:
            self.criteria_list.append(criterion)
            self.update_criteria_listbox()
            self.new_criterion_var.set("")

    def remove_criterion(self):
        """Remove the selected success criterion."""
        selection = self.criteria_listbox.curselection()
        if selection:
            index = selection[0]
            del self.criteria_list[index]
            self.update_criteria_listbox()

    def update_criteria_listbox(self):
        """Update the criteria listbox display."""
        self.criteria_listbox.delete(0, tk.END)
        for criterion in self.criteria_list:
            self.criteria_listbox.insert(tk.END, criterion)

    def collect_form_data(self) -> dict[str, Any]:
        """Collect all form data into a config dictionary."""
        config = {
            "project_name": self.project_name_var.get(),
            "repo_url": self.repo_url_var.get(),
            "local_path": self.local_path_var.get(),
            "profile": self.profile_var.get() if self.profile_var.get() != "none" else None,
            "languages": self.languages_var.get(),
            "must_use": self.must_use_var.get(),
            "must_avoid": self.must_avoid_var.get(),
            "goal": self.goal_text.get("1.0", tk.END).strip(),
            "context": self.context_text.get("1.0", tk.END).strip(),
            "initial_task": self.initial_task_text.get("1.0", tk.END).strip(),
            "success_criteria": self.criteria_list.copy(),
            "platforms": [
                p for p, var in self.platforms_vars.items() if var.get()
            ],
            "git_branch": get_current_branch(self.local_path_var.get()) if self.boot_is_git_repo else None,
        }
        return config

    def update_preview(self):
        """Update the preview pane with generated content."""
        config = self.collect_form_data()
        content = self.generator.generate(config)
        self.preview_text.delete("1.0", tk.END)
        self.preview_text.insert("1.0", content)

        # Switch to preview tab
        self.notebook.select(3)

    def bootstrap_geck_project(self):
        """Create full GECK project structure in the specified local path."""
        config = self.collect_form_data()

        # Validate config
        errors = self.generator.validate_config(config)
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Validate local path
        local_path = config.get("local_path", "").strip()
        if not local_path:
            messagebox.showerror("Validation Error", "Local Path is required.")
            return

        dirpath = Path(local_path)
        if not dirpath.exists():
            messagebox.showerror("Validation Error", f"Local Path does not exist:\n{dirpath}")
            return

        if not dirpath.is_dir():
            messagebox.showerror("Validation Error", f"Local Path is not a directory:\n{dirpath}")
            return

        try:
            geck_path = self.generator.init_geck_folder(dirpath, config)
            files = sorted([f.name for f in geck_path.iterdir()])
            messagebox.showinfo(
                "Success",
                f"GECK project bootstrapped successfully!\n\n"
                f"Created: {geck_path}/\n"
                + "\n".join(f"  - {f}" for f in files)
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to bootstrap GECK project:\n{e}")

    # Bootstrapper git branch methods
    def _update_boot_git_ui(self, path: str):
        """Show and populate the git branch UI for Bootstrapper."""
        self.boot_is_git_repo = True
        self.boot_branches = get_branches(path, include_remote=False)
        current = get_current_branch(path)

        self.boot_branch_combo["values"] = self.boot_branches
        if current and current in self.boot_branches:
            self.boot_branch_var.set(current)
        elif self.boot_branches:
            self.boot_branch_var.set(self.boot_branches[0])

        status = f"Current branch: {current}" if current else "Detached HEAD"
        if has_uncommitted_changes(path):
            status += " (uncommitted changes)"
        self.boot_git_status_var.set(status)

        self.boot_git_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5, padx=5)

    def _hide_boot_git_ui(self):
        """Hide the git branch UI for Bootstrapper."""
        self.boot_is_git_repo = False
        self.boot_git_frame.grid_forget()

    def _boot_checkout_branch(self):
        """Checkout the selected branch in the Bootstrapper path."""
        path = self.local_path_var.get()
        branch = self.boot_branch_var.get()
        if not path or not branch:
            return

        if has_uncommitted_changes(path):
            messagebox.showwarning(
                "Uncommitted Changes",
                "You have uncommitted changes. Please commit or stash them before switching branches."
            )
            return

        success, msg = checkout_branch(path, branch)
        if success:
            self._update_boot_git_ui(path)
        else:
            messagebox.showerror("Checkout Failed", msg)

    def _boot_fetch_branches(self):
        """Fetch latest from all remotes and refresh branch list."""
        path = self.local_path_var.get()
        if not path:
            return

        self.boot_git_status_var.set("Fetching...")
        self.root.update_idletasks()

        success, msg = fetch_all(path)
        if success:
            self._update_boot_git_ui(path)
        else:
            self.boot_git_status_var.set(f"Fetch failed: {msg}")

    # Repor action methods
    def browse_repor_working_dir(self):
        """Open file dialog to browse for Repor working directory."""
        path = filedialog.askdirectory(initialdir=self.repor_working_dir_var.get())
        if path:
            self.repor_working_dir_var.set(path)
            if is_git_repo(path):
                self._update_repor_git_ui(path)
            else:
                self._hide_repor_git_ui()

    def add_repor_repo(self):
        """Add a repository URL to the Repor list."""
        repo = self.new_repo_var.get().strip()
        if repo:
            self.repor_repos_list.append(repo)
            self.update_repor_repos_listbox()
            self.new_repo_var.set("")

    def remove_repor_repo(self):
        """Remove the selected repository from the Repor list."""
        selection = self.repor_repos_listbox.curselection()
        if selection:
            index = selection[0]
            del self.repor_repos_list[index]
            self.update_repor_repos_listbox()

    def update_repor_repos_listbox(self):
        """Update the Repor repos listbox display."""
        self.repor_repos_listbox.delete(0, tk.END)
        for repo in self.repor_repos_list:
            self.repor_repos_listbox.insert(tk.END, repo)

    def add_repor_goal(self):
        """Add a goal to the Repor goals list."""
        goal = self.new_repor_goal_var.get().strip()
        if goal:
            self.repor_goals_list.append(goal)
            self.update_repor_goals_listbox()
            self.new_repor_goal_var.set("")

    def remove_repor_goal(self):
        """Remove the selected goal from the Repor goals list."""
        selection = self.repor_goals_listbox.curselection()
        if selection:
            index = selection[0]
            del self.repor_goals_list[index]
            self.update_repor_goals_listbox()

    def update_repor_goals_listbox(self):
        """Update the Repor goals listbox display."""
        self.repor_goals_listbox.delete(0, tk.END)
        for goal in self.repor_goals_list:
            self.repor_goals_listbox.insert(tk.END, goal)

    def on_repor_profile_change(self, event=None):
        """Handle Repor profile selection change."""
        # Profile change is handled at generation time
        pass

    def get_repor_profile_key(self) -> str:
        """Get the selected Repor profile key."""
        display_name = self.repor_profile_combo.get()
        return self._repor_profile_map.get(display_name, "none")

    # Repor git branch methods
    def _update_repor_git_ui(self, path: str):
        """Show and populate the git branch UI for Repor."""
        self.repor_is_git_repo = True
        self.repor_branches = get_branches(path, include_remote=False)
        current = get_current_branch(path)

        self.repor_branch_combo["values"] = self.repor_branches
        if current and current in self.repor_branches:
            self.repor_branch_var.set(current)
        elif self.repor_branches:
            self.repor_branch_var.set(self.repor_branches[0])

        status = f"Current branch: {current}" if current else "Detached HEAD"
        if has_uncommitted_changes(path):
            status += " (uncommitted changes)"
        self.repor_git_status_var.set(status)

        # Pack after the Working Directory section
        self.repor_git_frame.pack(fill=tk.X, pady=5, after=self._repor_wd_frame)

    def _hide_repor_git_ui(self):
        """Hide the git branch UI for Repor."""
        self.repor_is_git_repo = False
        self.repor_git_frame.pack_forget()

    def _repor_checkout_branch(self):
        """Checkout the selected branch in the Repor working directory."""
        path = self.repor_working_dir_var.get()
        branch = self.repor_branch_var.get()
        if not path or not branch:
            return

        if has_uncommitted_changes(path):
            messagebox.showwarning(
                "Uncommitted Changes",
                "You have uncommitted changes. Please commit or stash them before switching branches."
            )
            return

        success, msg = checkout_branch(path, branch)
        if success:
            self._update_repor_git_ui(path)
        else:
            messagebox.showerror("Checkout Failed", msg)

    def _repor_fetch_branches(self):
        """Fetch latest from all remotes and refresh branch list for Repor."""
        path = self.repor_working_dir_var.get()
        if not path:
            return

        self.repor_git_status_var.set("Fetching...")
        self.root.update_idletasks()

        success, msg = fetch_all(path)
        if success:
            self._update_repor_git_ui(path)
        else:
            self.repor_git_status_var.set(f"Fetch failed: {msg}")

    def create_repor_instructions(self):
        """Create GECK Repor agent instructions file."""
        working_dir = self.repor_working_dir_var.get().strip()

        # Validate
        if not working_dir:
            messagebox.showerror("Validation Error", "Working directory is required.")
            return

        if not Path(working_dir).exists():
            messagebox.showerror("Validation Error", f"Working directory does not exist:\n{working_dir}")
            return

        if not self.repor_repos_list:
            messagebox.showerror("Validation Error", "At least one repository URL is required.")
            return

        # Ask for save location
        default_filename = "GECK_Repor_Instructions.md"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile=default_filename,
            initialdir=working_dir,
        )

        if not filepath:
            return

        try:
            profile_key = self.get_repor_profile_key()
            content = self.generator.generate_repor_instructions(
                working_directory=working_dir,
                repositories=self.repor_repos_list,
                exploration_goals=self.repor_goals_list,
                profile_name=profile_key,
                output_path=filepath,
            )
            messagebox.showinfo(
                "Success",
                f"GECK Repor instructions created:\n{filepath}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create Repor instructions:\n{e}")


def run_gui():
    """Run the GUI application."""
    # Set AppUserModelID on Windows so taskbar shows our icon instead of Python's
    try:
        import ctypes
        app_id = "geck.generator.gui.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except (ImportError, AttributeError, OSError):
        pass  # Not on Windows or failed, continue anyway

    root = tk.Tk()

    # Set application icon
    icon_path = get_icon_path()
    if icon_path:
        try:
            if icon_path.suffix == ".png":
                icon_image = tk.PhotoImage(file=str(icon_path))
                root.iconphoto(True, icon_image)
            else:
                root.iconbitmap(str(icon_path))
        except tk.TclError:
            pass  # Icon loading failed, continue without it

    app = GECKGeneratorGUI(root)

    # Ensure window appears on screen and is visible
    root.update_idletasks()

    # Center the window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"+{x}+{y}")

    # Bring window to front
    root.deiconify()
    root.lift()
    root.focus_force()

    root.mainloop()


if __name__ == "__main__":
    run_gui()
