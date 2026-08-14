import os
import sys
import argparse


def _resolve_output_dir(argv=None):
    """
    Extrai o diretório de saída dos argumentos do CLI, priorizando --graph,
    depois --memory-dir, depois --out. Retorna None se nenhum for passado.
    """
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--graph")
    p.add_argument("--memory-dir")
    p.add_argument("--out")
    args, _ = p.parse_known_args(argv)

    if args.graph:
        return os.path.dirname(os.path.abspath(args.graph))
    if args.memory_dir:
        return os.path.abspath(args.memory_dir)
    if args.out:
        path = os.path.abspath(args.out)
        _, ext = os.path.splitext(path)
        return os.path.dirname(path) if ext else path
    return None


def _set_graphify_out(argv=None):
    """
    Define GRAPHIFY_OUT antes de qualquer import do graphify.
    --graph explícito tem prioridade mesmo que GRAPHIFY_OUT já esteja setado.
    """
    custom = _resolve_output_dir(argv)
    if custom:
        os.environ["GRAPHIFY_OUT"] = custom
    elif "GRAPHIFY_OUT" not in os.environ:
        os.environ["GRAPHIFY_OUT"] = ".specs/graph"


def main():
    _set_graphify_out(sys.argv[1:])

    import importlib
    _graphify_main = importlib.import_module("graphify.__main__")
    _graphify_extract = importlib.import_module("graphify.extract")
    from graph_spec_design.extractors.custom_rust import extract_rust

    _graphify_extract._DISPATCH['.rs'] = extract_rust
    sys.exit(_graphify_main.main())


if __name__ == "__main__":
    main()
