"""
Pytest configuration and fixtures for Redshift Natural Language Agent tests
"""

import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture(scope="session")
def db_credentials():
    """Database connection credentials from environment"""
    return {
        'host': os.getenv('REDSHIFT_HOST', 'daplabs.955954582473.us-east-1.redshift-serverless.amazonaws.com'),
        'port': int(os.getenv('REDSHIFT_PORT', '5439')),
        'database': os.getenv('REDSHIFT_DATABASE', 'prod'),
        'user': os.getenv('REDSHIFT_USER', 'moonshoot_dev'),
        'password': os.getenv('REDSHIFT_PASSWORD'),
    }


@pytest.fixture(scope="session")
def gemini_api_key():
    """Gemini API key from environment"""
    return os.getenv('GEMINI_API_KEY')


@pytest.fixture(scope="session")
def anthropic_api_key():
    """Anthropic API key from environment"""
    return os.getenv('ANTHROPIC_API_KEY')


@pytest.fixture(scope="function")
def redshift_cli(db_credentials):
    """Create a RedshiftCLI instance for testing"""
    from redshift_nl_agent.database import RedshiftCLI

    cli = RedshiftCLI(**db_credentials)
    yield cli
    cli.close()


@pytest.fixture(scope="function")
def redshift_agent(db_credentials, gemini_api_key, anthropic_api_key):
    """Create a RedshiftAgent instance for testing"""
    from redshift_nl_agent.agent import RedshiftAgent

    agent = RedshiftAgent(
        db_credentials['host'],
        db_credentials['port'],
        db_credentials['database'],
        db_credentials['user'],
        db_credentials['password'],
        gemini_api_key=gemini_api_key,
        anthropic_api_key=anthropic_api_key
    )
    yield agent
    agent.cli.close()


@pytest.fixture(scope="function")
def schema_context(redshift_cli):
    """Create a SchemaContext instance for testing"""
    from redshift_nl_agent.schema import SchemaContext

    return SchemaContext(redshift_cli)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "validation: mark test as a validation test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database connection"
    )
    config.addinivalue_line(
        "markers", "requires_api: mark test as requiring API keys"
    )
