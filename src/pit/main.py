from cleo.application import Application

from pit.commands.init import InitCommand

application = Application()
application.add(InitCommand())

if __name__ == "__main__":
    application.run()
