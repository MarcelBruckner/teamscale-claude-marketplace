#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

server_dir = Path(__file__).resolve().parent / "server"

subprocess.run(["./generate-client.sh"], cwd=server_dir, check=True)
subprocess.run(
    ["uv", "run", "--directory", str(server_dir), "python", "server.py"],
    cwd=server_dir,
    check=True,
)
