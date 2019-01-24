from hindley_milner.src import env
from hindley_milner.src import syntax, typ

StdEnv = env.Env[syntax.Ident, typ.Type]


def std_env() -> StdEnv:
    T = typ.Var()
    U = typ.Var()

    return env.Env(locals={
        syntax.Ident("true"): typ.Bool,
        syntax.Ident("false"): typ.Bool,
        syntax.Ident("zero"): typ.Fn(typ.Int, typ.Bool),
        syntax.Ident("succ"): typ.Fn(typ.Int, typ.Int),
        syntax.Ident("pred"): typ.Fn(typ.Int, typ.Int),
        syntax.Ident("times"): typ.Fn(typ.Int, typ.Fn(typ.Int, typ.Int)),
        syntax.Ident("pair"): typ.Fn(T, typ.Fn(U, typ.Tuple(T, U))),
    })


