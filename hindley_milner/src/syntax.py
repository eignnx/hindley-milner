from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from hindley_milner.src import check
from hindley_milner.src import typ
from hindley_milner.src import utils


class AstNode(ABC):
    def __init__(self):
        self._type = None

    @abstractmethod
    def infer_type(self, checker: check.Checker) -> typ.Type:
        pass

    @property
    def type(self) -> typ.Type:
        """
        Returns the cached type inferred for this ast node. Must be called
        AFTER calling `infer_type` on the instance.
        """
        if self._type is None:
            cls = self.__class__.__name__
            msg = f"The attribute {cls}.type is not initialized until after "\
                  f"calling {cls}.infer_type!"
            raise AttributeError(msg)
        else:
            return self._type


class Value(AstNode, ABC):
    pass


@dataclass(eq=True)
class Ident(Value):
    """
    An identifier.
    x, printf, abstract_singleton_bean
    """
    name: str

    @utils.cache_in_attr("_type")
    def infer_type(self, checker: check.Checker) -> typ.Type:
        return checker.duplicate_type(checker.type_env[self])

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)


@dataclass(eq=True)
class Const(Value):
    """
    A literal.
    1, true, -4.21983, point { x=1, y=2 }
    """
    value: object
    _type: field(init=False)  # `_` ensures no collision with superclass property

    def infer_type(self, checker: check.Checker) -> typ.Type:
        return self.type  # Note: calls superclass property

    def __str__(self):
        return str(self.value)


@dataclass(eq=True)
class Lambda(AstNode):
    """
    lambda param: body
    """
    param: Ident
    body: AstNode

    @utils.cache_in_attr("_type")
    def infer_type(self, checker: check.Checker) -> typ.Type:

        # In a new scope, infer the type of the body.
        # Scoped because `self.param` is valid only inside this scope.
        # Parameter types are non-generic while checking the body.
        with checker.new_scope(), checker.scoped_non_generic() as arg_type:
            checker.type_env[self.param] = arg_type
            body_type = self.body.infer_type(checker)

        # After inferring body's type, arg type might be known.
        arg_type = checker.unifiers.concretize(arg_type)

        return typ.Fn(arg_type, body_type)


@dataclass(eq=True)
class Call(AstNode):
    """
    fn(arg)
    """
    fn: AstNode
    arg: AstNode

    @utils.cache_in_attr("_type")
    def infer_type(self, checker: check.Checker) -> typ.Type:

        # Get best guess as to the type of `self.arg`.
        arg_type = self.arg.infer_type(checker)

        # Set up a function type.
        beta = checker.fresh_var()
        fn_type_joiner = typ.Fn(arg_type, beta)

        # Ensure the `self.fn` refers to a Fn type.
        fn_type = self.fn.infer_type(checker)

        checker.unify(fn_type, fn_type_joiner)

        # In case beta's root was changed in the last unification, get it's
        # current root.
        return checker.unifiers.concretize(beta)


@dataclass(eq=True)
class If(AstNode):
    """
    if pred then yes else no
    """
    pred: AstNode
    yes: AstNode
    no: AstNode

    @utils.cache_in_attr("_type")
    def infer_type(self, checker: check.Checker) -> typ.Type:
        pred_type = self.pred.infer_type(checker)
        checker.unify(pred_type, typ.Bool)

        yes_type = self.yes.infer_type(checker)
        no_type = self.no.infer_type(checker)
        checker.unify(yes_type, no_type)

        return checker.unifiers.concretize(yes_type)


@dataclass(eq=True)
class Let(AstNode):
    """
    let left = right in body
    """
    left: Ident
    right: AstNode
    body: AstNode

    @utils.cache_in_attr("_type")
    def infer_type(self, checker: check.Checker) -> typ.Type:

        # Scope the `left = right` binding.
        with checker.new_scope():

            # First, bind `left` to a fresh type variable. This allows
            # for recursive let statements.
            # Note: `alpha` is only non-generic while inferring `right`. TODO: Why tho?
            with checker.scoped_non_generic() as alpha:
                checker.type_env[self.left] = alpha

                # Next infer the type of `right` using the binding just created.
                right_type = self.right.infer_type(checker)

            # Link the type variable with the inferred type of `right`.
            checker.unify(alpha, right_type)

            # With the environment set up, now the body can be typechecked.
            return self.body.infer_type(checker)
