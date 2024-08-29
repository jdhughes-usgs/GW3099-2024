import subprocess

cmd = ("ruff", "format", "../")
proc = subprocess.run(cmd)
assert proc.returncode == 0, f"Error running command: {' '.join(cmd)}"

cmd = ("ruff", "check", "../", "--fix")
proc = subprocess.run(cmd)
assert proc.returncode == 0, f"Error running command: {' '.join(cmd)}"
