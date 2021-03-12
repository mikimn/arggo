import datetime
import os
from os.path import join


def _working_dir_init(logging_dir: str, _template="%Y-%m-%d/%H-%M-%S"):
    output_dir = join(logging_dir, datetime.datetime.now().strftime(_template))
    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)
    return output_dir
