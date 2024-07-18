from unittest.mock import patch

import pytest

from converso.clients.google_search import (GoogleSearchClient,
                                            GoogleSearchClientPayload)


def test_search_financial_data():
    for query in ["bitcoin price", "tesla stock price"]:
        client = GoogleSearchClient()
        payload = GoogleSearchClientPayload(
            query=query, num_expanded_results=2)
        result = client.search(payload)
        assert result.startswith("\n\nFinancial data")


def test_search_info_box():
    for query in ["pizza"]:
        client = GoogleSearchClient()
        payload = GoogleSearchClientPayload(
            query=query, num_expanded_results=2)
        result = client.search(payload)
        assert "Found info box:" in result


def test_search_with_valid_payload_no_result():
    client = GoogleSearchClient()
    payload = GoogleSearchClientPayload(query="pizza", num_expanded_results=2)

    with patch.object(client, "make_request") as mock_make_request:
        mock_make_request.return_value = create_mock_response()

        with pytest.raises(ValueError):
            client.search(payload)

    mock_make_request.assert_called_once_with(
        "https://www.google.com/search", params={"q": "pizza"}
    )


def test_search_with_invalid_payload():
    client = GoogleSearchClient()
    payload = GoogleSearchClientPayload(query="")

    with patch.object(client, "make_request") as mock_make_request:
        with pytest.raises(ValueError):
            client.search(payload)


def create_mock_response():
    class MockResponse:
        def __init__(self):
            self.text = "Mock search result"

    return MockResponse()


if __name__ == "__main__":
    pytest.main()
