from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from check import Checker
from env import Env
from typ import Type, Fn, Var
from unifier_set import UnifierSet


class AstNode(ABC):
    @abstractmethod
    def infer_type(self, type_env: Env, unifiers: UnifierSet) -> Type:
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

    def infer_type(self, type_env: Env, unifiers: UnifierSet) -> Type:
        return type_env[self]

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

    def infer_type(self, type_env: Env, unifiers: UnifierSet) -> Type:
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

    def infer_type(self, type_env: Env, unifiers: UnifierSet) -> Type:
        arg_type = Var()
        unifiers.add(arg_type)
        type_env[self.arg] = arg_type
        body_type = self.body.infer_type(type_env, unifiers)
        arg_type = unifiers.root_of(arg_type)  # After inferring body's type, arg type might be known.
        return Fn(arg_type, body_type)


@dataclass
class Call(AstNode):
    """
    fn(arg)
    """
    fn: Ident
    arg: AstNode

    def infer_type(self, type_env: Env, unifiers: UnifierSet) -> Type:
        checker = Checker()

        # Set up a function type.
        alpha, beta = Var(), Var()
        unifiers.add(alpha), unifiers.add(beta)
        fn_type = Fn(alpha, beta)

        # Get best buess as to the type of `self.arg`.
        arg_type = self.arg.infer_type(type_env, unifiers)

        # Link that best guess with the new type variable `beta`.
        checker.unify(arg_type, beta, unifiers)

        # Ensure the `self.fn` refers to a Fn type.
        checker.unify(fn_type, type_env[self.fn], unifiers)

        # In case beta's root was changed in the last unification, get it's current root.
        return unifiers.root_of(beta)


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
