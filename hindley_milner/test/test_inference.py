from hindley_milner.src import check
from hindley_milner.src.syntax import Const, Ident, Lambda, Call, Let, If
from hindley_milner.src.typ import Int, Bool, Fn, Tuple, List


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

    T = checker.fresh_var()
    equiv_type = Fn(T, T)
    checker.unify(id_type, equiv_type)
    assert True


def test_call():
    checker = check.Checker()

    id = Lambda(Ident("x"), Ident("x"))
    checker.type_env[Ident("id")] = id.infer_type(checker)

    call = Call(Ident("id"), Const(3, Int))
    assert checker.unifiers.equivalent(call.infer_type(checker), Int)


def test_simple_let():
    """
    let x = 3 in x
    """
    checker = check.Checker()

    x = Ident("x")
    let = Let(x, Const(3, Int), x)
    assert checker.unifiers.equivalent(let.infer_type(checker), Int)


def test_complex_let():
    """
    let f = fun(a) a
    in pair( f(3) )( f(true) )
    """
    checker = check.Checker()

    f = Ident("f")
    a = Ident("a")
    three = Const(3, Int)
    true = Const(True, Bool)
    pair = Ident("pair")  # From std_env.

    f_of_3 = Call(f, three)
    f_of_true = Call(f, true)
    pair_call = Call(Call(pair, f_of_3), f_of_true)

    fn = Lambda(a, a)
    let = Let(f, fn, pair_call)

    inferred = let.infer_type(checker)
    assert checker.unifiers.equivalent(inferred, Tuple(Int, Bool))


def test_length_fn():
    """
    let length = fun(l)
        if null(l)
            then 0
            else succ(length(tail(l)))
    in length([true])
    """
    checker = check.Checker()

    length = Ident("length")
    l = Ident("l")
    tail = Ident("tail")
    succ = Ident("succ")
    null = Ident("null")

    tail_call = Call(tail, l)
    rec_call = Call(length, tail_call)
    succ_call = Call(succ, rec_call)

    if_stmt = If(
        Call(null, l),
        Const(0, Int),
        succ_call
    )

    fn = Lambda(l, if_stmt)

    body = Call(length, Const([True], List(Bool)))
    let = Let(length, fn, body)

    print(let.infer_type(checker))
