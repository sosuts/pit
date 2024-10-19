from pathlib import Path

from cleo.commands.command import Command
from cleo.helpers import argument, option

from pit.objects import ProjectFileType


class InitCommand(Command):
    name = "init"
    description = "Initializes a new pit project."
    options = [
        option(
            "force",
            "f",
            description="If set, it will delete the existing project and create a new one.",
            flag=True,
        )
    ]

    def handle(self):
        pit_dir = Path.cwd() / ".pit"

        if self.option("force"):
            self.line(f"Deleting existing pit project at {str(pit_dir)}")
            # delete folder even if it is not empty
            import shutil

            shutil.rmtree(pit_dir, ignore_errors=True)

        if pit_dir.exists():
            self.line(f"Pit project already exists at {str(pit_dir)}")
            return

        for file_type in ProjectFileType:
            (pit_dir / file_type).mkdir(parents=True)
        self.line(f"Created project at {str(pit_dir)}")
