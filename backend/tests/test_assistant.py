"""Unit tests for ChatSession — no API calls required."""
import pytest

from app.llm.assistant import ChatSession, Message


def test_chat_session_add_message():
    session = ChatSession()
    session.add("user", "Bonjour")
    assert len(session.messages) == 1
    assert session.messages[0].role == "user"
    assert session.messages[0].content == "Bonjour"


def test_chat_session_preserves_order():
    session = ChatSession()
    session.add("user", "Question 1")
    session.add("assistant", "Réponse 1")
    session.add("user", "Question 2")
    assert session.messages[0].role == "user"
    assert session.messages[1].role == "assistant"
    assert session.messages[2].role == "user"


def test_to_api_messages_format():
    session = ChatSession()
    session.add("user", "Test")
    session.add("assistant", "Réponse")
    api_messages = session.to_api_messages()
    assert isinstance(api_messages, list)
    assert len(api_messages) == 2
    assert api_messages[0] == {"role": "user", "content": "Test"}
    assert api_messages[1] == {"role": "assistant", "content": "Réponse"}


def test_empty_session_to_api_messages():
    session = ChatSession()
    assert session.to_api_messages() == []


def test_message_dataclass():
    msg = Message(role="user", content="hello")
    assert msg.role == "user"
    assert msg.content == "hello"
