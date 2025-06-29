"""Type definitions for LLMC format."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict

__all__ = [
    "LLMCMetadata",
    "LLMCMessage", 
    "LLMCAttachment",
    "LLMCConversation",
    "MessageRole",
    "AttachmentType",
]

# Type aliases
MessageRole = Union["user", "assistant", "system", "function"]
AttachmentType = Union["image", "audio", "video", "document", "other"]


class LLMCMetadata(TypedDict):
    """LLMC file metadata stored in YAML header."""
    
    version: str
    created_at: str
    participants: List[str]
    title: NotRequired[str]
    description: NotRequired[str]
    tags: NotRequired[List[str]]
    language: NotRequired[str]
    model_info: NotRequired[Dict[str, Any]]


class LLMCAttachment(TypedDict):
    """Attachment data structure."""
    
    id: str
    filename: str
    content_type: str
    size: int
    data: bytes
    created_at: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class LLMCMessage(TypedDict):
    """Message data structure."""
    
    id: str
    role: MessageRole
    content: str
    timestamp: str
    parent_id: NotRequired[Optional[str]]
    attachments: NotRequired[List[str]]  # List of attachment IDs
    metadata: NotRequired[Dict[str, Any]]


class LLMCConversation(TypedDict):
    """Complete LLMC conversation structure."""
    
    metadata: LLMCMetadata
    messages: List[LLMCMessage]
    attachments: NotRequired[List[LLMCAttachment]]


# Constants
LLMC_MAGIC = b"LLMC"
LLMC_VERSION = 1
LLMC_FORMAT_VERSION = 1
SQLITE_APPLICATION_ID = 0x4C4C4D43  # "LLMC" in hex


class LLMCError(Exception):
    """Base exception for LLMC-related errors."""
    pass


class LLMCParseError(LLMCError):
    """Raised when parsing LLMC file fails."""
    pass


class LLMCValidationError(LLMCError):
    """Raised when LLMC data validation fails."""
    pass


class LLMCFormatError(LLMCError):
    """Raised when LLMC file format is invalid."""
    pass
