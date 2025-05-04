import argparse
import shutil
from pathlib import Path

from pit.cli.commands.base import PitCommand


class InitCommand(PitCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="If set, it will delete the existing project and create a new one.",
        )
        parser.add_argument(
            "path",
            type=str,
            nargs="?",
            default=Path.cwd(),
            help="The path to initialize the pit project. Default is current directory.",
        )

    def run(self, args):
        print()
        pit_dir = Path(args.path) / ".pit"

        if args.force:
            print(f"Deleting existing pit project at {str(pit_dir)}")
            shutil.rmtree(pit_dir, ignore_errors=True)

        if pit_dir.exists():
            print(f"Pit project already exists at {str(pit_dir)}")
            return

        for file_type in ("objects", "refs"):
            (pit_dir / file_type).mkdir(parents=True)
        print(f"Created project at {str(pit_dir)}")

    def execute(args):
        pit_dir = Path.cwd() / ".pit"

        if args.force:
            print(f"Deleting existing pit project at {str(pit_dir)}")
            shutil.rmtree(pit_dir, ignore_errors=True)

        if pit_dir.exists():
            print(f"Pit project already exists at {str(pit_dir)}")
            return

        for file_type in ("objects", "refs"):
            (pit_dir / file_type).mkdir(parents=True)
        print(f"Created project at {str(pit_dir)}")
