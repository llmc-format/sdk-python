"""Python SDK for LLMD (LLM Dialogue) format.

This package provides tools to create, parse, and manipulate LLMD files,
which are designed to store LLM conversations in a structured format.

Example:
    >>> from llmd_python import LLMDParser, LLMDWriter
    >>>
    >>> # Parse an existing LLMD file
    >>> parser = LLMDParser()
    >>> conversation = parser.parse_file("conversation.llmd")
    >>>
    >>> # Create a new LLMD file
    >>> writer = LLMDWriter()
    >>> writer.write_file(conversation, "output.llmd")
"""

from .parser import LLMDParser
from .writer import LLMDWriter
from .types import (
    LLMDConversation,
    LLMDMessage,
    LLMDMetadata,
    LLMDAttachment,
    LLMDError,
    LLMDParseError,
    LLMDValidationError,
    LLMDFormatError,
    MessageRole,
    AttachmentType,
)

__version__ = "0.1.0"
__author__ = "LLMD Format Team"
__email__ = "team@llmd-format.org"

__all__ = [
    # Main classes
    "LLMDParser",
    "LLMDWriter",

    # Type definitions
    "LLMDConversation",
    "LLMDMessage",
    "LLMDMetadata",
    "LLMDAttachment",
    "MessageRole",
    "AttachmentType",

    # Exceptions
    "LLMDError",
    "LLMDParseError",
    "LLMDValidationError",
    "LLMDFormatError",

    # Metadata
    "__version__",
    "__author__",
    "__email__",
]


def parse_file(file_path: str) -> LLMDConversation:
    """Convenience function to parse an LLMD file.

    Args:
        file_path: Path to the LLMD file

    Returns:
        Parsed conversation data
    """
    parser = LLMDParser()
    return parser.parse_file(file_path)


def write_file(conversation: LLMDConversation, file_path: str) -> None:
    """Convenience function to write an LLMD file.

    Args:
        conversation: Conversation data to write
        file_path: Output file path
    """
    writer = LLMDWriter()
    writer.write_file(conversation, file_path)


def main() -> None:
    """CLI entry point."""
    print("LLMD Python SDK v0.1.0")
    print("Use 'llmd --help' for command line interface")
