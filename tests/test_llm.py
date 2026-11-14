
from src.llm_client import ask_llm


def test_llm_connection():
    answer = ask_llm("What is GST?")

    assert isinstance(answer, str)
    assert len(answer) > 0

    print(answer)
