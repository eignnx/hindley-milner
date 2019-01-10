import typ
from unifier_set import UnifierSet, UnificationError

def std_env():
    std = {}

    std["true"] = typ.Bool
    std["false"] = typ.Bool
    std["zero"] = typ.Fn(typ.Int, typ.Bool)
    std["succ"] = typ.Fn(typ.Int, typ.Int)
    std["pred"] = typ.Fn(typ.Int, typ.Int)
    std["times"] = typ.Fn(typ.Int, Fn(typ.Int, typ.Int))

    T = typ.Var()
    U = typ.Var()
    std["pair"] = typ.Fn(T, Fn(U, typ.Tuple(T, U)))

    return std


class Checker:
    def __init__(self):
        self.env = std_env()

    def occurs_in_type(self, t1, t2):
        if t1 == t2:
            return True
        elif isinstance(t2, typ.Poly):
            return any(self.occurs_in_type(t1, t) for t in t2.vals)
        else:
            return False

    def unify(self, t1, t2):
        unifiers = UnifierSet(typ.Var)
        return self._unify_rec(t1, t2, unifiers)

    def _unify_rec(self, t1, t2, unifiers):
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
            return self._unify_rec(t2, t1, unifiers) # Swap args and call again
        elif isinstance(t1, typ.Poly) and isinstance(t2, typ.Poly):
            if type(t1) is not type(t2):
                raise UnificationError(f"Type mismatch: {t1} != {t2}")
            elif len(t1.vals) != len(t2.vals):
                msg = f"Type mismatch: {t1} has different arity than {t2}!"
                raise UnificationError(msg)
            else:
                for x, y in zip(t1.vals, t2.vals):
                    self._unify_rec(x, y, unifiers)
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
