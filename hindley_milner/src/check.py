from contextlib import contextmanager
from typing import Set

from hindley_milner.src import env, utils
from hindley_milner.src import syntax, typ
from hindley_milner.src import std_env
from hindley_milner.src.unifier_set import UnifierSet, UnificationError, RecursiveUnificationError


class Checker:
    def __init__(self):
        self.unifiers = UnifierSet()
        self.type_env: std_env.StdEnv = std_env.std_env(self)

    def is_non_generic(self, v):
        return v in self.unifiers.non_generic_vars

    def is_generic(self, v):
        return not self.is_non_generic(v)

    @contextmanager
    def new_scope(self) -> None:
        """
        A context manager for typechecking inside a nested scope.

        Example:
        >>> checker = Checker()
        >>> x = syntax.Ident("x")
        >>> checker.type_env[x] = 333
        >>> with checker.new_scope():
        ...     checker.type_env[x] = 555
        ...     assert checker.type_env[x] == 555
        >>> assert checker.type_env[x] == 333
        """
        self.type_env = env.Env(parent=self.type_env)
        yield
        self.type_env = self.type_env.parent

    @contextmanager
    def scoped_non_generic(self) -> typ.Var:
        """
        A context manager that yields a fresh type variable that is
        non-generic only inside the scope of the with-block.

        Example:
        >>> checker = Checker()
        >>> with checker.scoped_non_generic() as alpha:
        ...     assert checker.is_non_generic(alpha)
        >>> assert checker.is_generic(alpha)
        """
        alpha = self.fresh_var(non_generic=True)
        yield alpha
        self.unifiers.make_generic(alpha)

    def fresh_var(self, non_generic=False) -> typ.Var:
        return self.unifiers.fresh_var(non_generic)

    def duplicate_type(self, t: typ.Type, substitutions=None) -> typ.Type:
        """
        Duplicates a type, taking into consideration the genericness and
        non-genericness of type variables.

        If T is a non-generic Var and U is a generic Var, then:
        self.duplicate_type(Fn(T, U, U)) == Fn(T, V, V)

        "In copying a type, we must only copy the generic variables, while the
        non-generic variables must be shared."
            -- Luca Cardelli, Basic Polymorphic Typechecking, 1988, pg. 11

        :param t:
        :param substitutions:
        :return:
        """
        substitutions = dict() if substitutions is None else substitutions

        # If t = Var("a") and Var("a") is unified with Tuple(x, y), duplicate
        # the Tuple, not the Var.
        t = self.unifiers.get_concrete(t)

        if type(t) is typ.Var:
            if self.is_non_generic(t):
                # Non-generic variables should be shared, not duplicated.
                return t
            elif t in substitutions.keys():
                # Already seen this substitution before. Use previously agreed
                # upon substitution.
                return substitutions[t]
            else:
                # Create a new substitution
                substitutions[t] = self.fresh_var()
                return substitutions[t]
        elif isinstance(t, typ.Poly):
            cls = type(t)
            args = (self.duplicate_type(x, substitutions) for x in t.vals)
            return cls(*args)

    def unify(self, t1: typ.Type, t2: typ.Type) -> None:
        self.unifiers.unify(t1, t2)


