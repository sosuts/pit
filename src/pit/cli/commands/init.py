import argparse
import shutil
from pathlib import Path


def add_arguments(parser: argparse.ArgumentParser):
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="If set, it will delete the existing project and create a new one.",
    )


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
