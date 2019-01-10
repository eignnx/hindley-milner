import unicode as uni
import itertools

def fresh_greek_stream():
    yield from uni.GREEK_LOWER
    n = 1
    while True:
        yield from (f"{ch}{n}" for ch in uni.GREEK_LOWER)
        n += 1

greek = fresh_greek_stream()

class Type:
    def __eq__(self, other):
        return type(self) is type(other)

class Var(Type):
    """
    Represents a type variable.
    α, β, γ
    """
    def __init__(self, val=None):
        self.val = val if val is not None else next(greek)

    def __repr__(self):
        cls_name = self.__class__.__name__
        val = repr(self.val)
        return f"{cls_name}({val})"

    def __str__(self):
        return str(self.val)

    def __hash__(self):
        return hash((self.__class__, self.val))

    def __eq__(self, other):
        return super().__eq__(other) and self.val == other.val

class Poly(Type):
    JOIN = None
    SIZE = None
    PARENS = None

    def __init__(self, *vals):
        if self.SIZE is not None and len(vals) > self.SIZE:
            cls_name = self.__class__.__name__
            msg = f"{cls_name} constructor takes at most {self.SIZE} arguments, {len(vals)} given!"
            raise ValueError(msg)
        self.vals = vals

    def __repr__(self):
        if self.SIZE == 0:
            return self.__class__.__name__
        cls_name = self.__class__.__name__
        vals = ", ".join(repr(v) for v in self.vals)
        return f"{cls_name}({vals})"

    def __str__(self):
        if self.SIZE == 0:
            return self.__class__.__name__
        else:
            sep = f" {self.JOIN} " if self.JOIN is not None else ", "
            vals = sep.join(str(v) for v in self.vals)
            lparen, rparen = self.PARENS if self.PARENS is not None else ("(", ")")
            return f"{lparen}{vals}{rparen}"

    def __hash__(self):
        return hash((self.__class__, self.vals))

    def __eq__(self, other):
        return super().__eq__(other) and \
            len(self.vals) == len(other.vals) and \
            all(x == y for x, y in zip(self.vals, other.vals))

class Tuple(Poly):
    JOIN = uni.CROSS

class Fn(Poly):
    JOIN = uni.ARROW
    SIZE = 2

def instance(cls):
    return cls()

@instance
class Int(Poly):
    SIZE = 0

@instance
class Bool(Poly):
    SIZE = 0
