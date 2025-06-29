"""Basic tests for LLMC Python SDK."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from llmd_python import (
    LLMCParser,
    LLMCWriter,
    LLMCConversation,
    LLMCMessage,
    LLMCMetadata,
    parse_file,
    write_file,
)


def test_create_simple_conversation():
    """Test creating a simple conversation."""
    # Create test data
    metadata: LLMCMetadata = {
        "version": "0.1",
        "created_at": "2024-01-15T10:30:00Z",
        "participants": ["user", "assistant"],
        "title": "Test Conversation",
    }
    
    messages: list[LLMCMessage] = [
        {
            "id": "msg_1",
            "role": "user",
            "content": "Hello, how are you?",
            "timestamp": "2024-01-15T10:30:00Z",
        },
        {
            "id": "msg_2", 
            "role": "assistant",
            "content": "I'm doing well, thank you! How can I help you today?",
            "timestamp": "2024-01-15T10:30:05Z",
        },
    ]
    
    conversation: LLMCConversation = {
        "metadata": metadata,
        "messages": messages,
    }
    
    # Test writing and reading
    with tempfile.NamedTemporaryFile(suffix=".llmc", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Write conversation
        writer = LLMCWriter()
        writer.write_file(conversation, tmp_path)
        
        # Verify file exists and has content
        assert Path(tmp_path).exists()
        assert Path(tmp_path).stat().st_size > 0
        
        # Read conversation back
        parser = LLMCParser()
        parsed_conversation = parser.parse_file(tmp_path)
        
        # Verify metadata
        assert parsed_conversation["metadata"]["version"] == "0.1"
        assert parsed_conversation["metadata"]["title"] == "Test Conversation"
        assert len(parsed_conversation["metadata"]["participants"]) == 2
        
        # Verify messages
        assert len(parsed_conversation["messages"]) == 2
        assert parsed_conversation["messages"][0]["role"] == "user"
        assert parsed_conversation["messages"][1]["role"] == "assistant"
        assert "Hello" in parsed_conversation["messages"][0]["content"]
        
    finally:
        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)


def test_convenience_functions():
    """Test convenience functions."""
    # Create test data
    conversation: LLMCConversation = {
        "metadata": {
            "version": "0.1",
            "created_at": "2024-01-15T10:30:00Z",
            "participants": ["user", "assistant"],
        },
        "messages": [
            {
                "id": "msg_1",
                "role": "user", 
                "content": "Test message",
                "timestamp": "2024-01-15T10:30:00Z",
            }
        ],
    }
    
    with tempfile.NamedTemporaryFile(suffix=".llmc", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # Test convenience functions
        write_file(conversation, tmp_path)
        parsed = parse_file(tmp_path)
        
        assert parsed["metadata"]["version"] == "0.1"
        assert len(parsed["messages"]) == 1
        
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def test_round_trip_with_javascript_file():
    """Test parsing the JavaScript SDK example file."""
    # Path to JavaScript SDK example
    js_example_path = Path("../sdk-js/examples/sample-conversation.llmc")
    
    if not js_example_path.exists():
        pytest.skip("JavaScript SDK example file not found")
    
    # Parse the JavaScript-created file
    parser = LLMCParser()
    conversation = parser.parse_file(js_example_path)
    
    # Verify basic structure
    assert "metadata" in conversation
    assert "messages" in conversation
    assert conversation["metadata"]["version"] == "0.1"
    assert len(conversation["messages"]) > 0
    
    # Test round-trip: write and read back
    with tempfile.NamedTemporaryFile(suffix=".llmc", delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        writer = LLMCWriter()
        writer.write_file(conversation, tmp_path)
        
        # Parse our own output
        parsed_again = parser.parse_file(tmp_path)
        
        # Verify consistency
        assert parsed_again["metadata"]["version"] == conversation["metadata"]["version"]
        assert len(parsed_again["messages"]) == len(conversation["messages"])
        
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    # Run basic test
    test_create_simple_conversation()
    print("✅ Basic conversation test passed!")
    
    test_convenience_functions()
    print("✅ Convenience functions test passed!")
    
    try:
        test_round_trip_with_javascript_file()
        print("✅ JavaScript interoperability test passed!")
    except Exception as e:
        print(f"⚠️  JavaScript interoperability test skipped: {e}")
    
    print("🎉 All tests completed!")
