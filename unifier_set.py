from disjoint_set import DisjointSet

class UnificationError(Exception):
    pass

class UnifierSet(DisjointSet):
    def __init__(self, var_type):
        super().__init__()
        self.var_type = var_type

    def unify(self, *e):
        from itertools import tee
        e, e_next = tee(iter(e))
        _ = next(e_next)
        for e1, e2 in zip(e, e_next):
            self._unify2(e1, e2)

    def _unify2(self, e1, e2):
        if e1 not in self.map: self.add(e1)
        if e2 not in self.map: self.add(e2)
        r1 = self.root_of(e1)
        r2 = self.root_of(e2)
        self.join_roots(r1, r2)

    def join_roots(self, r1, r2):
        size1, size2 = self.map[r1], self.map[r2]
        r1_is_var = isinstance(r1, self.var_type)
        r2_is_var = isinstance(r2, self.var_type)

        if r1_is_var and not r2_is_var:
            # `r2` is something concrete, make it the root.
            self.map[r2] += size1
            self.map[r1] = r2
        elif r2_is_var and not r1_is_var:
            # `r1` is something concrete, make it the root.
            self.map[r1] += size2
            self.map[r2] = r1
        elif r2_is_var and r1_is_var:
            # Use weighting heuristic to keep it fast.
            if size1 > size2:
                self.map[r1] += size2
                self.map[r2] = r1
            else:
                self.map[r2] += size1
                self.map[r1] = r2
        else: # Both are different concrete objects => error.
            if r1 != r2:
                msg = f"Cannot unify concrete types {r1} and {r2}!"
                raise UnificationError(msg)

    def equivalent(self, e1, e2):
        return self.same_set(e1, e2)

if __name__ == "__main__":
    from typ import *
    u = UnifierSet(Var)
    X, Y, Z = Var("X"), Var("Y"), Var("Z")
    u.unify(X, Y)
    u.unify(Z, Int)
    u.unify(Y, Bool)
    print(u)
