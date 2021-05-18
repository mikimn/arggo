import os

from arggo.environment.workdir import DirectoryStrategy


class FakeDirectoryStrategy(DirectoryStrategy):
    def __init__(self) -> None:
        super().__init__()
        self.dir = os.getcwd()

    def makedirs(self, path):
        pass

    def chdir(self, path):
        self.dir = path

    def getcwd(self):
        return self.dir
