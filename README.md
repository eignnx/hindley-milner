# hindley-milner
An implementation of the Hindley-Milner type-inference algorithm as described in Luca Cardelli's Basic Polymorphic Typechecker.

## References
See [Bodil Stokke's excellent talk](https://www.youtube.com/watch?v=8coUL8G1lFA) on the subject, and Luca Cardelli's 1988 paper [Basic Polymorphic Typechecking](http://lucacardelli.name/Papers/BasicTypechecking.pdf).

## Example
The top-level package has a [`__main__.py`](https://github.com/eignnx/hindley-milner/blob/master/hindley_milner/__main__.py) file which will run a repl. Type in an ML expression, and the expression's type will be displayed.
```
$ git clone https://github.com/eignnx/hindley-milner.git
$ cd hindley_milner
$ source venv/bin/activate
(venv) $ python -m hindley_milner
==> let fun f x y = times x y in f end
_ : (Int → (Int → Int))
==> null
_ : ((list κ) → Bool)
==> fn x => pair x x
_ : (λ → (λ × λ))
==> if 555 then true else false
Type mismatch: Int != Bool
==> let fun length l = if null l then 0 else succ (length (tail l)) in length end
_ : ((list τ) → Int)
```
