from src import typ
from src import syntax
from src.unifier_set import UnifierSet, UnificationError, RecursiveUnificationError


def std_env():
    std = {
        syntax.Ident("true"): typ.Bool,
        syntax.Ident("false"): typ.Bool,
        syntax.Ident("zero"): typ.Fn(typ.Int, typ.Bool),
        syntax.Ident("succ"): typ.Fn(typ.Int, typ.Int),
        syntax.Ident("pred"): typ.Fn(typ.Int, typ.Int),
        syntax.Ident("times"): typ.Fn(typ.Int, typ.Fn(typ.Int, typ.Int))
    }

    T = typ.Var()
    U = typ.Var()
    std[syntax.Ident("pair")] = typ.Fn(T, typ.Fn(U, typ.Tuple(T, U)))

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

    def unify(self, t1: typ.Type, t2: typ.Type) -> None:

        if type(t1) is typ.Var:
            if t1 == t2:
                return  # Type variables are identical, no need to unify.
            elif self.occurs_in_type(t1, t2):
                raise RecursiveUnificationError
            else:
                self.unifiers.unify(t1, t2)
        elif isinstance(t1, typ.Poly) and isinstance(t2, typ.Poly):
            if type(t1) is not type(t2):
                msg = f"Type mismatch: {t1} != {t2}"
                raise UnificationError(msg)
            elif len(t1.vals) != len(t2.vals):
                msg = f"Type mismatch: {t1} has different arity than {t2}!"
                raise UnificationError(msg)
            else:
                for x, y in zip(t1.vals, t2.vals):
                    self.unify(x, y)
        elif isinstance(t1, typ.Poly) and type(t2) is typ.Var:
            return self.unify(t2, t1)  # Swap args and call again

