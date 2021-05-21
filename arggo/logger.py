import sys

from arggo._internal.global_store import GlobalStore


class FileLogger:
    _KEY_BOUND = "file_logger_bound"

    def __init__(self, global_store: GlobalStore, output_file, write_mode="a"):
        self.gs = global_store
        self.terminal = None
        assert write_mode in {"w", "a"}
        self.log = open(output_file, write_mode)

    def bind(
        self,
    ):
        self.terminal = sys.stdout
        if not self.gs.get(FileLogger._KEY_BOUND, False):
            sys.stdout = self
            self.gs.put(FileLogger._KEY_BOUND, True)

    def write(self, message):
        if self.terminal is not None:
            self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass

    def original_stdout(self):
        return self.terminal
