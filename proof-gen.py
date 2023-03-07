#!/usr/bin/env python3

import tempfile, shutil, os, sys, subprocess, re

maude_src = "regexp-proof-gen.maude"
maude_cmd = "maude -no-banner -no-wrap -interactive {}"
maude_appendix = """
reduce in PROOF-GEN : theorem-{0}({1}) .
q .
"""

def process_mm(s):
    s = s.replace("'", "")
    s = s.replace("-", "_")
    s = s.replace(";)", ";")
    s = s.replace("(pub", "pub")
    s = s.replace("_>>", "->>")
    s = s.replace("_>", "->")
    s = s.replace("colon", ":")
    s = s.replace("no-binders", "")
    s = s.replace("bang", "!")
    s = s.replace("quote ", "'")
    s = s.replace("cong_of_equiv ", "cong_of_equiv_")
    return s

assert len(sys.argv) == 3, "Usage: proof-gen <fp-implies-top> <regex>"
theorem = sys.argv[1]
regex = sys.argv[2]

with subprocess.Popen(maude_cmd.format(maude_src), shell=True,
                      stdin=subprocess.PIPE,
                      stdout=subprocess.PIPE,
                     ) as maude_proc:
    (maude_output, _) = maude_proc.communicate(bytes(maude_appendix.format(theorem, regex), 'utf-8'))
    all_outputs = re.findall(r"result \[?(?:Pattern|MetaMathProof|MM0Decl)\]?: ([^\n]*)\n", process_mm(str(maude_output, 'utf8')))

print('import "../24-words-derivatives.mm1";')
print(all_outputs[0])
