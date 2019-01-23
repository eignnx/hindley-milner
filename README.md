# hindley-milner
An implementation of the Hindley-Milner type-inference algorithm as described in Luca Cardelli's Basic Polymorphic Typechecker.

## References
See [Bodil Stokke's excellent talk](https://www.youtube.com/watch?v=8coUL8G1lFA) on the subject, and Luca Cardelli's 1988 paper [Basic Polymorphic Typechecking](http://lucacardelli.name/Papers/BasicTypechecking.pdf).

## Example
```python3
import src.check as check
from src.syntax import Const, Ident, Lambda, Call
from src.typ import Int, Var, Bool, Fn

def test_lambda():
    checker = check.Checker()

    id = Lambda(Ident("x"), Ident("x")) # WIP!
    id_type = id.infer_type(checker)

    T = Var()
    equiv_type = Fn(T, T)
    checker.unify(id_type, equiv_type)
    assert True


def test_call():
    checker = check.Checker()

    id = Lambda(Ident("x"), Ident("x"))
    checker.type_env[Ident("id")] = id.infer_type(checker)

    call = Call(Ident("id"), Const(3, Int))
    assert call.infer_type(checker) == Int
```
