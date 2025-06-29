# LLMC Python SDK

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Python SDK for LLMC (LLM Dialogue) format - create, parse, and manipulate conversation files.

## Overview

LLMC is a standardized file format for storing LLM conversations. It combines YAML metadata with SQLite storage for efficient, structured conversation data management.

## Features

- 🔍 **Parse LLMC files**: Read existing conversation files
- ✍️ **Create LLMC files**: Generate new conversation files
- 🔄 **Round-trip compatibility**: Full fidelity read/write operations
- 🐍 **Pythonic API**: Clean, type-safe interface
- 🧪 **Well tested**: Comprehensive test suite
- 📚 **Type hints**: Full mypy support

## Installation

```bash
pip install llmc-python
```

Or with uv:
```bash
uv add llmc-python
```

## Quick Start

### Reading an LLMC file

```python
from llmc_python import parse_file

# Parse an existing LLMC file
conversation = parse_file("conversation.llmc")

# Access metadata
print(f"Title: {conversation['metadata'].get('title', 'Untitled')}")
print(f"Participants: {conversation['metadata']['participants']}")

# Access messages
for message in conversation["messages"]:
    print(f"{message['role']}: {message['content']}")
```

### Creating an LLMC file

```python
from llmc_python import write_file, LLMCConversation

# Create conversation data
conversation: LLMCConversation = {
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
write_file(conversation, "my_conversation.llmc")
```

### Using the class-based API

```python
from llmc_python import LLMCParser, LLMCWriter

# Parse with explicit parser
parser = LLMCParser()
conversation = parser.parse_file("input.llmc")

# Write with explicit writer
writer = LLMCWriter()
writer.write_file(conversation, "output.llmc")
```

## API Reference

### Core Classes

- `LLMCParser`: Parse LLMC files
- `LLMCWriter`: Create LLMC files

### Type Definitions

- `LLMCConversation`: Complete conversation structure
- `LLMCMessage`: Individual message
- `LLMCMetadata`: File metadata
- `LLMCAttachment`: File attachment

### Exceptions

- `LLMCError`: Base exception
- `LLMCParseError`: Parsing errors
- `LLMCValidationError`: Data validation errors
- `LLMCFormatError`: File format errors

## Development

### Setup

```bash
git clone https://github.com/llmc-format/sdk-python.git
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

## LLMC Format

LLMC files use a hybrid format:
- **Header**: Magic bytes + metadata pointers
- **YAML section**: Human-readable metadata
- **SQLite section**: Structured conversation data

For complete format specification, see the [LLMC Format Documentation](https://github.com/llmc-format/spec).

## Related Projects

- [LLMC Format Specification](https://github.com/llmc-format/spec)
- [JavaScript SDK](https://github.com/llmc-format/sdk-js)
- [CLI Tools](https://github.com/llmc-format/tools-cli)

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.