# Tests for the answer generation logic, both the LLM and vector search
# are mocked, so tests never make real API calls or use real quota
from unittest.mock import MagicMock, patch
from generate import answer_question


def make_fake_doc(content, source):
    # Creates a fake retrieved chunk matching the shape LangChain normally returns
    doc = MagicMock()
    doc.page_content = content
    doc.metadata = {"source": source}
    return doc

# Patches the getter functions, not vectorstore/llm directly, since
# those are only created inside answer_question now, not at import


@patch("generate.get_llm")
@patch("generate.get_vectorstore")
def test_returns_answer_and_sources_when_answer_found(mock_get_vectorstore, mock_get_llm):
    mock_vectorstore = MagicMock()
    mock_vectorstore.similarity_search.return_value = [
        make_fake_doc("You can set the default to None.",
                      "docs/query-params.md")
    ]
    mock_get_vectorstore.return_value = mock_vectorstore

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "You can make it optional by setting the default to None."
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    result = answer_question("How do I make a query parameter optional?")

    assert "None" in result["answer"]
    assert result["sources"] == ["docs/query-params.md"]


@patch("generate.get_llm")
@patch("generate.get_vectorstore")
def test_hides_sources_when_answer_not_found(mock_get_vectorstore, mock_get_llm):
    mock_vectorstore = MagicMock()
    mock_vectorstore.similarity_search.return_value = [
        make_fake_doc("Unrelated content about query parameters.",
                      "docs/query-params.md")
    ]
    mock_get_vectorstore.return_value = mock_vectorstore

    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = "I don't have enough information to answer that."
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    result = answer_question("How do I deploy to AWS?")

    # Locks in the real bug caught earlier, sources must stay empty here
    assert result["sources"] == []


@patch("generate.get_llm")
@patch("generate.get_vectorstore")
def test_extracts_text_from_list_response_format(mock_get_vectorstore, mock_get_llm):
    mock_vectorstore = MagicMock()
    mock_vectorstore.similarity_search.return_value = [
        make_fake_doc("Some content.", "docs/first-steps.md")
    ]
    mock_get_vectorstore.return_value = mock_vectorstore

    # Simulates the newer SDK response shape that caused a real bug earlier
    mock_llm = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [
        {"type": "text", "text": "This is the real answer.",
            "extras": {"signature": "abc123"}}
    ]
    mock_llm.invoke.return_value = mock_response
    mock_get_llm.return_value = mock_llm

    result = answer_question("Some question")

    assert result["answer"] == "This is the real answer."
