from itertools import tee

def pairwise(seq):
    first, second = tee(iter(seq))
    next(second)
    return zip(first, second)

def set_to_str(s):
    ele_list = ", ".join({str(v) for v in s})
    return f"{{{ele_list}}}"
