"""Tkinter GUI application for GECK Generator."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Any

from geck_generator.core.generator import GECKGenerator
from geck_generator.core.profiles import ProfileManager


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

        # Variables
        self.project_name_var = tk.StringVar()
        self.repo_url_var = tk.StringVar()
        self.local_path_var = tk.StringVar(value=str(Path.cwd()))
        self.profile_var = tk.StringVar(value="none")
        self.languages_var = tk.StringVar()
        self.must_use_var = tk.StringVar()
        self.must_avoid_var = tk.StringVar()
        self.criteria_list: list[str] = []
        self.platforms_vars: dict[str, tk.BooleanVar] = {}

        self.setup_ui()

    def setup_ui(self):
        """Set up the main UI components."""
        # Create menu bar
        self.setup_menu()

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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

        # Bottom button bar
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(
            self.button_frame, text="Preview", command=self.update_preview
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            self.button_frame, text="Save LLM_init.md", command=self.save_file
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            self.button_frame, text="Create GECK Folder", command=self.create_geck_folder
        ).pack(side=tk.LEFT, padx=5)

    def setup_menu(self):
        """Set up the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save LLM_init.md...", command=self.save_file)
        file_menu.add_command(label="Create GECK Folder...", command=self.create_geck_folder)
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
            "Supports:\n"
            "  - Interactive CLI\n"
            "  - GUI Application\n"
            "  - Template Substitution\n"
            "  - Preset Profiles"
        )

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

        # Configure column weights
        self.basic_frame.columnconfigure(1, weight=1)

    def setup_profile_tab(self):
        """Set up the Profile & Constraints tab."""
        # Profile selection
        profile_label_frame = ttk.LabelFrame(
            self.profile_frame, text="Project Profile", padding=10
        )
        profile_label_frame.pack(fill=tk.X, pady=5)

        ttk.Label(profile_label_frame, text="Select Profile:").pack(anchor=tk.W)

        profile_choices = [("None", "none")]
        for key, name, desc in self.profiles.get_profile_names_with_descriptions():
            profile_choices.append((f"{name}", key))

        for text, value in profile_choices:
            rb = ttk.Radiobutton(
                profile_label_frame,
                text=text,
                value=value,
                variable=self.profile_var,
                command=self.on_profile_change,
            )
            rb.pack(anchor=tk.W, pady=2)

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
        task_frame = ttk.LabelFrame(self.goals_frame, text="Initial Task", padding=10)
        task_frame.pack(fill=tk.X, pady=5)

        ttk.Label(task_frame, text="What is the first task to work on?").pack(anchor=tk.W)
        self.initial_task_text = scrolledtext.ScrolledText(task_frame, height=2, wrap=tk.WORD)
        self.initial_task_text.pack(fill=tk.X, expand=True, pady=5)

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

    def browse_path(self):
        """Open file dialog to browse for a directory."""
        path = filedialog.askdirectory(initialdir=self.local_path_var.get())
        if path:
            self.local_path_var.set(path)

    def on_profile_change(self):
        """Handle profile selection change."""
        profile_key = self.profile_var.get()
        if profile_key == "none":
            return

        profile = self.profiles.get_profile(profile_key)

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

    def save_file(self):
        """Save the generated content to a file."""
        config = self.collect_form_data()

        # Validate
        errors = self.generator.validate_config(config)
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Ask for save location
        default_path = Path(config.get("local_path", ".")) / "LLM_init.md"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialfile="LLM_init.md",
            initialdir=str(default_path.parent),
        )

        if not filepath:
            return

        try:
            self.generator.generate_to_file(config, filepath)
            messagebox.showinfo("Success", f"File saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def create_geck_folder(self):
        """Create a full GECK folder structure."""
        config = self.collect_form_data()

        # Validate
        errors = self.generator.validate_config(config)
        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return

        # Ask for directory
        dirpath = filedialog.askdirectory(
            title="Select directory to create GECK folder in",
            initialdir=config.get("local_path", "."),
        )

        if not dirpath:
            return

        try:
            geck_path = self.generator.init_geck_folder(dirpath, config)
            files = [f.name for f in geck_path.iterdir()]
            messagebox.showinfo(
                "Success",
                f"GECK folder created at:\n{geck_path}\n\nFiles created:\n" + "\n".join(f"  - {f}" for f in files)
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create GECK folder:\n{e}")


def run_gui():
    """Run the GUI application."""
    root = tk.Tk()
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
