#!/usr/bin/env python3

import tempfile, shutil, os, sys, subprocess, re

def reduce_in_module(src, module, expected_sort, term):
    output = subprocess.check_output(
        ['maude', '-no-banner', '-no-wrap', '-batch', src],
        input='reduce in {0} : {1} . \n'.format(module, term),
        text=True
    )
    output = output.split('\n')

    # Sanity check
    assert(output[0] == 'Maude> ==========================================')
    assert(output[1].startswith('reduce in {0}'.format(module)))
    assert(output[2].startswith('rewrites: '))
    assert(output[-2:] == ['Maude> Bye.', ''])
    output = output[3:-2]

    result_string = 'result {0}: '.format(expected_sort)
    assert(output[0].startswith(result_string)), output[0]

    output[0] = output[0][len(result_string):]
    return '\n'.join(output)

def cleanup_maude_output(s):
    s = s.replace("'", "")
    s = s.replace("-", "_")
    s = s.replace("[", "(")
    s = s.replace("]", ")")
    s = s.replace("_>>", "->>")
    s = s.replace("_>", "->")
    s = s.replace("colon", ":")
    s = s.replace("no_binders", "")
    s = s.replace("({", "{")
    s = s.replace("})", "}")
    s = s.replace("bang", "!")
    s = s.replace("quote ", "'")
    s = s.replace("cong_of_equiv ", "cong_of_equiv_")
    return s

assert len(sys.argv) == 4, "Usage: proof-gen <mm0|mm1> <main-goal|top-implies-fp|fp-implies-top> <regex>"
(mm01, theorem, regex) = sys.argv[1:]

if mm01 == 'mm0':
    print('import "../22-assumptions.mm0";')
    print(cleanup_maude_output(
          reduce_in_module('regexp-proof-gen.maude', 'PROOF-GEN', 'MM0Decl',
                                'theorem-{0}-mm0({1})'.format(theorem, regex))))
elif mm01 == 'mm1':
    print('import "../24-words-derivatives.mm1";')
    print(cleanup_maude_output(
          reduce_in_module('regexp-proof-gen.maude', 'PROOF-GEN', 'MM0Decl',
                                'theorem-{0}({1})'.format(theorem, regex))))
