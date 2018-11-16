from dataclasses import dataclass

class AstNode:
    pass

class Value(AstNode):
    pass

@dataclass
class Ident(Value):
    """
    An identifier.
    x, printf, abstract_singleton_bean
    """
    name: str

    def __str__(self):
        return self.name

@dataclass
class Const(Value):
    """
    A literal.
    1, true, -4.21983, point { x=1, y=2 }
    """
    value: object

    def __str__(self):
        return str(self.value)

@dataclass
class Fn(AstNode):
    arg: Ident
    body: AstNode

@dataclass
class Call(AstNode):
    fn: Fn
    arg: AstNode

@dataclass
class If(AstNode):
    pred: AstNode
    yes: AstNode
    no: AstNode

@dataclass
class Let(AstNode):
    left: Ident
    right: AstNode
    body: AstNode