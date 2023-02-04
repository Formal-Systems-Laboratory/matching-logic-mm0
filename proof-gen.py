#!/usr/bin/env python3

import tempfile, shutil, os, sys, subprocess, re, argparse

maude_src = "regexp-proof-gen/regexp.maude"
tmp_maude_file = "regex.maude"
maude_cmd = "maude -no-banner -no-wrap -interactive {}"
maude_appendix = """
reduce in PATTERN-METAMATH-TRANSLATE : {0} .
reduce in PROOF-GEN : fp(proofHint({0})) .
reduce in PROOF-GEN : proof-main-goal(proofHint({0})) .
q .
"""

mm_theorem_base = "\n\n\npub theorem fp_to_regex{}: ${} -> {}$ = \n  '{};\n"
mm0_theorem_base = "\n\n\ntheorem fp_to_regex{}: ${} -> {}$;\n"
mm_yellow = "yellow.mm1"
mm0_combined = "combined.mm0"
tmp_mm0_file = "regex.mm0"
mm_join_cmd = "mm0-rs join {} {}"
mm_compile_cmd = "mm0-rs compile {} {}"
tmp_mm_file = "regex.mm1"

def process_mm(s):
    s = s.replace("-", "_")
    s = s.replace("_>>", "->>")
    s = s.replace("cong_of_equiv '", "cong_of_equiv_")
    s = s.replace("'regex_", "regex_")
    s = s.replace("Var '", "Var ")
    s = s.replace("mu '", "mu ")
    s = re.sub(r"\(apply_subst ([^$]*)\$([^$]*)\$", r"(norm_lemma ,(propag_s_subst \g<1>$\g<2>$)", s)
    return s

parser = argparse.ArgumentParser()
parser.add_argument('regex', help="the regular expression to be checked for validity")
parser.add_argument('--mmb', dest='mmb_dest', action='store',
                    default="/dev/null",
                    help='file path for storing the generated mmb proof object',
                    required = False)
parser.add_argument('--mm0', dest='mm0_dest', action='store',
                    default="/dev/null",
                    help='file path for storing the generated mm0 spec file',
                    required = False)
parser.add_argument('--mm1', dest='mm1_dest', action='store',
                    default="/dev/null",
                    help='file path for storing the generated mm1 source',
                    required = False)
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
    mm_proof = all_outputs[2]

    raw_svars = re.findall(r"(?:sVar|mu) ([^ )]*)", mm_fp)
    svars = " ".join(set(raw_svars))

    if " Xk " in mm_regex:
        svars = svars + " Xk"
    if svars.strip():
        svars = " {{{}: SVar}} ".format(svars)

    mm_theorem = mm_theorem_base.format(svars, mm_fp, mm_regex, mm_proof)
    # print(mm_theorem)
    mm0_theorem = mm0_theorem_base.format(svars, mm_fp, mm_regex)
    # print(mm0_theorem)

    ### Generate MMB file ###
    mm_file_name = os.path.join(tmp_dir, tmp_mm_file)
    subprocess.run(mm_join_cmd.format(mm_yellow, mm_file_name), shell=True, check=True)
    with open(mm_file_name, "a") as mm_file:
        mm_file.write(mm_theorem)
    shutil.copyfile(mm_file_name, args.mm1_dest)
    subprocess.run(mm_compile_cmd.format(mm_file_name, args.mmb_dest), shell=True, check=True)

    ### Generate MM0 file ###
    mm0_file_name = os.path.join(tmp_dir, tmp_mm0_file)
    shutil.copyfile(mm0_combined, mm0_file_name)
    with open(mm0_file_name, "a") as mm0_file:
        mm0_file.write(mm0_theorem)
    shutil.copyfile(mm0_file_name, args.mm0_dest)
