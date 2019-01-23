import typ
from syntax import Ident
from unifier_set import UnifierSet, UnificationError


def std_env():
    std = {
        Ident("true"): typ.Bool,
        Ident("false"): typ.Bool,
        Ident("zero"): typ.Fn(typ.Int, typ.Bool),
        Ident("succ"): typ.Fn(typ.Int, typ.Int),
        Ident("pred"): typ.Fn(typ.Int, typ.Int),
        Ident("times"): typ.Fn(typ.Int, typ.Fn(typ.Int, typ.Int))
    }

    T = typ.Var()
    U = typ.Var()
    std[Ident("pair")] = typ.Fn(T, typ.Fn(U, typ.Tuple(T, U)))

    return std


class Checker:
    def __init__(self):
        self.type_env = std_env()
        self.unifiers = UnifierSet(typ.Var)
        self.non_generic_vars = set()

    def make_non_generic(self, var):
        self.non_generic_vars.add(var)

    def fresh_var(self) -> typ.Var:
        """
        A Var should always be added to the global UnifierSet whenever it's
        created. Returns a non-generic type variable.
        """
        v = typ.Var()
        self.unifiers.add(v)
        return v

    def duplicate_type(self, t: typ.Type) -> typ.Type:
        """
        Duplicates a type, taking into consideration the genericness and
        non-genericness of type variables.

        If T is a non-generic type, then:
        self.duplicate_type(Fn(T, U)) == Fn(T, V)

        :param t:
        :return:
        """
        ...

    def occurs_in_type(self, t1, t2):
        if t1 == t2:
            return True
        elif isinstance(t2, typ.Poly):
            return any(self.occurs_in_type(t1, t) for t in t2.vals)
        else:
            return False

    def unify(self, t1, t2, unifiers=None) -> UnifierSet:
        unifiers = UnifierSet(typ.Var) if unifiers is None else unifiers

        if type(t1) is typ.Var:
            if t1 != t2:
                if not self.occurs_in_type(t1, t2):
                    unifiers.unify(t1, t2)
                    return unifiers
                else:
                    raise UnificationError("Recursive unification!")
            else:
                # Type variables are identical, no need to unify.
                return unifiers
        elif isinstance(t1, typ.Poly) and type(t2) is typ.Var:
            return self.unify(t2, t1, unifiers)  # Swap args and call again
        elif isinstance(t1, typ.Poly) and isinstance(t2, typ.Poly):
            if type(t1) is not type(t2):
                raise UnificationError(f"Type mismatch: {t1} != {t2}")
            elif len(t1.vals) != len(t2.vals):
                msg = f"Type mismatch: {t1} has different arity than {t2}!"
                raise UnificationError(msg)
            else:
                for x, y in zip(t1.vals, t2.vals):
                    self.unify(x, y, unifiers)
                return unifiers


if __name__ == "__main__":
    from typ import *

    checker = Checker()
    T = Var("T")
    U = Var("U")

    unifs = checker.unify(T, U)
    assert unifs.same_set(T, U)

    unifs = checker.unify(T, Bool)
    assert unifs.same_set(T, Bool)

    unifs = checker.unify(Tuple(T, Bool), Tuple(Int, U))
    assert unifs.same_set(T, Int)
    assert unifs.same_set(U, Bool)

    try:
        good = False
        unifs = checker.unify(Tuple(Bool, Int), Tuple(T, T))
    except UnificationError as e:
        good = True
    finally:
        assert good, "Expected unification error!"

    try:
        good = False
        unifs = checker.unify(Tuple(Bool, Int), Tuple(Bool))
    except UnificationError as e:
        good = True
    finally:
        assert good, "Expected unification error"

    try:
        good = False
        unifs = checker.unify(Tuple(Bool, Int), Fn(Bool, Int))
    except UnificationError as e:
        good = True
    finally:
        assert good, "Expected unification error"

    print("Tests Pass.")
