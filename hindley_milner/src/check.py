from contextlib import contextmanager
from typing import Set

from hindley_milner.src import env
from hindley_milner.src import syntax, typ
from hindley_milner.src import std_env
from hindley_milner.src.unifier_set import UnifierSet, UnificationError, RecursiveUnificationError


class Checker:
    def __init__(self):
        self.type_env: std_env.StdEnv = std_env.std_env()
        self.unifiers = UnifierSet(typ.Var)
        self.non_generic_vars: Set[typ.Var] = set()

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
        self.type_env = env.Env(self.type_env)
        yield
        self.type_env = self.type_env.parent

    def make_non_generic(self, t: typ.Type) -> None:
        """
        Recursively searches for `Var`s in `t`, making them all non-generic.
        :param t:
        :return:
        """
        if type(t) is typ.Var:
            self.non_generic_vars.add(t)
        elif isinstance(t, typ.Poly):
            for x in t.vals:
                self.make_non_generic(x)

    def fresh_var(self, non_generic=False) -> typ.Var:
        """
        A Var should always be added to the global UnifierSet whenever it's
        created. Returns a non-generic type variable unless otherwise specified.
        """
        v = typ.Var()
        self.unifiers.add(v)
        if non_generic:
            self.non_generic_vars.add(v)
        return v

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

        if type(t) is typ.Var:
            if t in self.non_generic_vars:
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

                # "In unifying a non-generic type variable to a term, all the type
                # variables contained in that term become non-generic."
                #   -- Luca Cardelli, Basic Polymorphic Typechecking, 1988, pg. 11

                if t1 in self.non_generic_vars:
                    self.make_non_generic(t2)

                if type(t2) is typ.Var and t2 in self.non_generic_vars:
                    self.make_non_generic(t1)

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


