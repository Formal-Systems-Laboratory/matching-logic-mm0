from collections import defaultdict
import os
import time
from typing import Any, Dict, List, NamedTuple, Optional, Tuple, no_type_check

### Benchmarks ##################

class ProofStats(NamedTuple):
    theorems: int
    pos: int
    subst: int
    equiv: int
    bitr: int
    cong: int
    nodes: int

class Benchmark(NamedTuple):
    join:      Optional[int] = None
    compile:   Optional[int] = None
    check:     Optional[int] = None
    gen_mm0:   Optional[int] = None
    join_mm0:  Optional[int] = None
    gen_mm1:   Optional[int] = None
    gen_ph:    Optional[int] = None

    size_mmb:  Optional[int] = None
    size_mm1:  Optional[int] = None

    fp_imp_r_stats: Optional[ProofStats] = None
    d_imp_fp_stats: Optional[ProofStats] = None

    def _asdict_nested(self) -> Dict[str,Any]:
        ret = self._asdict()
        del ret['fp_imp_r_stats']
        del ret['d_imp_fp_stats']
        if self.fp_imp_r_stats:
            ret.update({ k + '_fp_imp_r' : v for k,v in self.fp_imp_r_stats._asdict().items() })
        if self.d_imp_fp_stats:
            ret.update({ k + '_d_imp_fp' : v for k,v in self.d_imp_fp_stats._asdict().items() })
        return ret

def benchmark_fields() -> List[str]:
    ret = list(Benchmark._fields[0:-2])
    ret = ret + [k + '_fp_imp_r' for k in ProofStats._fields]
    ret = ret + [k + '_d_imp_fp' for k in ProofStats._fields]
    return ret


benchmarks : Dict[str, Benchmark] = defaultdict(lambda: Benchmark())

class _Benchmark():
    def __init__(self, test_name: str, aspect: str):
        self.test_name = test_name
        self.aspect = aspect
        self.start = time.time_ns()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        end = time.time_ns()
        runtime = (end - self.start) / (1000 * 1000)
        benchmarks[self.test_name] = benchmarks[self.test_name]._replace(**{self.aspect: runtime})

def benchmark(test_name: str, aspect: str) -> _Benchmark:
    return _Benchmark(test_name, aspect)

def record_mmb_stats(test_name: str, mmb_file: str) -> None:
    b = benchmarks[test_name]._replace(size_mmb=os.path.getsize(mmb_file))
    benchmarks[test_name] = b

def record_mm1_stats(test_name: str, mm1_file: str) -> None:
    b = benchmarks[test_name]._replace(size_mm1=os.path.getsize(mm1_file))
    with open(mm1_file) as f:
        for l in f:
            prefix = '---  stat '
            if not l.startswith(prefix):
                continue
            l = l[len(prefix):-2]
            vals = l.split(',')
            stats = ProofStats(*(int(v) for v in vals[1:]))
            if vals[0] == 'fp_implies_regex':
                b = b._replace(fp_imp_r_stats=stats)
            elif vals[0] == 'top_implies_fp':
                b = b._replace(d_imp_fp_stats=stats)
            else:
                assert False

    benchmarks[test_name] = b
