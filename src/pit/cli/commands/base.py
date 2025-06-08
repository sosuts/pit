from abc import ABCMeta, abstractmethod


class AbstractCommand(metaclass=ABCMeta):
    @abstractmethod
    def add_arguments(self, parser):
        raise NotImplementedError

    @abstractmethod
    def execute(self, args):
        raise NotImplementedError
