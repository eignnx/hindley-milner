from src import check, typ


def test_generic_var_duplication():
    checker = check.Checker()
    T = checker.fresh_var()
    assert checker.duplicate_type(T) != T


def test_non_generic_var_duplication():
    checker = check.Checker()
    T = checker.fresh_var()
    checker.make_non_generic(T)
    assert checker.duplicate_type(T) == T


def test_simple_compound_type_duplication():
    checker = check.Checker()
    fn = typ.Fn(typ.Int, typ.Bool)
    assert checker.duplicate_type(fn) == fn


def test_compound_type_with_type_vars():
    checker = check.Checker()

    generic = checker.fresh_var()
    non_generic = checker.fresh_var()
    checker.make_non_generic(non_generic)

    tup = typ.Tuple(non_generic, non_generic, generic, generic)
    actual = checker.duplicate_type(tup)

    assert type(actual) is typ.Tuple

    a, b, c, d = actual.vals

    assert a == non_generic
    assert b == non_generic
    assert c != non_generic
    assert c != generic
    assert d != non_generic
    assert d != generic


def test_deep_type_duplication():
    checker = check.Checker()

    G1 = checker.fresh_var()
    G2 = checker.fresh_var()
    N1 = checker.fresh_var()
    N2 = checker.fresh_var()

    checker.make_non_generic(N1)
    checker.make_non_generic(N2)

    orig = typ.Tuple(G1, N1, N1, N2, typ.Tuple(G1, N1, N2, G2, typ.Int), typ.Int)
    duplicated = checker.duplicate_type(orig)

    assert type(duplicated) is typ.Tuple

    g1_outer, n1_outer_1, n1_outer_2, n2_outer, tup, i_outer = duplicated.vals

    assert g1_outer != G1
    assert n1_outer_1 == N1 == n1_outer_2
    assert n2_outer == N2
    assert i_outer == typ.Int

    assert type(tup) is typ.Tuple

    g1_inner, n1_inner, n2_inner, g2_inner, i_inner = tup.vals

    assert g1_inner == g1_outer
    assert n1_inner == n1_outer_1 == N1
    assert n2_inner == n2_outer == N2
    assert g2_inner != G2
    assert i_inner == typ.Int
