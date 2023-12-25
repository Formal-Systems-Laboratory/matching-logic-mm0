#!/usr/bin/env python3

import os, sys
from maude import reduce_in_module

def cleanup_maude_output(s: str) -> str:
    s = s.replace("'", "")
    s = s.replace("-", "_")
    s = s.replace("[[", "(")
    s = s.replace("]]", ")")
    s = s.replace("_>>", "->>")
    s = s.replace("_>", "->")
    s = s.replace("colon", ":")
    s = s.replace("no_binders", "")
    s = s.replace("bang", "!")
    s = s.replace("quote ", "'")
    s = s.replace("cong_of_equiv ", "cong_of_equiv_")
    s = s.replace("comment", "--- ")
    return s

assert len(sys.argv) == 4, "Usage: proof-gen  <mm0|mm1> <fp-implies-top> <regex>"
(mm01, theorem, regex) = sys.argv[1:]

if mm01 == 'mm0':
    print('import "../20-theory-words.mm0";')
    print(cleanup_maude_output(
          reduce_in_module('regexp-proof-gen.maude', 'PROOF-GEN', 'MM0Decl',
                                'theorem-{0}-mm0({1})'.format(theorem, regex))))
elif mm01 == 'mm1':
    print('import "../22-words-theorems.mm1";')
    print(cleanup_maude_output(
          reduce_in_module('regexp-proof-gen.maude', 'PROOF-GEN', 'MM0Decl',
                                'theorem-{0}({1})'.format(theorem, regex))))
