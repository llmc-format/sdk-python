"""Type definitions for LLMD format."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

if sys.version_info >= (3, 11):
    from typing import NotRequired, TypedDict
else:
    from typing_extensions import NotRequired, TypedDict

__all__ = [
    "LLMDMetadata",
    "LLMDMessage", 
    "LLMDAttachment",
    "LLMDConversation",
    "MessageRole",
    "AttachmentType",
]

# Type aliases
MessageRole = Union["user", "assistant", "system", "function"]
AttachmentType = Union["image", "audio", "video", "document", "other"]


class LLMDMetadata(TypedDict):
    """LLMD file metadata stored in YAML header."""
    
    version: str
    created_at: str
    participants: List[str]
    title: NotRequired[str]
    description: NotRequired[str]
    tags: NotRequired[List[str]]
    language: NotRequired[str]
    model_info: NotRequired[Dict[str, Any]]


class LLMDAttachment(TypedDict):
    """Attachment data structure."""
    
    id: str
    filename: str
    content_type: str
    size: int
    data: bytes
    created_at: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class LLMDMessage(TypedDict):
    """Message data structure."""
    
    id: str
    role: MessageRole
    content: str
    timestamp: str
    parent_id: NotRequired[Optional[str]]
    attachments: NotRequired[List[str]]  # List of attachment IDs
    metadata: NotRequired[Dict[str, Any]]


class LLMDConversation(TypedDict):
    """Complete LLMD conversation structure."""
    
    metadata: LLMDMetadata
    messages: List[LLMDMessage]
    attachments: NotRequired[List[LLMDAttachment]]


# Constants
LLMD_MAGIC = b"LLMD"
LLMD_VERSION = 1
LLMD_FORMAT_VERSION = 1
SQLITE_APPLICATION_ID = 0x4C4C4D44  # "LLMD" in hex


class LLMDError(Exception):
    """Base exception for LLMD-related errors."""
    pass


class LLMDParseError(LLMDError):
    """Raised when parsing LLMD file fails."""
    pass


class LLMDValidationError(LLMDError):
    """Raised when LLMD data validation fails."""
    pass


class LLMDFormatError(LLMDError):
    """Raised when LLMD file format is invalid."""
    pass
