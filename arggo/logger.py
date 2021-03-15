import sys


class _Logger(object):
    def __init__(self, output_file, write_mode="a"):
        self.terminal = sys.stdout
        assert write_mode in {"w", "a"}
        self.log = open(output_file, write_mode)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass

    def original_stdout(self):
        return self.terminal


def bind_logger_to_stdout(output_file):
    sys.stdout = _Logger(output_file)
    return sys.stdout


def bind_logger_to_stderr(output_file):
    # Not coloring?
    sys.stderr = _Logger(output_file)
    return sys.stderr
