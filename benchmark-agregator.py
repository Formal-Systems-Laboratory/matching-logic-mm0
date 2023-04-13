#!/usr/bin/env python3

import sys
import csv
import re
import math

def maybe_int(input):
    if input == '':
        return None
    return int(input)

def maybe_float(input):
    if input == '':
        return None
    return math.ceil(float(input))

def plus(*args):
    ret = 0
    for arg in args:
        if arg is None: return None
        ret += arg
    return ret

def divide(num, by):
    # Ceiling div
    if num is None or by is None: return None
    return math.ceil(num / by)

def filter(name: str) -> bool:
    if name == '22-words-theorems': return True
    if re.match(r'^\d\d-.*$', name): return False
    if re.match(r'^eq-lr', name): return False
    if (re.match(r'^match-', name) or re.match(r'^eq-', name)) and not re.match(r'.*[1248]', name):
        return False
    return True

def rename(name: str) -> str:
    name = name.replace('a-or-b-star', '$(a + b)\kleene$')
    name = name.replace('kleene-star-star', '${a\kleene}\kleene \limplies a\kleene$')
    # TODO: Addition replacements
    name = re.sub(r'match-(\w)-00(\d)', r'$\\match_\1(\2)$', name)
    name = re.sub(r'eq-(\w)-00(\d)', r'$\\eq_\1(\2)$', name)
    return name

base_mmb = 0
base_mm1 = 0
def aggregate(input):
    global base_mmb, base_mm1
    simpls = plus( maybe_int(input['equiv_fp_imp_r']), maybe_int(input['equiv_d_imp_fp'])
                 , maybe_int(input['bitr_fp_imp_r']), maybe_int(input['bitr_d_imp_fp'])
                 )
    ret = {
        'Benchmark'         : rename(input['name']),
        '`.mm1` Size'         : divide(maybe_int(input['size_mm1']) - base_mm1, 1024),
        '`.mm1` time'          : maybe_float(input['gen_mm1']),
        '`.mmb` Size'          : divide(maybe_int(input['size_mmb']) - base_mmb, 1024),
        '`.mmb` time'          : maybe_float(input['compile']),
        'Nodes'             : maybe_int(input['nodes_fp_imp_r']),
        'Thms'          : plus(maybe_int(input['theorems_fp_imp_r']), maybe_int(input['theorems_d_imp_fp'])),
        'simpls.'           : simpls,
        'cong'               : maybe_int(input['cong_fp_imp_r']),
        'per simpl.'    : divide(maybe_int(input['cong_fp_imp_r']), simpls),
    }
    if input['name'] == '22-words-theorems':
        base_mmb = maybe_int(input['size_mmb'])
        base_mm1 = maybe_int(input['size_mm1'])
    return ret

with open('.build/benchmarks.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    writer = None
    for row in reader:
        out = aggregate(row)
        if not writer:
            writer = csv.DictWriter(sys.stdout, fieldnames=out.keys(), delimiter=',')
            writer.writeheader()
        if not filter(row['name']):
            continue
        writer.writerow(out)
    assert writer


