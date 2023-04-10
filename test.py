#!/usr/bin/env python3

import pytest
from glob import glob
from os import path, makedirs
from typing import no_type_check
from subprocess import check_call, check_output
from sys import argv

import maude
from benchmarks import benchmark, record_mm1_stats, record_mmb_stats

test_dir=".build"


### PyTest Helpers #####################

def regex_to_id(exp: str) -> str:
    return exp.replace(' ', '') \
              .replace('*', 'x') \
              .replace('(', 'C') \
              .replace(')', 'D') \
              .replace('/\\', '@') \
              .replace('\\/', '+') \

@no_type_check
def slow(*args):
    return pytest.param(*args, marks=pytest.mark.slow)

### MM0 Helpers #######################

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


### Tests: Maude #######################

def test_maude_version() -> None:
    maude.check_maude_version()

def test_maude_unit_tests() -> None:
    assert maude.reduce_in_module('test.maude', 'TEST', 'TestResult', 'unit-tests') == 'passed'


### Test: proof check base MM0/1 files ##########################

makedirs(test_dir, exist_ok=True)
last_mm0_file = None
base_mm_tests = []
for f in sorted((glob('*.mm0') + glob('*.mm1'))):
    if path.splitext(f)[1] == '.mm0':
        last_mm0_file = path.join(test_dir, 'joined.' + f)
        join(f, last_mm0_file)
    assert last_mm0_file
    base_mm_tests += [(last_mm0_file, f)]

@pytest.mark.parametrize('mm0_file,mm1_file', base_mm_tests)
def test_mm(mm0_file: str, mm1_file: str) -> None:
    basename = path.basename(mm1_file)
    test_name, extension = path.splitext(basename)
    output_basename = path.join(test_dir, test_name)
    output_joined = path.join(test_dir, test_name + '.joined' + extension)
    output_mmb    = path.join(test_dir, test_name + '.mmb')

    with benchmark(test_name, 'join'):      join(mm1_file, output_joined)
    record_mm1_stats(test_name, output_joined)
    with benchmark(test_name, 'compile'):   compile(output_joined, output_mmb)
    record_mmb_stats(test_name, output_mmb)
    with benchmark(test_name, 'check'):     check(output_mmb, mm0_file)


### Test: proof generated certificates ##########################

@pytest.mark.parametrize('theorem,test_name,regex',
[   ('main-goal',            'a-or-b-star',                '(a + b)*'),
    ('main-goal',            'kleene-star-star',           '(a *) * ->> (a *)'),
    ('main-goal',            'example-in-paper',           '(a . a)* ->> (((a *) . a) + epsilon) '),
    ('main-goal',            'alternate-top',              '((a *) . b) * + (((b *) . a) *)'),
    ('main-goal',            'even-or-odd',                '((((a . a) + (a . b)) + (b . a)) + (b . b)) * + ((a + b) . (((((a . a) + (a . b)) + (b . a)) + (b . b)) *))'),
    ('main-goal',            'no-contains-a-or-no-only-b', '(~ (top . (a . top))) + ~ (b *)'),
])
def test_regex(theorem: str, test_name: str, regex: str) -> None:
    output_mm0_file = path.join(test_dir, test_name + '.mm0')
    output_joined_mm0_file = path.join(test_dir, test_name + '.joined.mm0')
    output_mm1_file = path.join(test_dir, test_name + '.mm1')
    output_joined_mm1_file = path.join(test_dir, test_name + '.joined.mm1')

    with benchmark(test_name, 'gen_mm0'):  run_proof_gen('mm0', theorem, regex, output_mm0_file)
    with benchmark(test_name, 'join_mm0'): join(output_mm0_file, output_joined_mm0_file)
    with benchmark(test_name, 'gen_mm1'): run_proof_gen('mm1', theorem, regex, output_mm1_file)
    test_mm(output_joined_mm0_file, output_mm1_file)

# Benchmarks from Unified Decision Procedures for Regular Expression Equivalence
# https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=f650281fc011a2c132690903eb443ff1ab3298f7

@pytest.mark.parametrize('n', [1, 2, 4, 5, 6, 7, slow(8)])
def test_regex_match_l(n: int) -> None:
    test_regex('main-goal', 'match-l-{:03d}'.format(n), 'match-l({})'.format(n))

@pytest.mark.parametrize('n', [1, 2, 4, 5, 6, 7, slow(8)])
def test_regex_match_r(n: int) -> None:
    test_regex('main-goal', 'match-r-{:03d}'.format(n), 'match-r({})'.format(n))

@pytest.mark.parametrize('n', [1, 2, 4, 5, 6, 7, slow(8)])
def test_regex_eq_l(n: int) -> None:
    test_regex('main-goal', 'eq-l-{:03d}'.format(n), 'eq-l({})'.format(n))

@pytest.mark.parametrize('n', [1, 2, 4, 5, 6, 7, slow(8)])
def test_regex_eq_r(n: int) -> None:
    test_regex('main-goal', 'eq-r-{:03d}'.format(n), 'eq-r({})'.format(n))

@pytest.mark.parametrize('n', [1, 2, 4, 5, slow(6), slow(7), slow(8)])
def test_regex_eq_lr(n: int) -> None:
    test_regex('main-goal', 'eq-lr-{:03d}'.format(n), 'eq-lr({})'.format(n))

@pytest.mark.parametrize('exp', [
    'a',
    '(a . a) . (a . a)',
    '(a + b)',
    '(( (b . b) * ) . ( b * ))',
    '( a  /\\ ( a /\\ b ) )',
    '(bot . bot)*',
])
def test_regex_implies_self(exp: str) -> None:
    id = regex_to_id(exp)
    test_regex('main-goal',  'implies-self-{}'.format(id), '{} ->> {}'.format(exp, exp))


### Randomized tests using hypothesis

from typing import Callable
import hypothesis
from hypothesis import given, settings
from hypothesis.strategies import composite, just, recursive, SearchStrategy, DrawFn

def regex() -> SearchStrategy[str]:

    def epsilon() -> SearchStrategy[str]:
        return just('epsilon')

    def bot() -> SearchStrategy[str]:
        return just('bot')

    def letters() -> SearchStrategy[str]:
        return just('a') | just('b')

    @composite
    def neg(draw: DrawFn, arg: SearchStrategy[str]) -> str:
        return '( ~ ' + draw(arg) + ')'

    @composite
    def kleene(draw: DrawFn, arg: SearchStrategy[str]) -> str:
        return '( ' + draw(arg) + ' * )'

    @composite
    def concat(draw: DrawFn, arg: SearchStrategy[str]) -> str:
        return '(' + draw(arg) + ' . ' + draw(arg) + ')'

    @composite
    def plus(draw: DrawFn, arg: SearchStrategy[str]) -> str:
        return '( ' + draw(arg) + ' + ' + draw(arg) + ' )'

    return recursive(bot() | epsilon() | letters(),
                     lambda sub: concat(sub) | kleene(sub) | plus(sub))

# @given(regex())
# @settings(deadline=20*1000, verbosity=hypothesis.Verbosity.verbose, max_examples=10)
# @pytest.mark.slow
# def test_equiv(exp):
#     test_regex_implies_self(exp)
