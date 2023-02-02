import tempfile, shutil, os, sys, subprocess, re, argparse

maude_src = "regexp-proof-gen/regexp.maude"
tmp_maude_file = "regex.maude"
maude_cmd = "maude -no-wrap {} </dev/null"
maude_appendix = """

reduce in PATTERN-METAMATH-TRANSLATE : {0} .
reduce in PROOF-GEN : fp(proofHint({0})) .
reduce in PROOF-GEN : proof-main-goal(proofHint({0})) .
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
    s = s.replace("cong_of_equiv '", "cong_of_equiv_")
    s = s.replace("'regex_", "regex_")
    s = s.replace("Var '", "Var ")
    s = s.replace("mu '", "mu ")
    return re.sub(r"\(apply_subst ([^$]*)\$([^$]*)\$", r"(norm_lemma ,(propag_s_subst \g<1>$\g<2>$)", s)

var_counter = 0
generated_vars = ""
def newVar(_):
    global var_counter
    global generated_vars
    var_counter = var_counter + 1
    var = "X" + str(var_counter)
    generated_vars = generated_vars + var + " "
    return var

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
args = parser.parse_args()

regex = args.regex

with tempfile.TemporaryDirectory() as tmp_dir:
    maude_file_name = os.path.join(tmp_dir, tmp_maude_file)
    shutil.copyfile(maude_src, maude_file_name)
    with open(maude_file_name, "a") as maude_file:
        maude_file.write(maude_appendix.format(regex))
    maude_result = subprocess.run(maude_cmd.format(maude_file_name), shell=True, stdout=subprocess.PIPE)
    maude_output = maude_result.stdout.decode()
    # print(maude_output)
    maude_output = maude_output.split("\n==========================================")
    mm_regex = maude_output[1].split("result Pattern: ",1)[1].replace("kleene ", "kleene _ ")
    # print(mm_regex)
    mm_fp = process_mm(maude_output[2].split("result Pattern: ",1)[1])
    # print(mm_fp)
    mm_proof = process_mm(maude_output[3].split("result MetaMathProof: ",1)[1].split("\nMaude> Bye.",1)[0])
    # print(mm_proof)

    raw_svars = re.findall(r"(?:sVar|mu) ([^ )]*)", mm_fp)
    svars = " ".join(set(raw_svars)) + " "

    mm_regex = re.sub("_", newVar, mm_regex)
    svars = svars + generated_vars
    if svars.strip():
        svars = " {" + svars + ": SVar} "

    mm_theorem = mm_theorem_base.format(svars, mm_fp, mm_regex, mm_proof)
    # print(mm_theorem)
    mm0_theorem = mm0_theorem_base.format(svars, mm_fp, mm_regex)
    # print(mm0_theorem)

    ### Generate MMB file ###
    mm_file_name = os.path.join(tmp_dir, tmp_mm_file)
    subprocess.run(mm_join_cmd.format(mm_yellow, mm_file_name), shell=True)
    with open(mm_file_name, "a") as mm_file:
        mm_file.write(mm_theorem)
    # For debugging only:
    # shutil.copyfile(mm_file_name, "re.mm1")
    subprocess.run(mm_compile_cmd.format(mm_file_name, args.mmb_dest), shell=True)

    ### Generate MM0 file ###
    mm0_file_name = os.path.join(tmp_dir, tmp_mm0_file)
    shutil.copyfile(mm0_combined, mm0_file_name)
    with open(mm0_file_name, "a") as mm0_file:
        mm0_file.write(mm0_theorem)
    shutil.copyfile(mm0_file_name, args.mm0_dest)

    