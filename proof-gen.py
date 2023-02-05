#!/usr/bin/env python3

import tempfile, shutil, os, sys, subprocess, re, argparse

maude_src = "regexp-proof-gen/regexp.maude"
maude_cmd = "maude -no-banner -no-wrap -interactive {}"
maude_appendix = """
reduce in PATTERN-METAMATH-TRANSLATE : {0} .
reduce in PROOF-GEN : fp(proofHint({0})) .
reduce in PROOF-GEN : proof-main-goal(proofHint({0})) .
q .
"""

def process_mm(s):
    s = s.replace("-", "_")
    s = s.replace("_>>", "->>")
    s = s.replace("cong_of_equiv '", "cong_of_equiv_")
    s = s.replace("'regex_", "regex_")
    s = s.replace("Var '", "Var ")
    s = s.replace("mu '", "mu ")
    s = s.replace("(propag_s_subst", ",(propag_s_subst ")
    s = s.replace("'_", "_")
    return s

parser = argparse.ArgumentParser()
parser.add_argument('regex', help="the regular expression to be checked for validity")
args = parser.parse_args()
regex = args.regex

with tempfile.TemporaryDirectory() as tmp_dir:
    with subprocess.Popen(maude_cmd.format(maude_src), shell=True,
                          stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE) as maude_proc:
        (maude_output, _) = maude_proc.communicate(bytes(maude_appendix.format(regex), 'utf-8'))
        all_outputs = re.findall(r"result \[?(?:Pattern|MetaMathProof)\]?: ([^\n]*)\n", process_mm(str(maude_output, 'utf8')))

    # print(all_outputs)
    mm_regex = all_outputs[0]
    mm_fp = all_outputs[1]
    mm_fp_implies_regex = all_outputs[2]

    raw_svars = re.findall(r"(?:sVar|mu) ([^ )]*)", mm_fp)
    svars = " ".join(set(raw_svars))

    if " Xk " in mm_regex:
        svars = svars + " Xk"
    if svars.strip():
        svars = " {{{}: SVar}} ".format(svars)

    print('import "../24-words-derivatives.mm1";')
    print("pub theorem fp_to_regex{}: ${} -> {}$ = \n  '{};".format(svars, mm_fp, mm_regex, mm_fp_implies_regex))

