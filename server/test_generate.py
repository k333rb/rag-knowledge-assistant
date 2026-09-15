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


@patch("generate.llm")
@patch("generate.vectorstore")
def test_returns_answer_and_sources_when_answer_found(mock_vectorstore, mock_llm):
    # Sets up fake retrieved chunks
    mock_vectorstore.similarity_search.return_value = [
        make_fake_doc("You can set the default to None.",
                      "docs/query-params.md")
    ]

    # Sets up a fake LLM response, plain string form
    mock_response = MagicMock()
    mock_response.content = "You can make it optional by setting the default to None."
    mock_llm.invoke.return_value = mock_response

    result = answer_question("How do I make a query parameter optional?")

    assert "None" in result["answer"]
    assert result["sources"] == ["docs/query-params.md"]


@patch("generate.llm")
@patch("generate.vectorstore")
def test_hides_sources_when_answer_not_found(mock_vectorstore, mock_llm):
    mock_vectorstore.similarity_search.return_value = [
        make_fake_doc("Unrelated content about query parameters.",
                      "docs/query-params.md")
    ]

    mock_response = MagicMock()
    mock_response.content = "I don't have enough information to answer that."
    mock_llm.invoke.return_value = mock_response

    result = answer_question("How do I deploy to AWS?")

    # This is the exact bug you caught and fixed, worth locking in permanently
    assert result["sources"] == []


@patch("generate.llm")
@patch("generate.vectorstore")
def test_extracts_text_from_list_response_format(mock_vectorstore, mock_llm):
    mock_vectorstore.similarity_search.return_value = [
        make_fake_doc("Some content.", "docs/first-steps.md")
    ]

    # Simulates the newer SDK response shape, a list of content blocks
    # rather than a plain string, this is the exact bug encountered earlier
    mock_response = MagicMock()
    mock_response.content = [
        {"type": "text", "text": "This is the real answer.",
            "extras": {"signature": "abc123"}}
    ]
    mock_llm.invoke.return_value = mock_response

    result = answer_question("Some question")

    assert result["answer"] == "This is the real answer."
