"""
Setup script for AI Voice Assistant Pro
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-voice-assistant-pro",
    version="1.0.0",
    author="Faizan Arshad",
    author_email="faizanarshad124@gmail.com",
    description="Advanced AI-Powered Voice Assistant with Modern Web Interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Voice_Chatbot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Chat",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.950",
        ],
        "docker": [
            "gunicorn>=20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "voice-assistant=voice_chatbot.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "voice_chatbot": [
            "web/static/**/*",
            "web/templates/**/*",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/Voice_Chatbot/issues",
        "Source": "https://github.com/yourusername/Voice_Chatbot",
        "Documentation": "https://github.com/yourusername/Voice_Chatbot/blob/main/README.md",
    },
)
