#!/usr/bin/env python3

from collections import defaultdict
from glob import glob
from os import path, makedirs
import time
from tabulate import tabulate
from typing import Dict, List, NamedTuple, Optional, Tuple
from subprocess import check_call, check_output
from sys import argv

test_dir=".build"

### Infrastructure ################

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
        runtime = (end - self.start) // (1000 * 1000)
        benchmarks[self.test_name] = benchmarks[self.test_name]._replace(**{self.aspect: runtime})

def benchmark(test_name: str, aspect: str) -> _Benchmark:
    return _Benchmark(test_name, aspect)

### Helpers #######################

def join(input_file: str, output_file: str) -> None:
    check_call(['mm0-rs', 'join', input_file, output_file])
def compile(input_file: str, output_file: str) -> None:
    check_call(['mm0-rs', 'compile', '-q', '--warn-as-error', input_file, output_file])
def check(mmb_file: str, mm0_file: str) -> None:
    with open(mm0_file) as f:
        check_call(['mm0-c', mmb_file], stdin=f)

def run_proof_gen(mode: str, theorem: str, regex: str, output_file: str) -> None:
    with open(output_file, 'w') as f:
        check_call(['./proof-gen.py', mode, theorem, regex], stdout=f)

### Tests #########################

def test_mm(mm0_file: str, mm1_file: str) -> None:
    basename = path.basename(mm1_file)
    test_name, extension = path.splitext(basename)
    output_basename = path.join(test_dir, test_name)
    output_joined = path.join(test_dir, test_name + '.joined' + extension)
    output_mmb    = path.join(test_dir, test_name + '.mmb')

    print("Testing: %s" % test_name)
    # There seems to be a bug in mm0-rs that causes the program to crash
    # when compiling un-joined files.
    with benchmark(test_name, 'join'):      join(mm1_file, output_joined)
    with benchmark(test_name, 'compile'):   compile(output_joined, output_mmb)
    with benchmark(test_name, 'check'):     check(output_mmb, mm0_file)


def test_regex(theorem: str, test_name: str, regex: str) -> None:
    output_mm0_file = path.join(test_dir, test_name + '.mm0')
    output_joined_mm0_file = path.join(test_dir, test_name + '.joined.mm0')
    output_mm1_file = path.join(test_dir, test_name + '.mm1')
    output_joined_mm1_file = path.join(test_dir, test_name + '.joined.mm1')

    with benchmark(test_name, 'gen_mm0'):  run_proof_gen('mm0', theorem, regex, output_mm0_file)
    with benchmark(test_name, 'join_mm0'): join(output_mm0_file, output_joined_mm0_file)
    with benchmark(test_name, 'gen_mm1'): run_proof_gen('mm1', theorem, regex, output_mm1_file)
    test_mm(output_joined_mm0_file, output_mm1_file)

fast = False
slow = True
TestData = Tuple[bool, str, str, str]

def param_test(theorem: str, test_name: str, regex: str, fast=[], slow=[]) -> List[TestData]:
    ret = []
    for param in fast:
        ret.append((fast, theorem, test_name.format(param), regex.format(param)))
    for param in slow:
        ret.append((slow, theorem, test_name.format(param), regex.format(param)))
    return ret

### Main #######################

# Arg parsing
usage = 'usage: test [--no-slow-tests]'
run_slow_tests = True
assert len(argv) <= 2, usage
if len(argv) == 2:
    if argv[1] == '--no-slow-tests':
        run_slow_tests = False
    else:
        raise AssertionError(usage)

# Check concrete MM0/MM1 lemmas
makedirs(test_dir, exist_ok=True)
last_mm0_file = None
for f in sorted((glob('*.mm0') + glob('*.mm1'))):
    if path.splitext(f)[1] == '.mm0':
        last_mm0_file = path.join(test_dir, 'joined.' + f)
        join(f, last_mm0_file)
    assert last_mm0_file
    test_mm(last_mm0_file, f)

# Regular expression tests
tests : List[TestData] = [
    (fast, 'main-goal',            'a-or-b-star',                '(a + b)*'),
    (fast, 'fp-implies-regex-pub', 'kleene-star-star',           '(a *) * ->> (a *)'),
    (fast, 'fp-implies-regex-pub', 'example-in-paper',           '(a . a)* ->> (((a *) . a) + epsilon) '),
    (fast, 'fp-implies-regex-pub', 'alternate-top',              '((a *) . b) * + (((b *) . a) *)'),
    (fast, 'fp-implies-regex-pub', 'even-or-odd',                '((((a . a) + (a . b)) + (b . a)) + (b . b)) * + ((a + b) . (((((a . a) + (a . b)) + (b . a)) + (b . b)) *))'),
    (fast, 'fp-implies-regex-pub', 'no-contains-a-or-no-only-b', '(~ (top . (a . top))) + ~ (b *)'),

    # Benchmarks from Unified Decision Procedures for Regular Expression Equivalence
    # https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=f650281fc011a2c132690903eb443ff1ab3298f7
    *param_test('fp-implies-regex-pub', 'match-l-{:03d}', 'match-l({})', fast=[1,4], slow=[2, 10, 20, 30, 40, 100]),
    *param_test('fp-implies-regex-pub', 'match-r-{:03d}', 'match-r({})', fast=[1,4], slow=[2, 10, 20, 30]),
    *param_test('fp-implies-regex-pub',    'eq-l-{:03d}',    'eq-l({})', fast=[1,4], slow=[2, 10, 20, 30]),
    *param_test('fp-implies-regex-pub',    'eq-r-{:03d}',    'eq-r({})', fast=[1,4], slow=[2, 10, 20, 30]),
    *param_test('fp-implies-regex-pub',   'eq-lr-{:03d}',   'eq-lr({})', fast=[1,4], slow=[2, 10, 20, 30]),
]

for test in tests:
    is_slow, theorem, name, expression = test
    if (not is_slow) or run_slow_tests:
        test_regex(theorem, name, expression)

print()
print_benchmarks()
