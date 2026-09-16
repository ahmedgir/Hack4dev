from __future__ import annotations

import os
import subprocess
from pathlib import Path


def main() -> int:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        print("LOCALAPPDATA is unavailable; this check is intended for Windows.")
        return 1

    install_dir = Path(local_app_data) / "Programs" / "ASTAP"
    executable = install_dir / "astap_cli.exe"
    if not executable.exists():
        print(f"ASTAP CLI not found: {executable}")
        return 1

    result = subprocess.run(
        [str(executable), "-help"],
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )
    first_line = (result.stdout or result.stderr).splitlines()[0]
    d05_count = len(list(install_dir.glob("d05_*.1476")))
    d20_count = len(list(install_dir.glob("d20_*.1476")))

    print(first_line)
    print(f"Executable: {executable}")
    print(f"D05 files: {d05_count}")
    print(f"D20 files: {d20_count}")

    if d20_count == 0:
        print("ASTAP is callable, but the D20 database is missing.")
        return 2

    print("ASTAP CLI and D20 are available to Python/Codex.")
    print("Note: plate-solving these 650x500 frames is not validated yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
