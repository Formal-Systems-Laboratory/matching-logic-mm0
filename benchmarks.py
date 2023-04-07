from collections import defaultdict
from tabulate import tabulate
import time
from typing import Dict, List, NamedTuple, Optional, Tuple, no_type_check

### Benchmarks ##################

class Benchmark(NamedTuple):
    join:      Optional[int] = None
    compile:   Optional[int] = None
    check:     Optional[int] = None
    gen_mm0:   Optional[int] = None
    join_mm0:  Optional[int] = None
    gen_mm1:   Optional[int] = None

benchmarks : Dict[str, Benchmark] = defaultdict(lambda: Benchmark())

def print_benchmarks() -> None:
    print(tabulate(((name, *value) for (name, value) in sorted(benchmarks.items())),
                    headers=('name',) +  Benchmark._fields
         )        )

class _Benchmark():
    def __init__(self, test_name: str, aspect: str):
        self.test_name = test_name
        self.aspect = aspect
        self.start = time.time_ns()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time_ns()
        runtime = (end - self.start)
        benchmarks[self.test_name] = benchmarks[self.test_name]._replace(**{self.aspect: runtime})

def benchmark(test_name: str, aspect: str) -> _Benchmark:
    return _Benchmark(test_name, aspect)

