import os
from pathlib import Path

from cleo.application import Application
from cleo.testers.command_tester import CommandTester

from pit.commands.init import InitCommand


# use tempdir fixture
class TestInitCommand:
    def test_nothing(self, tmpdir):
        p = Path(tmpdir)
        os.chdir(p)
        application = Application()
        application.add(InitCommand())

        command = application.find("init")
        command_tester = CommandTester(command)
        command_tester.execute(inputs="-f")
        print(list(p.rglob("*")))
        print(command_tester.io.fetch_output())
