import argparse


class Command:
    def execute(self, args):
        raise NotImplementedError("Subclasses must implement this method")


class InitCommand(Command):
    def execute(self, args):
        print("Initializing repository...")


class AddCommand(Command):
    def execute(self, args):
        print(f"Adding files: {args.files}")


class CommitCommand(Command):
    def execute(self, args):
        print(f"Committing with message: {args.message}")


class PitCLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="pit", description="Pit version control system"
        )
        self.subparsers = self.parser.add_subparsers(title="Commands", dest="command")

        self.commands = {
            "init": InitCommand(),
            "add": AddCommand(),
            "commit": CommitCommand(),
        }

        self._register_commands()

    def _register_commands(self):
        # init command
        parser_init = self.subparsers.add_parser(
            "init", help="Initialize a new repository"
        )
        parser_init.set_defaults(func=self.commands["init"].execute)

        # add command
        parser_add = self.subparsers.add_parser(
            "add", help="Add file contents to the index"
        )
        parser_add.add_argument("files", nargs="+", help="Files to add")
        parser_add.set_defaults(func=self.commands["add"].execute)

        # commit command
        parser_commit = self.subparsers.add_parser(
            "commit", help="Record changes to the repository"
        )
        parser_commit.add_argument(
            "-m", "--message", required=True, help="Commit message"
        )
        parser_commit.set_defaults(func=self.commands["commit"].execute)

    def run(self):
        args = self.parser.parse_args()
        if args.command:
            args.func(args)
        else:
            self.parser.print_help()
