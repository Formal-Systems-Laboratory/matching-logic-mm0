#!/usr/bin/env python3
from os import path, makedirs
from subprocess import check_call, check_output
from glob import glob

test_dir=".build"

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

def test_mm(mm0_file: str, mm1_file: str) -> None:
    test_name = path.basename(mm1_file)
    output_basename = path.join(test_dir, test_name)
    _, extension = path.splitext(mm1_file)
    output_joined = path.join(test_dir, test_name + '.joined.' + extension)
    output_mmb    = path.join(test_dir, test_name + '.mmb')

    print("Testing: %s" % test_name)
    # There seems to be a bug in mm0-rs that causes the program to crash
    # when compiling un-joined files.
    join(mm1_file, output_joined)
    compile(output_joined, output_mmb)
    check(output_mmb, mm0_file)


def test_regex(theorem: str, test_name: str, regex: str) -> None:
    output_mm0_file = path.join(test_dir, test_name + '.mm0')
    output_joined_mm0_file = path.join(test_dir, test_name + '.joined.mm0')
    output_mm1_file = path.join(test_dir, test_name + '.mm1')
    output_joined_mm1_file = path.join(test_dir, test_name + '.joined.mm1')

    run_proof_gen('mm0', theorem, regex, output_mm0_file)
    join(output_mm0_file, output_joined_mm0_file)
    run_proof_gen('mm1', theorem, regex, output_mm1_file)
    test_mm(output_joined_mm0_file, output_mm1_file)


### Main #######################

makedirs(test_dir, exist_ok=True)
last_mm0_file = None
for f in sorted((glob('*.mm0') + glob('*.mm1'))):
    if path.splitext(f)[1] == '.mm0':
        last_mm0_file = path.join(test_dir, 'joined.' + f)
        join(f, last_mm0_file)
    assert last_mm0_file
    test_mm(last_mm0_file, f)

test_regex('main-goal',            'a-or-b-star',                '(a + b)*')
test_regex('fp-implies-regex-pub', 'kleene-star-star',           '(a *) * ->> (a *)')
test_regex('fp-implies-regex-pub', 'example-in-paper',           '(a . a)* ->> (((a *) . a) + epsilon) ')
test_regex('fp-implies-regex-pub', 'alternate-top',              '((a *) . b) * + (((b *) . a) *)')
test_regex('fp-implies-regex-pub', 'even-or-odd',                '((((a . a) + (a . b)) + (b . a)) + (b . b)) * + ((a + b) . (((((a . a) + (a . b)) + (b . a)) + (b . b)) *))')
test_regex('fp-implies-regex-pub', 'no-contains-a-or-no-only-b', '(~ (top . (a . top))) + ~ (b *)')
print('Passed.')
