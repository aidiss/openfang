"""Tests for data types."""

from openfang.types import Match, Page, Result


def test_page():
    page = Page(url="https://example.com", title="Example", text="Hello", html="<p>Hello</p>")
    assert page.url == "https://example.com"
    assert page.title == "Example"
    assert page.text == "Hello"
    assert page.html == "<p>Hello</p>"


def test_match():
    match = Match(path="src/main.py", line=42, text="def main():")
    assert match.path == "src/main.py"
    assert match.line == 42
    assert match.text == "def main():"


def test_result_ok():
    result = Result(code=0, stdout="success", stderr="")
    assert result.ok
    assert result.code == 0
    assert result.stdout == "success"


def test_result_error():
    result = Result(code=1, stdout="", stderr="error occurred")
    assert not result.ok
    assert result.code == 1
    assert result.stderr == "error occurred"
