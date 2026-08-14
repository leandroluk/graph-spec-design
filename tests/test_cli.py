import os
import sys
import importlib
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


def _make_graphify_mocks():
    mock_main = mock.MagicMock()
    mock_main.main = mock.MagicMock(return_value=0)
    mock_extract = mock.MagicMock()
    mock_extract._DISPATCH = {}
    mock_extractors_base = mock.MagicMock()

    # Atributos de submodulos via dict
    mods = {
        "graphify": mock.MagicMock(),
        "graphify.__main__": mock_main,
        "graphify.extract": mock_extract,
        "graphify.extractors": mock.MagicMock(),
        "graphify.extractors.base": mock_extractors_base,
    }
    return mods, mock_main


def _apply_mocks(mods):
    for k, v in mods.items():
        sys.modules[k] = v


def _cleanup_mocks(mods):
    for k in mods:
        sys.modules.pop(k, None)
    sys.modules.pop("graph_spec_design.cli", None)
    sys.modules.pop("graph_spec_design.extractors.custom_rust", None)
    sys.modules.pop("graph_spec_design", None)


def test_custom_graph_sets_graphify_out_to_graph_dir():
    """
    --graph /custom/dir/graph.json → GRAPHIFY_OUT == /custom/dir
    Nenhum artefato deve ir para graphify-out/ default.
    """
    mods, _ = _make_graphify_mocks()
    _apply_mocks(mods)

    env_backup = os.environ.pop("GRAPHIFY_OUT", None)
    try:
        import graph_spec_design.cli as cli_module
        importlib.reload(cli_module)

        with mock.patch("sys.argv", ["graph-spec-design", "cluster-only", "/repo/root",
                                     "--graph", "/custom/dir/graph.json"]):
            with mock.patch("sys.exit"):
                cli_module.main()

        expected = os.path.dirname(os.path.abspath("/custom/dir/graph.json"))
        assert os.environ["GRAPHIFY_OUT"] == expected, (
            f"Esperado {expected!r}, obtido {os.environ['GRAPHIFY_OUT']!r}"
        )
        assert os.environ["GRAPHIFY_OUT"] != ".specs/graph"
    finally:
        if env_backup is not None:
            os.environ["GRAPHIFY_OUT"] = env_backup
        else:
            os.environ.pop("GRAPHIFY_OUT", None)
        _cleanup_mocks(mods)


def test_no_graph_flag_uses_default_specs_graph():
    """
    Sem --graph/--memory-dir/--out → GRAPHIFY_OUT == .specs/graph
    """
    mods, _ = _make_graphify_mocks()
    _apply_mocks(mods)

    env_backup = os.environ.pop("GRAPHIFY_OUT", None)
    try:
        import graph_spec_design.cli as cli_module
        importlib.reload(cli_module)

        with mock.patch("sys.argv", ["graph-spec-design", "cluster-only", "/repo/root"]):
            with mock.patch("sys.exit"):
                cli_module.main()

        assert os.environ["GRAPHIFY_OUT"] == ".specs/graph", (
            f"Esperado '.specs/graph', obtido {os.environ['GRAPHIFY_OUT']!r}"
        )
    finally:
        if env_backup is not None:
            os.environ["GRAPHIFY_OUT"] = env_backup
        else:
            os.environ.pop("GRAPHIFY_OUT", None)
        _cleanup_mocks(mods)


def test_explicit_graph_overrides_env():
    """
    --graph explícito tem prioridade mesmo se GRAPHIFY_OUT já estiver setado.
    """
    mods, _ = _make_graphify_mocks()
    _apply_mocks(mods)

    env_backup = os.environ.get("GRAPHIFY_OUT")
    os.environ["GRAPHIFY_OUT"] = "/old/value"
    try:
        import graph_spec_design.cli as cli_module
        importlib.reload(cli_module)

        with mock.patch("sys.argv", ["graph-spec-design", "cluster-only", "/repo/root",
                                     "--graph", "/new/dir/graph.json"]):
            with mock.patch("sys.exit"):
                cli_module.main()

        expected = os.path.dirname(os.path.abspath("/new/dir/graph.json"))
        assert os.environ["GRAPHIFY_OUT"] == expected, (
            f"Esperado {expected!r}, obtido {os.environ['GRAPHIFY_OUT']!r}"
        )
    finally:
        if env_backup is not None:
            os.environ["GRAPHIFY_OUT"] = env_backup
        else:
            os.environ.pop("GRAPHIFY_OUT", None)
        _cleanup_mocks(mods)


def test_memory_dir_flag_sets_graphify_out():
    """
    --memory-dir /custom/mem → GRAPHIFY_OUT == /custom/mem
    """
    mods, _ = _make_graphify_mocks()
    _apply_mocks(mods)

    env_backup = os.environ.pop("GRAPHIFY_OUT", None)
    try:
        import graph_spec_design.cli as cli_module
        importlib.reload(cli_module)

        with mock.patch("sys.argv", ["graph-spec-design", "query", "/repo/root",
                                     "--memory-dir", "/custom/mem"]):
            with mock.patch("sys.exit"):
                cli_module.main()

        expected = os.path.abspath("/custom/mem")
        assert os.environ["GRAPHIFY_OUT"] == expected, (
            f"Esperado {expected!r}, obtido {os.environ['GRAPHIFY_OUT']!r}"
        )
    finally:
        if env_backup is not None:
            os.environ["GRAPHIFY_OUT"] = env_backup
        else:
            os.environ.pop("GRAPHIFY_OUT", None)
        _cleanup_mocks(mods)


def test_no_orphan_graphify_out_dir(tmp_path):
    """
    Teste de regressão: com --graph apontando para um dir customizado,
    nenhum artefato aparece em <path>/graphify-out/.
    Verifica que o diretório graphify-out/ NÃO é criado.
    """
    graphify_out_default = tmp_path / "graphify-out"
    graph_dir = tmp_path / ".specs" / "graph"
    graph_dir.mkdir(parents=True)

    mods, _ = _make_graphify_mocks()
    _apply_mocks(mods)

    env_backup = os.environ.pop("GRAPHIFY_OUT", None)
    try:
        import graph_spec_design.cli as cli_module
        importlib.reload(cli_module)

        graph_file = str(graph_dir / "graph.json")
        with mock.patch("sys.argv", ["graph-spec-design", "cluster-only", str(tmp_path),
                                     "--graph", graph_file]):
            with mock.patch("sys.exit"):
                cli_module.main()

        assert not graphify_out_default.exists(), (
            f"Diretório órfão {graphify_out_default} foi criado quando não deveria!"
        )
        expected = str(graph_dir)
        assert os.environ["GRAPHIFY_OUT"] == expected
    finally:
        if env_backup is not None:
            os.environ["GRAPHIFY_OUT"] = env_backup
        else:
            os.environ.pop("GRAPHIFY_OUT", None)
        _cleanup_mocks(mods)


if __name__ == "__main__":
    import tempfile, pathlib

    tests = [
        test_custom_graph_sets_graphify_out_to_graph_dir,
        test_no_graph_flag_uses_default_specs_graph,
        test_explicit_graph_overrides_env,
        test_memory_dir_flag_sets_graphify_out,
    ]

    for fn in tests:
        print(f"  running {fn.__name__}...")
        fn()
        print(f"  OK {fn.__name__}")

    # test com tmp_path simulado
    print(f"  running test_no_orphan_graphify_out_dir...")
    with tempfile.TemporaryDirectory() as td:
        test_no_orphan_graphify_out_dir(pathlib.Path(td))
    print(f"  OK test_no_orphan_graphify_out_dir")

    print("\nAll tests passed!")
