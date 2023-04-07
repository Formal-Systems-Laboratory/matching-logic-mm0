import pytest
from typing import no_type_check
import benchmarks

@no_type_check
def pytest_addoption(parser):
    parser.addoption('--skip-slow', action='store_true', help='Skip tests marked slow')

@no_type_check
def pytest_runtest_setup(item):
    if 'slow' in item.keywords and item.config.getoption("--skip-slow"):
        pytest.skip("slow test.")

@no_type_check
def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow.")

@no_type_check
def pytest_sessionfinish(session):
    print()
    benchmarks.print_benchmarks()
