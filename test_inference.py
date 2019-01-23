from check import Checker
from syntax import Const, Ident, Lambda, Call
from env import Env
from typ import Int, Var, Bool, Fn
from unifier_set import UnifierSet


def test_const():
    three = Const(3, Int)
    assert three.infer_type(Env(), UnifierSet(Var)) == Int

    t = Const(True, Bool)
    assert t.infer_type(Env(), UnifierSet(Var)) == Bool


def test_ident():
    x = Ident("x")
    env = Env()
    env[x] = Int
    assert x.infer_type(env, UnifierSet(Var)) == Int


def test_lambda():
    checker = Checker()

    id = Lambda(Ident("x"), Ident("x"))
    id_type = id.infer_type(Env(), UnifierSet(Var))

    T = Var()
    equiv_type = Fn(T, T)
    assert checker.unify(id_type, equiv_type) is not None


def test_call():
    checker = Checker()
    type_env = Env()
    unifiers = UnifierSet(Var)

    id = Lambda(Ident("x"), Ident("x"))
    type_env[Ident("id")] = id.infer_type(type_env, unifiers)

    call = Call(Ident("id"), Const(3, Int))
    assert call.infer_type(type_env, unifiers) == Int


