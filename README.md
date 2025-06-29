# LLMD Python SDK

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Python SDK for LLMD (LLM Dialogue) format - create, parse, and manipulate conversation files.

## Overview

LLMD is a standardized file format for storing LLM conversations. It combines YAML metadata with SQLite storage for efficient, structured conversation data management.

## Features

- 🔍 **Parse LLMD files**: Read existing conversation files
- ✍️ **Create LLMD files**: Generate new conversation files
- 🔄 **Round-trip compatibility**: Full fidelity read/write operations
- 🐍 **Pythonic API**: Clean, type-safe interface
- 🧪 **Well tested**: Comprehensive test suite
- 📚 **Type hints**: Full mypy support

## Installation

```bash
pip install llmd-python
```

Or with uv:
```bash
uv add llmd-python
```

## Quick Start

### Reading an LLMD file

```python
from llmd_python import parse_file

# Parse an existing LLMD file
conversation = parse_file("conversation.llmd")

# Access metadata
print(f"Title: {conversation['metadata'].get('title', 'Untitled')}")
print(f"Participants: {conversation['metadata']['participants']}")

# Access messages
for message in conversation["messages"]:
    print(f"{message['role']}: {message['content']}")
```

### Creating an LLMD file

```python
from llmd_python import write_file, LLMDConversation

# Create conversation data
conversation: LLMDConversation = {
    "metadata": {
        "version": "0.1",
        "created_at": "2024-01-15T10:30:00Z",
        "participants": ["user", "assistant"],
        "title": "My Conversation"
    },
    "messages": [
        {
            "id": "msg_1",
            "role": "user",
            "content": "Hello, how are you?",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "id": "msg_2",
            "role": "assistant",
            "content": "I'm doing well, thank you!",
            "timestamp": "2024-01-15T10:30:05Z"
        }
    ]
}

# Write to file
write_file(conversation, "my_conversation.llmd")
```

### Using the class-based API

```python
from llmd_python import LLMDParser, LLMDWriter

# Parse with explicit parser
parser = LLMDParser()
conversation = parser.parse_file("input.llmd")

# Write with explicit writer
writer = LLMDWriter()
writer.write_file(conversation, "output.llmd")
```

## API Reference

### Core Classes

- `LLMDParser`: Parse LLMD files
- `LLMDWriter`: Create LLMD files

### Type Definitions

- `LLMDConversation`: Complete conversation structure
- `LLMDMessage`: Individual message
- `LLMDMetadata`: File metadata
- `LLMDAttachment`: File attachment

### Exceptions

- `LLMDError`: Base exception
- `LLMDParseError`: Parsing errors
- `LLMDValidationError`: Data validation errors
- `LLMDFormatError`: File format errors

## Development

### Setup

```bash
git clone https://github.com/llmd-format/sdk-python.git
cd sdk-python
uv sync
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Type checking
uv run mypy src/

# Code formatting
uv run black src/ tests/
uv run isort src/ tests/

# Linting
uv run flake8 src/ tests/
```

## LLMD Format

LLMD files use a hybrid format:
- **Header**: Magic bytes + metadata pointers
- **YAML section**: Human-readable metadata
- **SQLite section**: Structured conversation data

For complete format specification, see the [LLMD Format Documentation](https://github.com/llmd-format/spec).

## Related Projects

- [LLMD Format Specification](https://github.com/llmd-format/spec)
- [JavaScript SDK](https://github.com/llmd-format/sdk-js)
- [CLI Tools](https://github.com/llmd-format/tools-cli)

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.