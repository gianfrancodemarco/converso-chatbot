from typing import TypedDict

import pytest
from langgraph.graph import StateGraph

from converso.helpers import HtmlProcessor, StateGraphDrawer


class DummyAgentState(TypedDict):
    pass


class DummyStateGraph(StateGraph):
    def __init__(self):
        super().__init__(DummyAgentState)
        self.add_node("start", lambda x: None)
        self.add_node("end", lambda x: None)
        self.add_edge("start", "end")
        self.add_conditional_edges(
            "start",
            lambda x: "end",
            {
                "form": "end"
            }
        )
        self.set_entry_point("start")


class TestHelpers:

    def test_draw_converso_graph(self):
        StateGraphDrawer().draw(DummyStateGraph())
        assert True

    def test_clear_html(self):
        html = """
        <script>
        alert('Hello');
        </script>
        <style>
        h1 {color: blue;}
        </style>
        <html><body><h1>Title</h1><p>Paragraph</p></body></html>
        """
        expected_output = "Title\nParagraph"
        result = HtmlProcessor.clear_html(html)
        assert result == expected_output, "HTML was not cleared correctly"
