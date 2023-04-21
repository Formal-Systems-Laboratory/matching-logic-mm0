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

def build_str(letters, delim, part_format):
    return delim.join(map(part_format.format, letters))

def bin_tree_list(n):
    if n == 1:
        return ['id']
    return [((('orld @ '*(n-2)) + 'orld') if i == 0 else (('orld @ '*(n-i-1)) + 'orrd')) for i in range(n)]

def gen_mm1(letters, f, longest):
    n = len(letters)
    f.write('import "{}.mm0";\n'.format(filename))
    f.write('import "23-words-theorems.mm1";\n')
    for i, lname in enumerate(letters):
        if n == 1:
            proof = 'eq_to_intro_rev all_letters'
        else:
            if i == 0:
                proof = ('@ syl orl '*(n-2)) + 'orl'
            else:
                proof = ('@ syl orl '*(n-i-1)) + 'orr'
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
    
    for (lname1, lname2) in itertools.combinations(letters, 2):
        der_diff_letters = dedent('''
            theorem regex_eq_der_diff_l_{1}_wrt_{0}: $ (derivative {0} {1}) <-> bot $ =
              '(regex_eq_der_diff_l functional_{0} functional_{1} {0}_in_top_letter {1}_in_top_letter no_confusion_{0}_{1});'''.format(lname1, lname2))
        f.write(der_diff_letters)
    f.write('\n')

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
          '''.format(build_str(letters, ' \/ ', '({0} . (derivative {0} phi))'),
                     ' \/ '.join(letters),
                     build_str(letters, ' ', '\'[{0} functional_{0}]'),
                     functools.reduce('(bitr (cong_of_equiv_exists andir) @ bitr or_exists_bi @ oreqi {0} {1})'.format,
                                      map("(mp ,(func_to_and_ctx_bi 'x $eVar x . derivative (eVar x) phi$) functional_{})".format,
                                          letters))))
    f.write(der_equality_bi_concrete)

    positive_in_fp_interior = dedent('''
        theorem positive_in_fp_interior {{X: SVar}} ({0}: Pattern X)
          {1}:
          $ _Positive X (epsilon \/ ({2})) $
          = '(positive_in_or positive_disjoint {3});
        '''.format(build_str(letters, ' ', 'phi_{0}'),
                   build_str(letters, '\n          ', '(pos_{0}: $ _Positive X phi_{0} $)'),
                   build_str(letters, ' \/ ', '{0} . phi_{0}'),
                   functools.reduce('(positive_in_or {0} {1})'.format, map('(positive_in_concat positive_disjoint pos_{0})'.format, letters)),
                   ))
    f.write(positive_in_fp_interior)

    fp_implies_regex_interior = dedent('''
        theorem fp_implies_regex_interior {{X: SVar}} ({0} rho: Pattern X)
          {1}
          (he: $ epsilon -> rho $)
          {2}:
          ----------------------------------------------
          $(mu X (epsilon \/ ({3}))) -> rho$ =
          '(KT (positive_in_fp_interior {4}) @
            apply_equiv der_equality_bi_concrete (norm
              (norm_imp_l @ norm_sym @ _sSubst_or sSubstitution_disjoint {5})
              (orim (iand id he) {6})
            ));
        '''.format(build_str(letters, ' ', 'phi_{0}'),
                   build_str(letters, '\n          ', '(pos_{0}: $ _Positive X phi_{0} $)'),
                   build_str(letters, '\n          ', '(h_{0}: $ s[ rho / X ] phi_{0} -> (derivative {0} rho) $)'),
                   build_str(letters, ' \/ ', '({0} . phi_{0})'),
                   build_str(letters, ' ', 'pos_{0}'),
                   functools.reduce('(_sSubst_or {0} {1})'.format, ['(sSubst_concat_r norm_refl)']*n),
                   functools.reduce('(orim {0} {1})'.format, map('(framing_concat_r h_{0})'.format, letters)),
                   ))
    f.write(fp_implies_regex_interior)

    top_implies_fp_interior = dedent('''
        theorem top_implies_fp_interior {{X box: SVar}} ({0} {1}: Pattern X box)
          {2}
          {3}
        
          {4}
          {5}
          : ------------------------
          $(mu X (epsilon \/ ({6}))) . top_letter -> (mu X (epsilon \/ ({7})))$
          = '(unwrap_subst appctx_concat_l
            @ KT_subst (positive_in_fp_interior {8}) ,(propag_s_subst_adv 'X $epsilon \/ ({9})$ (atom-map! {10}))
            @ eori
              ( wrap_subst appctx_concat_l
                @ rsyl (anl regex_eq_eps_concat_l)
                @ unfold_r (positive_in_fp_interior {11})
                @ norm (norm_sym @ norm_imp_r ,(propag_s_subst_adv 'X $epsilon \/ ({9})$ (atom-map! {10})))
                @ orrd
                @ rsyl (eq_to_intro all_letters)
                {12})
            {13}
            );
        '''.format(build_str(letters, ' ', 'fp_unf_{0}'),
                   build_str(letters, ' ', 'fp_ctximp_{0}'),
                   build_str(letters, '\n          ', '(p_fp_unf_{0}: $ _Positive X fp_unf_{0} $)'),
                   build_str(letters, '\n          ', '(p_fp_ctximp_{0}: $ _Positive X fp_ctximp_{0} $)'),
                   build_str(letters, '\n          ', '(he_{{0}}: $ epsilon -> s[ (mu X (epsilon \/ ({0}))) / X ] fp_unf_{{0}} $)'
                             .format(build_str(letters, ' \/ ', '{0} . fp_unf_{0}'))),
                   build_str(letters, '\n          ', '(h{{0}}: $ ((s[ (ctximp_app box (sVar box . top_letter) (mu X (epsilon \/ ({0})))) / X ] fp_ctximp_{{0}}) . top_letter)\n            -> (s[ (mu X (epsilon \/ ({0}))) / X ] fp_unf_{{0}}) $)'
                             .format(build_str(letters, ' \/ ', '{0} . fp_unf_{0}'))),
                   build_str(letters, ' \/ ', '{0} . fp_ctximp_{0}'),
                   build_str(letters, ' \/ ', '{0} . fp_unf_{0}'),
                   build_str(letters, ' ', 'p_fp_ctximp_{0}'),
                   build_str(letters, ' \/ ', '{0} . _'),
                   build_str(letters, ' ', '\'[{0} #t]'),
                   build_str(letters, ' ', 'p_fp_unf_{0}'),
                   functools.reduce('(orim {0} {1})'.format, map('(rsyl (anr regex_eq_eps_concat_r) @ framing_concat_r he_{0})'.format, letters)),
                   functools.reduce('(eori {0} {1})'.format, map('''
                     ( wrap_subst appctx_concat_l
                       @ rsyl (bi1i @ assoc_concat)
                       @ unfold_r (positive_in_fp_interior {0})
                       @ norm (norm_sym @ norm_imp_r ,(propag_s_subst_adv 'X $epsilon \/ ({1})$ (atom-map! {2})))
                       @ orrd
                       @ {{1}}
                       @ framing_concat_r h{{0}})'''.format(build_str(letters, ' ', 'p_fp_unf_{0}'),
                                                            build_str(letters, ' \/ ', '{0} . _'),
                                                            build_str(letters, ' ', '\'[{0} #t]'),
                                                            ).format, letters, bin_tree_list(n))),
                   ))
    f.write(top_implies_fp_interior)



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
