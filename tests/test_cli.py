from ollama_bench import parse_model_args


def test_parse_model_args_empty() -> None:
    assert parse_model_args(None) == []
    assert parse_model_args([]) == []


def test_parse_model_args_space_separated() -> None:
    assert parse_model_args(["llama3.2 phi4 gemma3:4b"]) == ["llama3.2", "phi4", "gemma3:4b"]


def test_parse_model_args_multiple_values() -> None:
    assert parse_model_args(["llama3.2", "phi4"]) == ["llama3.2", "phi4"]
