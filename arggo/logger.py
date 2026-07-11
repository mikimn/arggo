import logging
import sys

from arggo._internal.global_store import GlobalStore


class WrapperStream:
    def __init__(self, stream, log):
        self.stream = stream
        self.log = log

    # Proxy
    def __getattr__(self, attr):
        return getattr(self.stream, attr)

    def write(self, message):
        if self.stream is not None:
            self.stream.write(message)
        self.log.write(message)

    def flush(self):
        pass


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
        if not self.gs.get(FileLogger._KEY_BOUND, False):
            self.terminal = sys.stdout
            sys.stdout = WrapperStream(sys.stdout, self.log)
            # sys.stderr = WrapperStream(sys.stderr, self.log)
            for handler in logging.root.handlers:
                if isinstance(handler, logging.StreamHandler):
                    handler.stream = WrapperStream(handler.stream, self.log)
            self.gs.put(FileLogger._KEY_BOUND, True)

    def original_stdout(self):
        return self.terminal
