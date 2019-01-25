from itertools import tee
from typing import Iterator

from hindley_milner.src import unicode


def fresh_greek_stream() -> Iterator[str]:
    yield from unicode.GREEK_LOWER
    n = 1
    while True:
        yield from (f"{ch}{n}" for ch in unicode.GREEK_LOWER)
        n += 1


def pairwise(seq):
    first, second = tee(iter(seq))
    next(second)
    return zip(first, second)


def set_to_str(s):
    ele_list = ", ".join({str(v) for v in s})
    return f"{{{ele_list}}}"


def instance(cls):
    """
    A class decorator that replaces its input class with an instance of that
    class.
    :param cls:
    :return:
    """
    return cls()
