#!/usr/bin/env python3

import os, string, itertools, functools, sys
from textwrap import dedent

def gen_mm0(letters, f, longest):
    f.write('import "20-theory-words.mm0";\n')
    for lname in letters:
        space = ' '*(longest-len(lname))
        symbol_def = dedent('''
            term {0}_symbol{1}: Symbol;
            def {0}{1}: Pattern = $ sym {0}_symbol {1}$;'''.format(lname, space))
        f.write(symbol_def)
    f.write('\n')
    for lname in letters:
        space = ' '*(longest-len(lname))
        functional_let = dedent('''
            axiom functional_{0} {1}: $ is_func {0}{1} $;'''.format(lname, space))
        f.write(functional_let)
    f.write('\n')
    for (lname1, lname2) in itertools.combinations(letters, 2):
        space1 = ' '*(longest-len(lname1))
        space2 = ' '*(longest-len(lname2))
        no_confusion = dedent('''
            axiom no_confusion_{0}_{1}{2}{3}: $ {0} {2}!= {1} {3}$;'''.format(lname1, lname2, space1, space2))
        f.write(no_confusion)
    f.write('\n')
    top_letter = 'axiom all_letters: $ top_letter == {} $;'.format(' \/ '.join(letters))
    f.write('\n{}\n'.format(top_letter))

def gen_thms(letters, f, longest, str_base):
    for lname in letters:
        thm = dedent(str_base.format(lname))
        f.write(thm)
    f.write('\n')

def gen_mm1(letters, f, longest):
    n = len(letters)
    f.write('import "{}.mm0";\n'.format(filename))
    f.write('import "23-words-theorems.mm1";\n')
    for i, lname in enumerate(letters):
        if n == 1:
            proof = 'eq_to_intro_rev all_letters'
        else:
            if i == 0:
                proof = '{}orl'.format('@ syl orl '*(n-2))
            else:
                proof = '{}orr'.format('@ syl orl '*(n-i-1))
            proof = 'syl (eq_to_intro_rev all_letters) {}'.format(proof)
        in_top_letter = dedent('''
            theorem {0}_in_top_letter: $ {0} -> top_letter $ =
              \'({1});'''.format(lname, proof))
        f.write(in_top_letter)
    f.write('\n')
    gen_thms(letters, f, longest, '''
        theorem functional_{0}_concat {{x v: EVar}}: $ exists x (eVar x == {0} . eVar v) $ =
          '(functional_l_concat functional_{0});''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_ewp_{0}: $ epsilon /\ {0} <-> bot $ =
          '(regex_eq_ewp_l {0}_in_top_letter);''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_ewp_not_{0}: $ (epsilon /\ ~{0}) <-> epsilon $ =
          '(ibii anl @ iand id @ dne @ anl regex_eq_ewp_{0});''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_der_bot_wrt_{0}: $ (derivative {0} bot) <-> bot $ =
          '(ibii (regex_eq_der_bot functional_{0}) absurdum);''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_der_epsilon_wrt_{0}: $ (derivative {0} epsilon) <-> bot $ =
          '(regex_eq_der_epsilon functional_{0} {0}_in_top_letter);''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_der_choice_wrt_{0}: $ (derivative {0} (Alpha \/ Beta)) <-> (derivative {0} Alpha) \/ (derivative {0} Beta) $ =
          '(regex_eq_der_choice functional_{0});''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_der_conj_wrt_{0}: $ (derivative {0} (Alpha /\ Beta)) <-> (derivative {0} Alpha) /\ (derivative {0} Beta) $ =
          '(regex_eq_der_conj functional_{0});''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_der_neg_wrt_{0}: $ (derivative {0} (~ Alpha)) <-> ~ (derivative {0} Alpha) $ =
          '(regex_eq_der_neg functional_{0});''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_der_same_l_wrt_{0}: $ (derivative {0} {0}) <-> epsilon $ =
          '(regex_eq_der_same_l functional_{0} {0}_in_top_letter);''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_der_concat_wrt_{0}: $ (derivative {0} (Alpha . Beta)) <-> ((derivative {0} Alpha) . Beta) \/ ((epsilon /\ Alpha) . (derivative {0} Beta)) $ =
          '(regex_eq_der_concat functional_{0} {0}_in_top_letter);''')
    gen_thms(letters, f, longest, '''
        theorem regex_eq_der_kleene_wrt_{0} (X_fresh: $ _sFresh X Alpha $): $ (derivative {0} (kleene X Alpha)) <-> ((derivative {0} Alpha) . (kleene X Alpha)) $ =
          '(regex_eq_der_kleene X_fresh functional_{0} {0}_in_top_letter);''')

    der_equality_bi_concrete = dedent('''
        theorem der_equality_bi_concrete: $phi <-> (epsilon /\ phi) \/ ({0})$ =
          (named
          \'(bitr der_equality_bi
          @ oreq2i
          @ bitr ( cong_of_equiv_exists
                  @ bitr (aneq2i (bitr (cong_of_equiv_mem @ eq_to_intro_bi all_letters)
                                      ,(propag_mem_w_fun \'x ${1}$ (atom-map! {2}))))
                  ancomb)
          {3}
          ));
          '''.format(' \/ '.join(map('({0} . (derivative {0} phi))'.format, letters)),
                     ' \/ '.join(letters),
                     ' '.join(map('\'[{0} functional_{0}]'.format, letters)),
                     functools.reduce('(bitr (cong_of_equiv_exists andir) @ bitr or_exists_bi @ oreqi {0} {1})'.format,
                                      map("(mp ,(func_to_and_ctx_bi 'x $eVar x . derivative (eVar x) phi$) functional_{})".format,
                                          letters))))
    f.write(der_equality_bi_concrete)

assert len(sys.argv) >= 3, "Usage: words-theory-gen <filename> <letter>*"
filename = sys.argv[1]
letters = sys.argv[2:]

assert len(set(letters)) == len(letters), "List of letters may not contain duplicates"

ascii = set(string.ascii_uppercase + string.ascii_lowercase)
assert all(ascii.issuperset(lname) for lname in letters), "Letter names may only be of the form 'a-Z'*"

longest = max(map(len, letters))

f = open("{}.mm0".format(filename), "w")
gen_mm0(letters, f, longest)
f.close()

f = open("{}.mm1".format(filename), "w")
gen_mm1(letters, f, longest)
f.close()
