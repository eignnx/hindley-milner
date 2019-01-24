import pytest

from hindley_milner.src.check import Checker
from hindley_milner.src.typ import *
from hindley_milner.src.unifier_set import UnificationError


def test_var_unification():
    checker = Checker()
    T = checker.fresh_var()
    U = checker.fresh_var()

    assert not checker.unifiers.same_set(T, U)

    checker.unify(T, U)
    assert checker.unifiers.same_set(T, U)

    checker.unify(T, Bool)
    assert checker.unifiers.same_set(T, Bool)
    assert checker.unifiers.same_set(U, Bool)


def test_var_more_unification():
    checker = Checker()
    T = checker.fresh_var()
    U = checker.fresh_var()

    checker.unify(Tuple(T, Bool), Tuple(Int, U))
    assert checker.unifiers.same_set(T, Int)
    assert checker.unifiers.same_set(U, Bool)


def test_unification_error():
    checker = Checker()
    T = checker.fresh_var()

    with pytest.raises(UnificationError):
        checker.unify(Tuple(Bool, Int), Tuple(T, T))

    with pytest.raises(UnificationError):
        checker.unify(Tuple(Bool, Int), Tuple(Bool))

    with pytest.raises(UnificationError):
        checker.unify(Tuple(Bool, Int), Fn(Bool, Int))


def test_basic_generic_non_generic_unification():
    checker = Checker()

    generic = checker.fresh_var()
    non_generic = checker.fresh_var()

    checker.make_non_generic(non_generic)

    checker.unify(generic, non_generic)

    assert generic in checker.non_generic_vars


def test_basic_generic_non_generic_unification_reversed():
    checker = Checker()

    generic = checker.fresh_var()
    non_generic = checker.fresh_var()

    checker.make_non_generic(non_generic)

    checker.unify(non_generic, generic)

    assert generic in checker.non_generic_vars


def test_complex_generic_non_generic_unification():
    checker = Checker()

    generic = checker.fresh_var()
    non_generic = checker.fresh_var()

    checker.make_non_generic(non_generic)

    t = Tuple(generic)
    checker.unify(non_generic, t)

    assert generic in checker.non_generic_vars
