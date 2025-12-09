#!/usr/bin/env python3
"""
Test script to verify mem0ai works with both protobuf 5.x and 6.x
"""
import subprocess
import sys
import os

def run_command(cmd, venv_name):
    """Run command in a virtual environment"""
    print(f"\n{'='*60}")
    print(f"Testing: {venv_name}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✓ SUCCESS: {venv_name}")
        if result.stdout:
            print("STDOUT:", result.stdout[:500])
    else:
        print(f"✗ FAILED: {venv_name}")
        print("STDERR:", result.stderr[:500])

    return result.returncode == 0

def test_protobuf_compatibility():
    """Test mem0ai installation with different protobuf versions"""

    # Test protobuf 5.29.0 (minimum supported)
    venv_5x = "test_protobuf_5x"
    run_command(f"python -m venv {venv_5x} && . {venv_5x}/bin/activate && pip install --quiet protobuf==5.29.0 && pip install --quiet . && python -c 'import mem0; print(\"✓ mem0ai imported successfully with protobuf 5.x\")'", venv_5x)

    # Test protobuf 6.33.0 (latest 6.x)
    venv_6x = "test_protobuf_6x"
    run_command(f"python -m venv {venv_6x} && . {venv_6x}/bin/activate && pip install --quiet protobuf==6.33.0 && pip install --quiet . && python -c 'import mem0; print(\"✓ mem0ai imported successfully with protobuf 6.x\")'", venv_6x)

    # Test with langgraph-api (requires protobuf 6.x)
    venv_langgraph = "test_langgraph"
    run_command(f"python -m venv {venv_langgraph} && . {venv_langgraph}/bin/activate && pip install --quiet langgraph-api==0.5.7 && pip install --quiet . && python -c 'from mem0 import Memory; print(\"✓ mem0ai works with LangGraph!\")'", venv_langgraph)

    # Cleanup
    run_command("rm -rf test_protobuf_5x test_protobuf_6x test_langgraph", "Cleanup")

if __name__ == "__main__":
    print("Testing mem0ai protobuf compatibility...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")

    test_protobuf_compatibility()

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)