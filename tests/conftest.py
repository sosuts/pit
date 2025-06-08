import subprocess

try:
    subprocess.run(["git", "--version"], check=True, capture_output=True)
except subprocess.CalledProcessError:
    raise OSError(
        "Git is not installed or not found in the system PATH.\n"
        "Git must be installed to run tests."
    )
