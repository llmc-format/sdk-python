#!/usr/bin/env python3
"""Parse and display an LLMD file using the Python SDK."""

import sys
from pathlib import Path
from llmd_python import parse_file, LLMDParseError

def parse_and_display(file_path: str):
    """Parse an LLMD file and display its contents."""
    
    try:
        print(f"🔍 Parsing LLMD file: {file_path}")
        print("=" * 60)
        
        # Parse the file
        conversation = parse_file(file_path)
        
        # Display metadata
        metadata = conversation["metadata"]
        print("📋 METADATA:")
        print(f"  Version: {metadata['version']}")
        print(f"  Created: {metadata['created_at']}")
        print(f"  Title: {metadata.get('title', 'Untitled')}")
        print(f"  Description: {metadata.get('description', 'No description')}")
        print(f"  Participants: {', '.join(metadata['participants'])}")
        
        if 'tags' in metadata:
            print(f"  Tags: {', '.join(metadata['tags'])}")
        
        if 'language' in metadata:
            print(f"  Language: {metadata['language']}")
        
        if 'model_info' in metadata:
            model = metadata['model_info']
            print(f"  Model: {model.get('name', 'Unknown')} ({model.get('provider', 'Unknown')})")
        
        print()
        
        # Display messages
        messages = conversation["messages"]
        print(f"💬 MESSAGES ({len(messages)} total):")
        print("-" * 60)
        
        for i, message in enumerate(messages, 1):
            role_emoji = "👤" if message["role"] == "user" else "🤖"
            print(f"{role_emoji} Message {i} ({message['role']}):")
            print(f"   ID: {message['id']}")
            print(f"   Time: {message['timestamp']}")
            
            # Display content with proper formatting
            content = message['content']
            if len(content) > 200:
                # Truncate long messages
                content = content[:200] + "..."
            
            # Indent content lines
            content_lines = content.split('\n')
            for line in content_lines:
                print(f"   {line}")
            
            if 'parent_id' in message:
                print(f"   Parent: {message['parent_id']}")
            
            if 'attachments' in message:
                print(f"   Attachments: {len(message['attachments'])}")
            
            print()
        
        # Display attachments if any
        if "attachments" in conversation:
            attachments = conversation["attachments"]
            print(f"📎 ATTACHMENTS ({len(attachments)} total):")
            print("-" * 60)
            
            for attachment in attachments:
                print(f"  📄 {attachment['filename']}")
                print(f"     Type: {attachment['content_type']}")
                print(f"     Size: {attachment['size']} bytes")
                print(f"     ID: {attachment['id']}")
                print()
        
        # Summary
        print("📊 SUMMARY:")
        print(f"  Total messages: {len(messages)}")
        print(f"  Total attachments: {len(conversation.get('attachments', []))}")
        
        # Calculate approximate file size
        file_size = Path(file_path).stat().st_size
        print(f"  File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        print("✅ Parsing completed successfully!")
        
    except LLMDParseError as e:
        print(f"❌ Failed to parse LLMD file: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python parse_sample.py <llmd_file>")
        print("Example: python parse_sample.py examples/python-sdk-demo.llmd")
        sys.exit(1)
    
    file_path = sys.argv[1]
    parse_and_display(file_path)

if __name__ == "__main__":
    main()
