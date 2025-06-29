#!/usr/bin/env python3
"""Create a sample LLMC file using the Python SDK."""

from datetime import datetime
from llmc_python import write_file, LLMCConversation

def create_sample_conversation():
    """Create a sample conversation and save it as LLMC file."""
    
    # Create conversation data
    conversation: LLMCConversation = {
        "metadata": {
            "version": "0.1",
            "created_at": datetime.now().isoformat() + "Z",
            "participants": ["user", "assistant"],
            "title": "Python SDK Demo Conversation",
            "description": "A sample conversation created with the LLMC Python SDK",
            "tags": ["demo", "python", "sdk"],
            "language": "en",
            "model_info": {
                "name": "gpt-4",
                "provider": "openai",
                "version": "2024-01-15"
            }
        },
        "messages": [
            {
                "id": "msg_001",
                "role": "user",
                "content": "Hello! Can you help me understand the LLMC format?",
                "timestamp": "2024-01-15T10:30:00Z"
            },
            {
                "id": "msg_002",
                "role": "assistant", 
                "content": "Of course! LLMC (LLM Dialogue) is a standardized file format for storing conversations with language models. It combines YAML metadata with SQLite storage for efficient data management.",
                "timestamp": "2024-01-15T10:30:05Z"
            },
            {
                "id": "msg_003",
                "role": "user",
                "content": "That sounds interesting! What are the main benefits of using LLMC?",
                "timestamp": "2024-01-15T10:30:10Z"
            },
            {
                "id": "msg_004",
                "role": "assistant",
                "content": "The main benefits include:\n\n1. **Standardization**: Consistent format across different tools and platforms\n2. **Efficiency**: SQLite provides fast querying and compact storage\n3. **Metadata**: Rich YAML headers for conversation context\n4. **Portability**: Single file contains everything needed\n5. **Extensibility**: Support for attachments and custom metadata\n\nThis makes it perfect for archiving, sharing, and analyzing LLM conversations!",
                "timestamp": "2024-01-15T10:30:15Z"
            },
            {
                "id": "msg_005",
                "role": "user",
                "content": "Excellent! How do I get started with the Python SDK?",
                "timestamp": "2024-01-15T10:30:20Z"
            },
            {
                "id": "msg_006",
                "role": "assistant",
                "content": "Getting started is easy! Here's a quick example:\n\n```python\nfrom llmc_python import parse_file, write_file\n\n# Read an existing LLMC file\nconversation = parse_file('my_chat.llmc')\n\n# Access the data\nprint(conversation['metadata']['title'])\nfor msg in conversation['messages']:\n    print(f\"{msg['role']}: {msg['content']}\")\n\n# Create and save a new conversation\nwrite_file(new_conversation, 'output.llmc')\n```\n\nThe SDK handles all the format details for you!",
                "timestamp": "2024-01-15T10:30:25Z"
            }
        ]
    }
    
    # Write to file
    output_file = "examples/python-sdk-demo.llmc"
    write_file(conversation, output_file)
    
    print(f"✅ Created sample LLMC file: {output_file}")
    print(f"📊 Conversation contains {len(conversation['messages'])} messages")
    print(f"👥 Participants: {', '.join(conversation['metadata']['participants'])}")
    print(f"🏷️  Tags: {', '.join(conversation['metadata']['tags'])}")
    
    return output_file

if __name__ == "__main__":
    create_sample_conversation()
