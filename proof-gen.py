#!/usr/bin/env python3

import tempfile, shutil, os, sys, subprocess, re, argparse

maude_src = "regexp-proof-gen.maude"
maude_cmd = "maude -no-banner -no-wrap -interactive {}"
maude_appendix = """
reduce in PATTERN-METAMATH-TRANSLATE : {0} .
reduce in PROOF-GEN : fp(proofHint({0})) .
reduce in PROOF-GEN : proof-top-implies-fp(proofHint({0})) .
reduce in PROOF-GEN : proof-main-goal(proofHint({0})) .
q .
"""

def process_mm(s):
    s = s.replace("'top-implies-fp-leaf", "top_implies_fp_leaf")
    s = s.replace("'orl", "orl")
    s = s.replace("-", "_")
    s = s.replace("_>>", "->>")
    s = s.replace("cong_of_equiv '", "cong_of_equiv_")
    s = s.replace("'regex_", "regex_")
    s = s.replace("Var '", "Var ")
    s = s.replace("mu '", "mu ")
    s = s.replace("'sSubst", "sSubst")
    s = s.replace("'_", "_")
    s = s.replace("bang", "!")
    s = s.replace("'X", "X")
    s = s.replace("'box", "box")
    return s

parser = argparse.ArgumentParser()
parser.add_argument('regex', help="the regular expression to be checked for validity")
args = parser.parse_args()
regex = args.regex

with tempfile.TemporaryDirectory() as tmp_dir:
    with subprocess.Popen(maude_cmd.format(maude_src), shell=True,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                         ) as maude_proc:
        (maude_output, _) = maude_proc.communicate(bytes(maude_appendix.format(regex), 'utf-8'))
        all_outputs = re.findall(r"result \[?(?:Pattern|MetaMathProof)\]?: ([^\n]*)\n", process_mm(str(maude_output, 'utf8')))

    # print(all_outputs)
    mm_regex = all_outputs[0]
    mm_fp = all_outputs[1]
    mm_top_implies_fp = all_outputs[2]
    mm_fp_implies_regex = all_outputs[3]

    svars_in_top_implies_fp = re.findall(r"(?:sVar|mu) ([^ )]*)", mm_fp)
    svars_in_top_implies_fp = " ".join(set(svars_in_top_implies_fp)).strip()

    svars_in_fp_to_regex = svars_in_top_implies_fp
    if " Xk " in mm_regex:
        svars_in_fp_to_regex = svars_in_fp_to_regex + " Xk"

    if svars_in_top_implies_fp:
        svars_in_top_implies_fp = " {{{}: SVar}} ".format(svars_in_top_implies_fp)
    if svars_in_fp_to_regex:
        svars_in_fp_to_regex = " {{{}: SVar}} ".format(svars_in_fp_to_regex)

    print('import "../24-words-derivatives.mm1";')
    print("pub theorem fp_to_regex{}: ${} -> {}$ = \n  '{};".format(svars_in_fp_to_regex, mm_fp, mm_regex, mm_fp_implies_regex))
    print("pub theorem top_implies_fp {}: $top_word X -> {}$ = \n  '{};".format(svars_in_top_implies_fp, mm_fp, mm_top_implies_fp))

