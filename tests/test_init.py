import subprocess

from pit.cli.commands.cli import InitArgs, InitCommand


def test_init_command_creates_expected_files_and_dirs(tmp_path):
    """Test the InitCommand to ensure it creates the expected .pit directory and initializes a git repository."""
    repo_path = tmp_path / "pit-test"
    repo_path.mkdir()

    args = InitArgs(force=False, path=str(repo_path))
    cmd = InitCommand()
    cmd.execute(args)

    pit_dir = repo_path / ".pit"
    assert pit_dir.exists() and pit_dir.is_dir()

    subprocess.run(["git", "init"], cwd=repo_path, check=True)

    git_items = set(p.name for p in (repo_path / ".git").iterdir())
    pit_items = set(p.name for p in pit_dir.iterdir())
    assert pit_items == git_items
