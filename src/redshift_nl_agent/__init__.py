"""
Redshift Natural Language Agent

A natural language to SQL query interface for Amazon Redshift.
Supports Google Gemini, Anthropic Claude, and rule-based SQL generation.
"""

__version__ = "1.0.0"

from .database import RedshiftCLI
from .schema import SchemaContext
from .agent import RedshiftAgent

__all__ = ['RedshiftCLI', 'SchemaContext', 'RedshiftAgent']
