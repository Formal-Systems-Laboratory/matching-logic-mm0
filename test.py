#!/usr/bin/env python3

from collections import defaultdict
from glob import glob
from os import path, makedirs
from subprocess import check_call, check_output
from sys import argv
import time
from typing import Dict, NamedTuple, Optional
from tabulate import tabulate

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


### Main #######################

usage = 'usage: test [--no-slow-tests]'
# parse_args
assert len(argv) <= 2, usage
run_slow_tests = True
if len(argv) == 2:
    if argv[1] == '--no-slow-tests':
        which_tests = False
    else:
        raise AssertionError(usage)

makedirs(test_dir, exist_ok=True)
last_mm0_file = None
for f in sorted((glob('*.mm0') + glob('*.mm1'))):
    if path.splitext(f)[1] == '.mm0':
        last_mm0_file = path.join(test_dir, 'joined.' + f)
        join(f, last_mm0_file)
    assert last_mm0_file
    test_mm(last_mm0_file, f)

test_regex('main-goal',        'a-or-b-star',                '(a + b)*')
test_regex('fp-implies-regex', 'kleene-star-star',           '(a *) * ->> (a *)')
test_regex('fp-implies-regex', 'example-in-paper',           '(a . a)* ->> (((a *) . a) + epsilon) ')
test_regex('fp-implies-regex', 'alternate-top',              '((a *) . b) * + (((b *) . a) *)')
test_regex('fp-implies-regex', 'even-or-odd',                '((((a . a) + (a . b)) + (b . a)) + (b . b)) * + ((a + b) . (((((a . a) + (a . b)) + (b . a)) + (b . b)) *))')
test_regex('fp-implies-regex', 'no-contains-a-or-no-only-b', '(~ (top . (a . top))) + ~ (b *)')

# Benchmarks:
# Unified Decision Procedures for Regular Expression Equivalence
# From: https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=f650281fc011a2c132690903eb443ff1ab3298f7
test_regex('fp-implies-regex', 'match-r-04',                  'match-r(4)')
test_regex('fp-implies-regex', 'match-r-10',                 'match-r(10)')
test_regex('fp-implies-regex', 'match-l-04',                  'match-l(4)')
test_regex('fp-implies-regex', 'match-l-10',                 'match-l(10)')
test_regex('fp-implies-regex', 'match-l-20',                 'match-l(20)')
test_regex('fp-implies-regex', 'eq-l-04',                     'eq-l(4)')
test_regex('fp-implies-regex', 'eq-l-10',                    'eq-l(10)')
test_regex('fp-implies-regex', 'eq-l-20',                    'eq-l(20)')
test_regex('fp-implies-regex', 'eq-r-04',                     'eq-r(4)')
test_regex('fp-implies-regex', 'eq-r-10',                    'eq-r(10)')
if run_slow_tests:
    test_regex('fp-implies-regex', 'match-r-20',                 'match-r(20)')
    test_regex('fp-implies-regex', 'match-r-30',                 'match-r(30)')
    test_regex('fp-implies-regex', 'match-r-40',                 'match-r(40)')
    test_regex('fp-implies-regex', 'match-l-30',                 'match-l(30)')
    test_regex('fp-implies-regex', 'match-l-40',                 'match-l(40)')
    test_regex('fp-implies-regex', 'match-l-99',                 'match-l(99)')
    test_regex('fp-implies-regex', 'eq-l-30',                    'eq-l(30)')
    test_regex('fp-implies-regex', 'eq-r-20',                    'eq-r(20)')
    test_regex('fp-implies-regex', 'eq-r-30',                    'eq-r(30)')

    test_regex('fp-implies-regex', 'eq-lr-10',                   'eq-lr(10)')
    test_regex('fp-implies-regex', 'eq-lr-20',                   'eq-lr(20)')
    test_regex('fp-implies-regex', 'eq-lr-30',                   'eq-lr(30)')
    test_regex('fp-implies-regex', 'eq-lr-30',                   'eq-lr(30)')

print_benchmarks()
print('Passed.')
