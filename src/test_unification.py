import pytest

from src.check import Checker
from src.typ import *
from src.unifier_set import UnificationError


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

