import argparse

from pit.cli.commands import init


def main():
    parser = argparse.ArgumentParser(
        prog="pit",
        description="Manage git-like repositories.",
    )
    subparsers = parser.add_subparsers()

    init_command = subparsers.add_parser("init", help="Initializes a new pit project.")
    init.add_arguments(init_command)
    init_command.set_defaults(handler=init.execute)
    args = parser.parse_args()

    if hasattr(args, "handler"):
        args.handler(args)
    else:
        # 未知のサブコマンドの場合はヘルプを表示
        parser.print_help()
