import pytest
from typing import no_type_check
from typing import Dict, List, NamedTuple, Optional, Tuple, no_type_check
import benchmarks
import csv

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

def pytest_sessionfinish(session) -> None:
    with open('.build/benchmarks.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['name'] + benchmarks.benchmark_fields())
        writer.writeheader()

        for (name, b) in benchmarks.benchmarks.items():
            d = b._asdict_nested()
            d['name'] = name
            writer.writerow(d)
