#!/usr/bin/env python3

import os, string, itertools, sys
from textwrap import dedent

def gen_mm0(letters, f, longest):
    f.write('import "20-theory-words.mm0";\n')
    for lname in letters:
        space = longest-len(lname)
        symbol_def = dedent('''
            term {0}_symbol{1}: Symbol;
            def {0}{1}: Pattern = $ sym {0}_symbol {1}$;'''.format(lname, ' '*space))
        f.write(symbol_def)
    f.write('\n')
    for lname in letters:
        space = longest-len(lname)
        functional_let = dedent('''
            axiom functional_{0} {1}{{x: EVar}}: $ exists x (eVar x == {0}{1}) $;'''.format(lname, ' '*space))
        f.write(functional_let)
    f.write('\n')
    for (lname1, lname2) in itertools.combinations(letters, 2):
        space1 = longest-len(lname1)
        space2 = longest-len(lname2)
        space12 = space1 + space2
        no_confusion = dedent('''
            axiom no_confusion_{0}_{1}{2}: $ {0} {3}!= {1} {4}$;'''.format(lname1, lname2, ' '*space12, ' '*space1, ' '*space2))
        f.write(no_confusion)
    f.write('\n')
    top_letter = 'axiom all_letters: $ top_letter == {} $;'.format(' \/ '.join(letters))
    f.write('\n{}\n'.format(top_letter))


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
