"""LLMD file parser implementation."""

import sqlite3
import struct
from pathlib import Path
from typing import BinaryIO, Union

import yaml

from .types import (
    LLMD_MAGIC,
    LLMD_VERSION,
    SQLITE_APPLICATION_ID,
    LLMDAttachment,
    LLMDConversation,
    LLMDFormatError,
    LLMDMessage,
    LLMDMetadata,
    LLMDParseError,
)

__all__ = ["LLMDParser"]


class LLMDParser:
    """Parser for LLMD files."""

    def __init__(self) -> None:
        """Initialize the parser."""
        pass

    def parse_file(self, file_path: Union[str, Path]) -> LLMDConversation:
        """Parse an LLMD file from disk.
        
        Args:
            file_path: Path to the LLMD file
            
        Returns:
            Parsed conversation data
            
        Raises:
            LLMDParseError: If parsing fails
            LLMDFormatError: If file format is invalid
        """
        try:
            with open(file_path, "rb") as f:
                return self.parse_stream(f)
        except (OSError, IOError) as e:
            raise LLMDParseError(f"Failed to read file {file_path}: {e}") from e

    def parse_stream(self, stream: BinaryIO) -> LLMDConversation:
        """Parse an LLMD file from a binary stream.
        
        Args:
            stream: Binary stream containing LLMD data
            
        Returns:
            Parsed conversation data
            
        Raises:
            LLMDParseError: If parsing fails
            LLMDFormatError: If file format is invalid
        """
        try:
            # Read and validate header
            header = self._read_header(stream)
            
            # Read YAML metadata
            yaml_data = self._read_yaml_section(stream, header["yaml_length"])
            metadata = self._parse_metadata(yaml_data)
            
            # Read SQLite data
            stream.seek(header["sqlite_offset"])
            sqlite_data = stream.read()
            
            # Parse SQLite database
            messages, attachments = self._parse_sqlite_data(sqlite_data)
            
            # Construct conversation
            conversation: LLMDConversation = {
                "metadata": metadata,
                "messages": messages,
            }
            
            if attachments:
                conversation["attachments"] = attachments
                
            return conversation
            
        except Exception as e:
            if isinstance(e, (LLMDParseError, LLMDFormatError)):
                raise
            raise LLMDParseError(f"Unexpected error during parsing: {e}") from e

    def _read_header(self, stream: BinaryIO) -> dict:
        """Read and validate LLMD file header."""
        # Read magic bytes
        magic = stream.read(4)
        if magic != LLMD_MAGIC:
            raise LLMDFormatError(f"Invalid magic bytes: {magic!r}")
        
        # Read version
        version = struct.unpack("<B", stream.read(1))[0]
        if version != LLMD_VERSION:
            raise LLMDFormatError(f"Unsupported version: {version}")
        
        # Skip reserved bytes
        stream.read(3)
        
        # Read format version
        format_version = struct.unpack("<I", stream.read(4))[0]
        if format_version != 1:
            raise LLMDFormatError(f"Unsupported format version: {format_version}")
        
        # Read YAML length
        yaml_length = struct.unpack("<I", stream.read(4))[0]
        
        # Read SQLite offset
        sqlite_offset = struct.unpack("<Q", stream.read(8))[0]
        
        return {
            "version": version,
            "format_version": format_version,
            "yaml_length": yaml_length,
            "sqlite_offset": sqlite_offset,
        }

    def _read_yaml_section(self, stream: BinaryIO, yaml_length: int) -> str:
        """Read YAML section from stream."""
        yaml_data = stream.read(yaml_length)
        if len(yaml_data) != yaml_length:
            raise LLMDFormatError("Incomplete YAML section")

        try:
            # Handle potential null bytes at the beginning (JavaScript SDK compatibility)
            yaml_text = yaml_data.decode("utf-8")
            # Strip null bytes and whitespace from the beginning
            yaml_text = yaml_text.lstrip('\x00').strip()
            return yaml_text
        except UnicodeDecodeError as e:
            raise LLMDFormatError(f"Invalid UTF-8 in YAML section: {e}") from e

    def _parse_metadata(self, yaml_data: str) -> LLMDMetadata:
        """Parse YAML metadata."""
        try:
            data = yaml.safe_load(yaml_data)
            if not isinstance(data, dict):
                raise LLMDFormatError("YAML metadata must be a dictionary")

            # Handle different field names for compatibility
            # JavaScript SDK uses 'llmd_version', Python SDK uses 'version'
            if "llmd_version" in data and "version" not in data:
                data["version"] = data.pop("llmd_version")

            # Handle different field names for timestamps
            if "created" in data and "created_at" not in data:
                data["created_at"] = data.pop("created")

            # Handle participants field - JavaScript SDK uses different format
            if "participants" not in data:
                # Try to infer participants from other fields or set default
                data["participants"] = ["user", "assistant"]
            elif isinstance(data["participants"], list) and len(data["participants"]) > 0:
                # JavaScript SDK uses objects with role/name/identifier
                # Convert to simple list of roles for compatibility
                if isinstance(data["participants"][0], dict):
                    roles = []
                    for participant in data["participants"]:
                        if "role" in participant:
                            roles.append(participant["role"])
                    if roles:
                        data["participants"] = roles

            # Validate required fields
            required_fields = ["version", "created_at", "participants"]
            for field in required_fields:
                if field not in data:
                    raise LLMDFormatError(f"Missing required field: {field}")

            return data  # type: ignore

        except yaml.YAMLError as e:
            raise LLMDFormatError(f"Invalid YAML metadata: {e}") from e

    def _parse_sqlite_data(self, sqlite_data: bytes) -> tuple[list[LLMDMessage], list[LLMDAttachment]]:
        """Parse SQLite database section."""
        # Write SQLite data to temporary file
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(sqlite_data)
            tmp_path = tmp_file.name

        try:
            # Connect to SQLite file
            conn = sqlite3.connect(tmp_path)

            # Verify application ID
            cursor = conn.execute("PRAGMA application_id;")
            app_id = cursor.fetchone()[0]
            if app_id != SQLITE_APPLICATION_ID:
                raise LLMDFormatError(f"Invalid SQLite application ID: {app_id:#x}")

            # Parse messages
            messages = self._parse_messages(conn)

            # Parse attachments
            attachments = self._parse_attachments(conn)

            return messages, attachments

        except sqlite3.Error as e:
            raise LLMDFormatError(f"SQLite parsing error: {e}") from e
        finally:
            conn.close()
            os.unlink(tmp_path)

    def _parse_messages(self, conn: sqlite3.Connection) -> list[LLMDMessage]:
        """Parse messages from SQLite database."""
        cursor = conn.execute("""
            SELECT id, role, content, timestamp, parent_id, attachments, metadata
            FROM messages
            ORDER BY timestamp
        """)
        
        messages = []
        for row in cursor:
            message: LLMDMessage = {
                "id": row[0],
                "role": row[1],
                "content": row[2],
                "timestamp": row[3],
            }
            
            if row[4] is not None:
                message["parent_id"] = row[4]
            
            if row[5]:
                # Parse JSON array of attachment IDs
                import json
                message["attachments"] = json.loads(row[5])
            
            if row[6]:
                # Parse JSON metadata
                import json
                message["metadata"] = json.loads(row[6])
            
            messages.append(message)
        
        return messages

    def _parse_attachments(self, conn: sqlite3.Connection) -> list[LLMDAttachment]:
        """Parse attachments from SQLite database."""
        try:
            cursor = conn.execute("""
                SELECT id, filename, content_type, size, data, created_at, metadata
                FROM attachments
            """)
        except sqlite3.OperationalError:
            # Attachments table doesn't exist
            return []
        
        attachments = []
        for row in cursor:
            attachment: LLMDAttachment = {
                "id": row[0],
                "filename": row[1],
                "content_type": row[2],
                "size": row[3],
                "data": row[4],
            }
            
            if row[5]:
                attachment["created_at"] = row[5]
            
            if row[6]:
                import json
                attachment["metadata"] = json.loads(row[6])
            
            attachments.append(attachment)
        
        return attachments
