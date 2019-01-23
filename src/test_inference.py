import src.check as check
from src.syntax import Const, Ident, Lambda, Call
from src.typ import Int, Var, Bool, Fn


def test_const():
    checker = check.Checker()
    three = Const(3, Int)
    assert three.infer_type(checker) == Int

    t = Const(True, Bool)
    assert t.infer_type(checker) == Bool


def test_ident():
    checker = check.Checker()
    x = Ident("x")
    checker.type_env[x] = Int
    assert x.infer_type(checker) == Int


def test_lambda():
    checker = check.Checker()

    id = Lambda(Ident("x"), Ident("x"))
    id_type = id.infer_type(checker)

    T = Var()
    equiv_type = Fn(T, T)
    checker.unify(id_type, equiv_type)
    assert True


def test_call():
    checker = check.Checker()

    id = Lambda(Ident("x"), Ident("x"))
    checker.type_env[Ident("id")] = id.infer_type(checker)

    call = Call(Ident("id"), Const(3, Int))
    assert call.infer_type(checker) == Int


