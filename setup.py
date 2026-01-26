"""Setup script for GECK Generator."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="geck-generator",
    version="1.0.0",
    author="GECK Generator",
    description="Generate LLM_init.md files for GECK v1.2 projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/example/geck-generator",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "questionary>=2.0.0",
        "jinja2>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "geck-generator=geck_generator.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: X11 Applications :: Tk",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords="geck llm generator markdown template",
)
