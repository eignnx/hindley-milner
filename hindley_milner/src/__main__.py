from hindley_milner.src import check
from hindley_milner.src import parse


def repl():
    checker = check.Checker()

    while True:
        inp = input("==> ")
        ast = parse.parse(inp)
        t = ast.infer_type(checker)
        t = checker.unifiers.get_concrete(t)
        print(t)


if __name__ == '__main__':
    repl()