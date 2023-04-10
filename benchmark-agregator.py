#!/usr/bin/env python3

import sys
import csv

def maybe_int(input):
    if input == '':
        return None
    return int(input)

def plus(left, right):
    if left is None or right is None: return None
    return left + right

def per(num, of):
    if num is None or of is None: return None
    return (num * 100 // of) / 100

def aggregate(input):
    return {
        'name'      : input['name'],
        'size_mmb'  : per(maybe_int(input['size_mmb']), 1000),
        'size_mm1'  : per(maybe_int(input['size_mm1']), 1000),
        'nodes'     : maybe_int(input['nodes_fp_imp_r']),
        'theorem_1' : maybe_int(input['theorems_d_imp_fp']),
        'theorem_2' : maybe_int(input['theorems_fp_imp_r']),
        'theorems'  : plus(maybe_int(input['theorems_fp_imp_r']), maybe_int(input['theorems_d_imp_fp'])),
        'simpls'    : plus(maybe_int(input['equiv_fp_imp_r']), maybe_int(input['equiv_d_imp_fp'])),
        'cong'      : per(maybe_int(input['cong_fp_imp_r']), maybe_int(input['theorems_fp_imp_r'])),
        'cong_simp' : per(maybe_int(input['cong_fp_imp_r']), maybe_int(input['equiv_fp_imp_r'])),
    }

with open('.build/benchmarks.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    writer = None
    for row in reader:
        out = aggregate(row)
        if not writer:
            writer = csv.DictWriter(sys.stdout, fieldnames=out.keys(), delimiter=',')
            writer.writeheader()
        if '001' in out['name']:
            print('.', file=sys.stdout)
        writer.writerow(out)
    print('.', file=sys.stdout)
    assert writer
    writer.writeheader()


