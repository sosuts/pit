import argparse
import shutil
import zlib
from dataclasses import dataclass
from pathlib import Path

from pit.cli.commands.base import AbstractCommand
from pit.objects.blob import Blob
from pit.objects.tree import Tree


@dataclass
class InitArgs:
    force: bool
    path: str


@dataclass
class AddArgs:
    files: list[str]


class PitCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="pit", description="Pit version control system"
        )
        self.subparsers = self.parser.add_subparsers(title="Commands", dest="command")
        self.commands = {
            # plumb
            "init": InitCommand(),
            "add": AddCommand(),
            "commit": CommitCommand(),
            "hash-object": HashObjectCommand(),
            "cat-file": CatFileCommand(),
        }
        self._register_commands()

    def _register_commands(self):
        for name, cmd in self.commands.items():
            parser = self.subparsers.add_parser(name, help=f"{name} command")
            cmd.add_arguments(parser)

            # コマンドごとにdataclassへ変換して渡すラッパーをセット
            def make_func(cmd):
                def wrapper(args_ns):
                    # サブコマンドごとにdataclassへ変換
                    if name == "init":
                        args = InitArgs(
                            force=args_ns.force,
                            path=args_ns.path,
                        )
                        cmd.execute(args)
                    elif name == "add":
                        args = AddArgs(
                            files=args_ns.files,
                        )
                        cmd.execute(args)
                    else:
                        cmd.execute(args_ns)

                return wrapper

            parser.set_defaults(func=make_func(cmd))

    def run(self):
        args = self.parser.parse_args()
        if hasattr(args, "func"):
            args.func(args)
        else:
            self.parser.print_help()


class InitCommand(AbstractCommand):
    DEFAULT_FILES = ("HEAD", "config", "description")
    DEFAULT_DIRS = ("branches", "hooks", "info", "objects", "refs")

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="If set, it will delete the existing project and create a new one.",
        )
        parser.add_argument(
            "-p",
            "--path",
            type=str,
            nargs="?",
            default=Path.cwd(),
            help="The path to initialize the pit project. Default is current directory.",
        )

    def execute(self, args: InitArgs):
        pit_dir = Path(args.path).resolve() / ".pit"

        if args.force:
            print(f"Deleting existing pit project at {str(pit_dir)}")
            shutil.rmtree(pit_dir, ignore_errors=True)

        if pit_dir.exists():
            print(f"Pit project already exists at {str(pit_dir)}")
            print("Use -f/--force option to overwrite it.")
            return

        for dir_ in self.DEFAULT_DIRS:
            (pit_dir / dir_).mkdir(parents=True)
        for file in self.DEFAULT_FILES:
            (pit_dir / file).touch()
        print(f"Created project at {str(pit_dir)}")


class AddCommand(AbstractCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("files", nargs="+", help="Files to add")

    def execute(self, args: AddArgs):
        for file in args.files:
            tree = Tree.from_directory(file)
            for entry in tree.entries:
                print(entry)
            tree.save()


class CommitCommand(AbstractCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("-m", "--message", required=True, help="Commit message")

    def execute(self, args):
        print(f"Committing with message: {args.message}")


class CatFileCommand(AbstractCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        # linuxのcatコマンドのように複数ファイルを指定できるようにする
        parser.add_argument("pit_object", help="Files to display")
        parser.add_argument(
            "-p", "--pretty", action="store_true", help="Display in pretty format"
        )
        parser.add_argument(
            "-t", "--type", action="store_true", help="Display the type of the object"
        )

    def execute(self, args):
        if args.pretty:
            self._cat_file(args.pit_object)
        elif args.type:
            self._show_type(args.pit_object)
        else:
            print(f"Displaying contents of file: {args.pit_object}")

    def _cat_file(self, pit_object: str):
        pit_object_path = Path(f".pit/objects/{pit_object[0:2]}/{pit_object[2:]}")
        if pit_object_path.exists():
            content = zlib.decompress(pit_object_path.read_bytes())
            print(content.decode("utf-8"))
        else:
            print(f"Object {pit_object} does not exist in the database.")

    def _show_type(self, pit_object: str):
        pit_object_path = Path(f".pit/objects/{pit_object[0:2]}/{pit_object[2:]}")
        with open(pit_object_path, "rb") as f:
            # read the type of the blob
            content = f.read()
            print(content)


class HashObjectCommand(AbstractCommand):
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("file", help="File to hash")
        parser.add_argument(
            "-w",
            "--write",
            action="store_true",
            help="Write the object to the database",
        )

    def execute(self, args):
        print(f"Hashing file: {args.file}")
        if args.write:
            self._main(args.file)
        else:
            print(
                f"Hash for {args.file} would be written to the database, but not actually writing."
            )

    def _main(self, file_path: str):
        with open(file_path, "rb") as f:
            content = f.read()
            blob = Blob(content)
        blob_hash = blob.hash
        Path(f".pit/objects/{blob_hash[0:2]}").mkdir(exist_ok=True, parents=True)
        compressed_content = zlib.compress(content)
        Path(f".pit/objects/{blob_hash[0:2]}/{blob_hash[2:]}").write_bytes(
            compressed_content
        )
        print(blob_hash)
