"""LLMC file writer implementation."""

import json
import sqlite3
import struct
import tempfile
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Union

import yaml

from .types import (
    LLMC_MAGIC,
    LLMC_VERSION,
    LLMC_FORMAT_VERSION,
    SQLITE_APPLICATION_ID,
    LLMCConversation,
    LLMCFormatError,
    LLMCValidationError,
)

__all__ = ["LLMCWriter"]


class LLMCWriter:
    """Writer for LLMC files."""

    def __init__(self) -> None:
        """Initialize the writer."""
        pass

    def write_file(self, conversation: LLMCConversation, file_path: Union[str, Path]) -> None:
        """Write conversation data to an LLMC file.
        
        Args:
            conversation: Conversation data to write
            file_path: Output file path
            
        Raises:
            LLMCValidationError: If conversation data is invalid
            LLMCFormatError: If writing fails
        """
        try:
            with open(file_path, "wb") as f:
                self.write_stream(conversation, f)
        except (OSError, IOError) as e:
            raise LLMCFormatError(f"Failed to write file {file_path}: {e}") from e

    def write_stream(self, conversation: LLMCConversation, stream: BinaryIO) -> None:
        """Write conversation data to a binary stream.
        
        Args:
            conversation: Conversation data to write
            stream: Binary stream to write to
            
        Raises:
            LLMCValidationError: If conversation data is invalid
            LLMCFormatError: If writing fails
        """
        try:
            # Validate conversation data
            self._validate_conversation(conversation)
            
            # Generate YAML metadata
            yaml_data = self._generate_yaml(conversation["metadata"])
            yaml_bytes = yaml_data.encode("utf-8")
            
            # Generate SQLite database
            sqlite_data = self._generate_sqlite(conversation)
            
            # Calculate offsets
            header_size = 32  # According to LLMC specification: 32-byte header
            sqlite_offset = header_size + len(yaml_bytes)
            
            # Write header
            self._write_header(stream, len(yaml_bytes), sqlite_offset)
            
            # Write YAML section
            stream.write(yaml_bytes)
            
            # Write SQLite section
            stream.write(sqlite_data)
            
        except Exception as e:
            if isinstance(e, (LLMCValidationError, LLMCFormatError)):
                raise
            raise LLMCFormatError(f"Unexpected error during writing: {e}") from e

    def _validate_conversation(self, conversation: LLMCConversation) -> None:
        """Validate conversation data structure."""
        if not isinstance(conversation, dict):
            raise LLMCValidationError("Conversation must be a dictionary")
        
        if "metadata" not in conversation:
            raise LLMCValidationError("Missing metadata section")
        
        if "messages" not in conversation:
            raise LLMCValidationError("Missing messages section")
        
        # Validate metadata
        metadata = conversation["metadata"]
        required_fields = ["version", "created_at", "participants"]
        for field in required_fields:
            if field not in metadata:
                raise LLMCValidationError(f"Missing required metadata field: {field}")
        
        # Validate messages
        messages = conversation["messages"]
        if not isinstance(messages, list):
            raise LLMCValidationError("Messages must be a list")
        
        for i, message in enumerate(messages):
            if not isinstance(message, dict):
                raise LLMCValidationError(f"Message {i} must be a dictionary")
            
            required_msg_fields = ["id", "role", "content", "timestamp"]
            for field in required_msg_fields:
                if field not in message:
                    raise LLMCValidationError(f"Message {i} missing required field: {field}")

    def _write_header(self, stream: BinaryIO, yaml_length: int, sqlite_offset: int) -> None:
        """Write LLMC file header (32 bytes according to specification)."""
        # Magic header (8 bytes): "LLMC\x01\x00\x00\x00"
        stream.write(LLMC_MAGIC)  # "LLMC" (4 bytes)
        stream.write(struct.pack("<B", LLMC_VERSION))  # Version 1 (1 byte)
        stream.write(b"\x00\x00\x00")  # Reserved (3 bytes)

        # Format version (4 bytes)
        stream.write(struct.pack("<I", LLMC_FORMAT_VERSION))

        # YAML length (4 bytes)
        stream.write(struct.pack("<I", yaml_length))

        # SQLite offset (8 bytes)
        stream.write(struct.pack("<Q", sqlite_offset))

        # Encryption flags (1 byte) - no encryption in v0.1
        stream.write(b"\x00")

        # Reserved (7 bytes) - all zeros
        stream.write(b"\x00\x00\x00\x00\x00\x00\x00")

    def _generate_yaml(self, metadata: dict) -> str:
        """Generate YAML metadata section."""
        try:
            return yaml.dump(
                metadata,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        except yaml.YAMLError as e:
            raise LLMCFormatError(f"Failed to generate YAML: {e}") from e

    def _generate_sqlite(self, conversation: LLMCConversation) -> bytes:
        """Generate SQLite database section."""
        # Create temporary database
        with tempfile.NamedTemporaryFile() as tmp_file:
            conn = sqlite3.connect(tmp_file.name)
            
            try:
                # Set application ID
                conn.execute(f"PRAGMA application_id = {SQLITE_APPLICATION_ID};")
                
                # Create schema
                self._create_schema(conn)
                
                # Insert data
                self._insert_messages(conn, conversation["messages"])
                
                if "attachments" in conversation:
                    self._insert_attachments(conn, conversation["attachments"])
                
                # Commit changes
                conn.commit()
                
                # Read database file
                conn.close()
                with open(tmp_file.name, "rb") as f:
                    return f.read()
                    
            except sqlite3.Error as e:
                raise LLMCFormatError(f"SQLite generation error: {e}") from e
            finally:
                try:
                    conn.close()
                except:
                    pass

    def _create_schema(self, conn: sqlite3.Connection) -> None:
        """Create SQLite database schema."""
        # Messages table
        conn.execute("""
            CREATE TABLE messages (
                id TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                parent_id TEXT,
                attachments TEXT,
                metadata TEXT
            );
        """)
        
        # Attachments table
        conn.execute("""
            CREATE TABLE attachments (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                content_type TEXT NOT NULL,
                size INTEGER NOT NULL,
                data BLOB NOT NULL,
                created_at TEXT,
                metadata TEXT
            );
        """)
        
        # Create indexes
        conn.execute("CREATE INDEX idx_messages_timestamp ON messages(timestamp);")
        conn.execute("CREATE INDEX idx_messages_parent_id ON messages(parent_id);")

    def _insert_messages(self, conn: sqlite3.Connection, messages: list) -> None:
        """Insert messages into database."""
        for message in messages:
            attachments_json = None
            if "attachments" in message and message["attachments"]:
                attachments_json = json.dumps(message["attachments"])
            
            metadata_json = None
            if "metadata" in message and message["metadata"]:
                metadata_json = json.dumps(message["metadata"])
            
            conn.execute("""
                INSERT INTO messages (id, role, content, timestamp, parent_id, attachments, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                message["id"],
                message["role"],
                message["content"],
                message["timestamp"],
                message.get("parent_id"),
                attachments_json,
                metadata_json,
            ))

    def _insert_attachments(self, conn: sqlite3.Connection, attachments: list) -> None:
        """Insert attachments into database."""
        for attachment in attachments:
            metadata_json = None
            if "metadata" in attachment and attachment["metadata"]:
                metadata_json = json.dumps(attachment["metadata"])
            
            conn.execute("""
                INSERT INTO attachments (id, filename, content_type, size, data, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                attachment["id"],
                attachment["filename"],
                attachment["content_type"],
                attachment["size"],
                attachment["data"],
                attachment.get("created_at"),
                metadata_json,
            ))
