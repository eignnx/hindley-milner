from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from src import check
from src.typ import Type, Fn, Var


class AstNode(ABC):
    @abstractmethod
    def infer_type(self, checker: check.Checker) -> Type:
        pass


class Value(AstNode):
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
    lambda arg: body
    """
    arg: Ident
    body: AstNode

    def infer_type(self, checker: check.Checker) -> Type:
        arg_type = Var()
        checker.unifiers.add(arg_type)
        checker.type_env[self.arg] = arg_type
        body_type = self.body.infer_type(checker)

        # After inferring body's type, arg type might be known.
        arg_type = checker.unifiers.root_of(arg_type)

        return Fn(arg_type, body_type)


@dataclass
class Call(AstNode):
    """
    fn(arg)
    """
    fn: Ident
    arg: AstNode

    def infer_type(self, checker: check.Checker) -> Type:

        # Set up a function type.
        alpha = checker.fresh_var()
        beta = checker.fresh_var()
        fn_type = Fn(alpha, beta)

        # Get best guess as to the type of `self.arg`.
        arg_type = self.arg.infer_type(checker)

        # Link that best guess with the new type variable `beta`.
        checker.unify(arg_type, beta)

        # Ensure the `self.fn` refers to a Fn type.
        checker.unify(fn_type, checker.type_env[self.fn])

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


@dataclass
class Let(AstNode):
    """
    let left = right in body
    """
    left: Ident
    right: AstNode
    body: AstNode
