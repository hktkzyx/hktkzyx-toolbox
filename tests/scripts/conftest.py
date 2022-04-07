from click import testing
import pytest


@pytest.fixture
def runner():
    runner = testing.CliRunner()
    yield runner
