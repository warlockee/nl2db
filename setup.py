#!/usr/bin/env python3
"""
Setup configuration for Redshift Natural Language Agent
"""

from setuptools import setup, find_packages
import os

# Read README for long description
readme_path = os.path.join(os.path.dirname(__file__), 'docs', 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
else:
    long_description = 'Natural language to SQL query interface for Amazon Redshift'

setup(
    name="redshift-nl-agent",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Natural language to SQL query interface for Amazon Redshift",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/redshift-nl-agent",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/redshift-nl-agent/issues",
        "Documentation": "https://github.com/yourusername/redshift-nl-agent/tree/main/docs",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "psycopg2-binary>=2.9.0",
    ],
    extras_require={
        "llm": [
            "google-generativeai>=0.3.0",
            "anthropic>=0.7.0",
        ],
        "formatting": [
            "tabulate>=0.9.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "all": [
            "google-generativeai>=0.3.0",
            "anthropic>=0.7.0",
            "tabulate>=0.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "redshift-agent=redshift_nl_agent.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
