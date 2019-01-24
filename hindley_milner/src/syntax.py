from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from hindley_milner.src import check
from hindley_milner.src.typ import Type, Fn, Var, Bool


# TODO: Impl `infer_type` for all subclasses of `AstNode`.
class AstNode(ABC):
    @abstractmethod
    def infer_type(self, checker: check.Checker) -> Type:
        pass


class Value(AstNode, ABC):
    pass


@dataclass(frozen=True)
class Ident(Value):
    """
    An identifier.
    x, printf, abstract_singleton_bean
    """
    name: str

    def infer_type(self, checker: check.Checker) -> Type:
        return checker.type_env[self]

    def __str__(self):
        return self.name


@dataclass
class Const(Value):
    """
    A literal.
    1, true, -4.21983, point { x=1, y=2 }
    """
    value: object
    type: field(init=False)

    def infer_type(self, checker: check.Checker) -> Type:
        return self.type

    def __str__(self):
        return str(self.value)


@dataclass
class Lambda(AstNode):
    """
    lambda param: body
    """
    param: Ident
    body: AstNode

    def infer_type(self, checker: check.Checker) -> Type:

        # In a new scope, infer the type of the body.
        with checker.new_scope():
            # Parameter types are non-generic
            arg_type = checker.fresh_var(non_generic=True)
            checker.type_env[self.param] = arg_type
            body_type = self.body.infer_type(checker)

        # After inferring body's type, arg type might be known.
        arg_type = checker.unifiers.root_of(arg_type)

        return Fn(arg_type, body_type)


@dataclass
class Call(AstNode):
    """
    fn(arg)
    """
    fn: AstNode
    arg: AstNode

    def infer_type(self, checker: check.Checker) -> Type:

        # Set up a function type.
        alpha = checker.fresh_var()
        beta = checker.fresh_var()
        fn_type = Fn(alpha, beta)

        # Ensure the `self.fn` refers to a Fn type.
        checker.unify(fn_type, self.fn.infer_type(checker))

        # Get best guess as to the type of `self.arg`.
        arg_type = self.arg.infer_type(checker)

        # Link that best guess with the new type variable `beta`.
        checker.unify(arg_type, beta)

        # In case beta's root was changed in the last unification, get it's current root.
        return checker.unifiers.root_of(beta)


@dataclass
class If(AstNode):
    """
    if pred then yes else no
    """
    pred: AstNode
    yes: AstNode
    no: AstNode

    def infer_type(self, checker: check.Checker) -> Type:
        pred_type = self.pred.infer_type(checker)
        checker.unify(pred_type, Bool)

        yes_type = self.yes.infer_type(checker)
        no_type = self.no.infer_type(checker)
        checker.unify(yes_type, no_type)

        return yes_type


@dataclass
class Let(AstNode):
    """
    let left = right in body
    """
    left: Ident
    right: AstNode
    body: AstNode

    def infer_type(self, checker: check.Checker) -> Type:
        with checker.new_scope():

            # First, bind `left` to a fresh type variable. This allows
            # for recursive let statements.
            alpha = checker.fresh_var()
            checker.type_env[self.left] = alpha

            # Next infer the type of `right` using the binding just created.
            right_type = self.right.infer_type(checker)

            # Link the type variable with the inferred type of `right`.
            checker.unify(alpha, right_type)

            # With the environment set up, now the body can be typechecked.
            return self.body.infer_type(checker)
