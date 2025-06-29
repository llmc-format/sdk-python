"""LLMC file parser implementation."""

import sqlite3
import struct
from pathlib import Path
from typing import BinaryIO, Union

import yaml

from .types import (
    LLMC_MAGIC,
    LLMC_VERSION,
    SQLITE_APPLICATION_ID,
    LLMCAttachment,
    LLMCConversation,
    LLMCFormatError,
    LLMCMessage,
    LLMCMetadata,
    LLMCParseError,
)

__all__ = ["LLMCParser"]


class LLMCParser:
    """Parser for LLMC files."""

    def __init__(self) -> None:
        """Initialize the parser."""
        pass

    def parse_file(self, file_path: Union[str, Path]) -> LLMCConversation:
        """Parse an LLMC file from disk.
        
        Args:
            file_path: Path to the LLMC file
            
        Returns:
            Parsed conversation data
            
        Raises:
            LLMCParseError: If parsing fails
            LLMCFormatError: If file format is invalid
        """
        try:
            with open(file_path, "rb") as f:
                return self.parse_stream(f)
        except (OSError, IOError) as e:
            raise LLMCParseError(f"Failed to read file {file_path}: {e}") from e

    def parse_stream(self, stream: BinaryIO) -> LLMCConversation:
        """Parse an LLMC file from a binary stream.
        
        Args:
            stream: Binary stream containing LLMC data
            
        Returns:
            Parsed conversation data
            
        Raises:
            LLMCParseError: If parsing fails
            LLMCFormatError: If file format is invalid
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
            conversation: LLMCConversation = {
                "metadata": metadata,
                "messages": messages,
            }
            
            if attachments:
                conversation["attachments"] = attachments
                
            return conversation
            
        except Exception as e:
            if isinstance(e, (LLMCParseError, LLMCFormatError)):
                raise
            raise LLMCParseError(f"Unexpected error during parsing: {e}") from e

    def _read_header(self, stream: BinaryIO) -> dict:
        """Read and validate LLMC file header (32 bytes)."""
        # Read magic header (8 bytes): "LLMC\x01\x00\x00\x00"
        magic = stream.read(4)
        if magic != LLMC_MAGIC:
            raise LLMCFormatError(f"Invalid magic bytes: {magic!r}")

        # Read version
        version = struct.unpack("<B", stream.read(1))[0]
        if version != LLMC_VERSION:
            raise LLMCFormatError(f"Unsupported version: {version}")

        # Skip reserved bytes (3 bytes)
        stream.read(3)

        # Read format version (4 bytes)
        format_version = struct.unpack("<I", stream.read(4))[0]
        if format_version != 1:
            raise LLMCFormatError(f"Unsupported format version: {format_version}")

        # Read YAML length (4 bytes)
        yaml_length = struct.unpack("<I", stream.read(4))[0]

        # Read SQLite offset (8 bytes)
        sqlite_offset = struct.unpack("<Q", stream.read(8))[0]

        # Read encryption flags (1 byte) - skip for v0.1
        stream.read(1)

        # Skip reserved bytes (7 bytes)
        stream.read(7)

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
            raise LLMCFormatError("Incomplete YAML section")

        try:
            # Handle potential null bytes at the beginning (JavaScript SDK compatibility)
            yaml_text = yaml_data.decode("utf-8")
            # Strip null bytes and whitespace from the beginning
            yaml_text = yaml_text.lstrip('\x00').strip()
            return yaml_text
        except UnicodeDecodeError as e:
            raise LLMCFormatError(f"Invalid UTF-8 in YAML section: {e}") from e

    def _parse_metadata(self, yaml_data: str) -> LLMCMetadata:
        """Parse YAML metadata."""
        try:
            data = yaml.safe_load(yaml_data)
            if not isinstance(data, dict):
                raise LLMCFormatError("YAML metadata must be a dictionary")



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
                    raise LLMCFormatError(f"Missing required field: {field}")

            return data  # type: ignore

        except yaml.YAMLError as e:
            raise LLMCFormatError(f"Invalid YAML metadata: {e}") from e

    def _parse_sqlite_data(self, sqlite_data: bytes) -> tuple[list[LLMCMessage], list[LLMCAttachment]]:
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
                raise LLMCFormatError(f"Invalid SQLite application ID: {app_id:#x}")

            # Parse messages
            messages = self._parse_messages(conn)

            # Parse attachments
            attachments = self._parse_attachments(conn)

            return messages, attachments

        except sqlite3.Error as e:
            raise LLMCFormatError(f"SQLite parsing error: {e}") from e
        finally:
            conn.close()
            os.unlink(tmp_path)

    def _parse_messages(self, conn: sqlite3.Connection) -> list[LLMCMessage]:
        """Parse messages from SQLite database (supports both schemas)."""
        # Try JavaScript SDK schema first
        try:
            cursor = conn.execute("""
                SELECT m.id, m.role, m.content, m.timestamp, m.parent_id, m.metadata,
                       GROUP_CONCAT(a.id) as attachment_ids
                FROM messages m
                LEFT JOIN attachments a ON a.message_id = m.id
                GROUP BY m.id, m.role, m.content, m.timestamp, m.parent_id, m.metadata
                ORDER BY m.sequence, m.timestamp
            """)

            messages = []
            for row in cursor:
                message: LLMCMessage = {
                    "id": f"msg_{row[0]}",  # Convert to string ID
                    "role": row[1],
                    "content": row[2],
                    "timestamp": row[3],
                }

                if row[4] is not None:
                    message["parent_id"] = f"msg_{row[4]}"

                if row[6]:  # attachment_ids
                    attachment_ids = [f"att_{aid}" for aid in row[6].split(',') if aid]
                    if attachment_ids:
                        message["attachments"] = attachment_ids

                if row[5]:  # metadata
                    import json
                    try:
                        message["metadata"] = json.loads(row[5])
                    except json.JSONDecodeError:
                        pass

                messages.append(message)

            return messages

        except sqlite3.OperationalError:
            # Fall back to Python SDK schema
            try:
                cursor = conn.execute("""
                    SELECT id, role, content, timestamp, parent_id, attachments, metadata
                    FROM messages
                    ORDER BY timestamp
                """)

                messages = []
                for row in cursor:
                    message: LLMCMessage = {
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

            except sqlite3.OperationalError as e:
                raise LLMCFormatError(f"Unsupported database schema: {e}") from e

    def _parse_attachments(self, conn: sqlite3.Connection) -> list[LLMCAttachment]:
        """Parse attachments from SQLite database (supports both schemas)."""
        try:
            # Try JavaScript SDK schema first
            cursor = conn.execute("""
                SELECT id, filename, content_type, size, data, checksum, metadata
                FROM attachments
            """)

            attachments = []
            for row in cursor:
                attachment: LLMCAttachment = {
                    "id": f"att_{row[0]}",  # Convert to string ID
                    "filename": row[1],
                    "content_type": row[2],
                    "size": row[3],
                    "data": row[4],
                }

                if row[6]:  # metadata
                    import json
                    try:
                        attachment["metadata"] = json.loads(row[6])
                    except json.JSONDecodeError:
                        pass

                attachments.append(attachment)

            return attachments

        except sqlite3.OperationalError:
            # Try Python SDK schema
            try:
                cursor = conn.execute("""
                    SELECT id, filename, content_type, size, data, created_at, metadata
                    FROM attachments
                """)

                attachments = []
                for row in cursor:
                    attachment: LLMCAttachment = {
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

            except sqlite3.OperationalError:
                # No attachments table
                return []
