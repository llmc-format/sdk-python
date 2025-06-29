"""Python SDK for LLMC (LLM Dialogue) format.

This package provides tools to create, parse, and manipulate LLMC files,
which are designed to store LLM conversations in a structured format.

Example:
    >>> from llmc_python import LLMCParser, LLMCWriter
    >>>
    >>> # Parse an existing LLMC file
    >>> parser = LLMCParser()
    >>> conversation = parser.parse_file("conversation.llmc")
    >>>
    >>> # Create a new LLMC file
    >>> writer = LLMCWriter()
    >>> writer.write_file(conversation, "output.llmc")
"""

from .parser import LLMCParser
from .writer import LLMCWriter
from .types import (
    LLMCConversation,
    LLMCMessage,
    LLMCMetadata,
    LLMCAttachment,
    LLMCError,
    LLMCParseError,
    LLMCValidationError,
    LLMCFormatError,
    MessageRole,
    AttachmentType,
)

__version__ = "0.1.0"
__author__ = "LLMC Format Team"
__email__ = "team@llmc-format.org"

__all__ = [
    # Main classes
    "LLMCParser",
    "LLMCWriter",

    # Type definitions
    "LLMCConversation",
    "LLMCMessage",
    "LLMCMetadata",
    "LLMCAttachment",
    "MessageRole",
    "AttachmentType",

    # Exceptions
    "LLMCError",
    "LLMCParseError",
    "LLMCValidationError",
    "LLMCFormatError",

    # Metadata
    "__version__",
    "__author__",
    "__email__",
]


def parse_file(file_path: str) -> LLMCConversation:
    """Convenience function to parse an LLMC file.

    Args:
        file_path: Path to the LLMC file

    Returns:
        Parsed conversation data
    """
    parser = LLMCParser()
    return parser.parse_file(file_path)


def write_file(conversation: LLMCConversation, file_path: str) -> None:
    """Convenience function to write an LLMC file.

    Args:
        conversation: Conversation data to write
        file_path: Output file path
    """
    writer = LLMCWriter()
    writer.write_file(conversation, file_path)


def main() -> None:
    """CLI entry point."""
    print("LLMC Python SDK v0.1.0")
    print("Use 'llmc --help' for command line interface")
