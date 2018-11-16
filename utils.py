
def set_to_str(s):
    ele_list = ", ".join({str(v) for v in s})
    return f"{{{ele_list}}}"