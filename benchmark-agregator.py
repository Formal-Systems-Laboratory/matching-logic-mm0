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

def minus(init, *args):
    if init is None: return None
    ret = init
    for arg in args:
        if arg is None: return None
        ret -= arg
    return ret

def divide(num, by):
    # Ceiling div
    if num is None or by is None: return None
    return math.ceil(num / by)

def percent(num, by):
    # Ceiling div
    if num is None or by is None: return None
    return math.ceil(num * 100 / by)


def times(num, by):
    if num is None or by is None: return None
    return (num * by)

def filter(name: str) -> bool:
    if name == '22-words-theorems': return True
    if re.match(r'^\d\d-.*$', name): return False
    if re.match(r'^eq-lr', name): return False
    if (re.match(r'^match-', name) or re.match(r'^eq-', name)) and not re.match(r'.*[1248]', name):
        return False

    # TODO: Curate cases that we want.
    if re.match(r'^implies-self', name): return False
    return True

def rename(name: str) -> str:
    name = name.replace('23-words-theorems', 'Base')
    name = name.replace('a-or-b-star', '$(a + b)\kleene$')
    name = name.replace('kleene-star-star', '${a\kleene}\kleene \limplies a\kleene$')
    name = name.replace('no-contains-a-or-no-only-b', '$\\lnot (\\top \\concat a \\concat \\top) + \lnot (b \\kleene)$')
    # TODO: Addition replacements
    name = re.sub(r'match-(\w)-00(\d)', r'$\\match_\1(\2)$', name)
    name = re.sub(r'eq-(\w)-00(\d)', r'$\\eq_\1(\2)$', name)
    return name

base_mmb_size = 0
base_mm1_size = 0
base_mmb_time = 0
def aggregate(input):
    global base_mmb_size, base_mm1_size, base_mmb_time, base_mm1_time
    simpls = plus(maybe_int(input['equiv_fp_imp_r']), maybe_int(input['bitr_fp_imp_r']))
    ret = {
        'Benchmark'     : rename(input['name']),
        '`.mm1` Size'   : divide(maybe_int(input['size_mm1']) - base_mm1_size, 1024),
        '`.mm1` time'   : maybe_float(input['gen_mm1']),
        '`.mmb` Size'   : divide(maybe_int(input['size_mmb']) - base_mmb_size, 1024),
        '`.mmb` time'   : maybe_float(input['compile']) - base_mmb_time,
        'Nodes'         : maybe_int(input['nodes_fp_imp_r']),
        'Thms 1'        : maybe_int(input['theorems_d_imp_fp']),
        'Thms 2'        : maybe_int(input['theorems_fp_imp_r']),
        'Simpls.'       : simpls,
        'cong'          : maybe_int(input['cong_fp_imp_r']),
        # 'per simpl.'    : divide(maybe_int(input['cong_fp_imp_r']), simpls),
        "O'head %"      : percent(minus( maybe_int(input['theorems_fp_imp_r'])
                                       , plus(times(2, simpls), maybe_int(input['cong_fp_imp_r']))
                                       )
                                 , maybe_int(input['theorems_fp_imp_r']))
    }
    if input['name'] == '22-words-theorems':
        base_mmb_size = maybe_int(input['size_mmb'])
        base_mm1_size = maybe_int(input['size_mm1'])
        base_mmb_time = maybe_float(input['compile'])
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


