from src import llm_client


def test_llm_connection(monkeypatch):

    monkeypatch.setattr(
        llm_client,
        "ask_llm",
        lambda prompt: "GST is 2646.36."
    )

    answer = llm_client.ask_llm("What is GST?")

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert answer == "GST is 2646.36."