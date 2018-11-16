import typ
from disjoint_set import DisjointSet

def std_env():
    T = typ.Var()
    U = typ.Var()

    return {
        "true": typ.Bool,
        "false": typ.Bool,
        "zero": typ.Fn(typ.Int, typ.Bool),
        "succ": typ.Fn(typ.Int, typ.Int),
        "pred": typ.Fn(typ.Int, typ.Int),
        "times": typ.Fn(typ.Int, typ.Fn(typ.Int, typ.Int)),
        "pair": typ.Fn(T, typ.Fn(U, typ.Tuple(T, U))),
    }

class Checker:
    def __init__(self):
        self.env = std_env()
        self.unifiers = DisjointSet()

    def prune_type(self, t):
        if type(t) is typ.Var and t in self.unifiers:
            return self.unifiers.root_of(t)
        else:
            return t

    def occurs_in_type(self, t1, t2):
        t2 = self.prune_type(t2)
        if t1 == t2:
            return True
        elif isinstance(t2, typ.Poly):
            return any(self.occurs_in_type(t1, t) for t in t2.vals)
        else:
            return False

    def unify(self, t1, t2):
        unifiers = DisjointSet()
        return self._unify_rec(t1, t2, unifiers)

    def _unify_rec(self, t1, t2, unifiers):
        #t1 = self.prune_type(t1)
        #t2 = self.prune_type(t2)

        if type(t1) is typ.Var:
            if t1 != t2:
                if self.occurs_in_type(t1, t2):
                    raise Exception("Recursive unification!")
                else:
                    if t1 in unifiers and type(t2) is not typ.Var:
                        t1_family = unifiers.family_of(t1)
                        t1_family = {t for t in t1_family if type(t) is not typ.Var}
                        t1_family = ", ".join(str(t) for t in t1_family)
                        msg = f"{t1} is already unified with {t1_family}, and cannot unify with {t2} as well!"
                        raise Exception(msg)
                    unifiers.add(t1)
                    unifiers.add(t2)
                    unifiers.join(t1, t2)
            else:
                # Type variables are identical, no need to unify.
                pass
        elif isinstance(t1, typ.Poly) and type(t2) is typ.Var:
            self._unify_rec(t2, t1, unifiers) # Swap args and call again
        elif isinstance(t1, typ.Poly) and isinstance(t2, typ.Poly):
            if type(t1) is not type(t2):
                raise Exception(f"Type mismatch: {t1} != {t2}")
            elif len(t1.vals) != len(t2.vals):
                raise Exception(f"Type mismatch: {t1} has different arity than {t2}!")
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
    except Exception as e:
        good = True
    finally:
        assert good, "Expected unification error!"

    print("Tests Pass.")