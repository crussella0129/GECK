"""
GECK Generator - Generate LLM_init.md files for GECK v1.2 projects.

Supports four interfaces:
- Interactive CLI prompts
- GUI application
- Template substitution
- Preset profiles
"""

__version__ = "1.0.0"
__author__ = "GECK Generator"

from geck_generator.core.generator import GECKGenerator
from geck_generator.core.profiles import ProfileManager
from geck_generator.core.templates import TemplateEngine

__all__ = ["GECKGenerator", "ProfileManager", "TemplateEngine", "__version__"]
