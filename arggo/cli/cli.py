import json
import os
import subprocess
from os.path import join

import jinja2
from interactive_argparse import PyInquirerPrompter, Question, QuestionKind

from arggo.experiment import FinishedExperiment

_DIR = os.path.dirname(os.path.realpath(__file__))


def write_new_file(template_file: str, output_file: str, *args, **kwargs):
    template_loader = jinja2.FileSystemLoader(
        searchpath=os.path.join(_DIR, "../templates")
    )
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_file)
    with open(output_file, "w") as f:
        f.write(template.render(*args, tag="arggo", **kwargs))


def experiment_create(name: str):
    template_file = "experiment_create.jinja"
    output_file = f"{name}.py"
    write_new_file(template_file, output_file, experiment_name=name)


def experiment_run(name: str):
    # Delegate the actual prompting to the target script's own
    # `InteractiveArgumentParser` (via arggo's `--arggo_interactive` meta-flag)
    # instead of re-building questions for it here.
    executable = "python"
    command = f"{name}.py"
    subprocess.run([executable, command, "--arggo_interactive"])


def _validate_parameters_file(file_path: str, experiment_name: str):
    with open(file_path) as f:
        parameters = json.load(f)
        metaparams = dict(parameters["__arggo"])
        script = metaparams.get("script", None)
        if script is None:
            return False

        return script.split("/")[-1].replace(".py", "") == experiment_name.replace(
            ".py", ""
        )


def _is_experiment_subfolder(path: str, experiment_name: str):
    parameters_file_path = join(path, "parameters.json")
    return os.path.isfile(parameters_file_path) and _validate_parameters_file(
        parameters_file_path, experiment_name
    )


def _lookup_experiments(base_dir: str, experiment_name: str):
    """
    A recursive method to look up directories which contain previously run experiments.
    :param base_dir: The base (root) dir to lookup from
    :param experiment_name: The experiment name to look for
    :return:
    """
    found_directories = []
    if _is_experiment_subfolder(base_dir, experiment_name):
        found_directories.append(base_dir)

    sub_folders_with_paths = [f.path for f in os.scandir(base_dir) if f.is_dir()]
    for sub_folder in sub_folders_with_paths:
        found_directories += _lookup_experiments(sub_folder, experiment_name)
    return found_directories


def experiment_reproduce(name: str, base_dir: str):
    found_experiments = sorted(_lookup_experiments(base_dir, name))
    if len(found_experiments) == 0:
        print("No experiments found to reproduce")
        return
    question = Question(
        name="experiment_path",
        message="Found these experiments. Select one to reproduce:",
        kind=QuestionKind.SINGLE_CHOICE,
        choices=found_experiments,
    )
    answers = PyInquirerPrompter()([question])
    experiment_path = answers["experiment_path"]
    experiment = FinishedExperiment(experiment_path)
    experiment.reproduce()
