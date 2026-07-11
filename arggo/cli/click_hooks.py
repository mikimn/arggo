from .cli import *
import click


@click.group()
def main():
    pass


@main.group()
def experiment():
    pass


@experiment.command()
@click.argument("name", nargs=1)
def create(name: str):
    print(f"Creating an experiment named {name}")
    experiment_create(name)


@experiment.command()
@click.argument("name", nargs=1)
@click.option(
    "--logging_dir",
    prompt="The directory in which to look for experiments to reproduce",
    type=str,
    default="logs",
)
def reproduce(name: str, logging_dir: str):
    print(f"Looking for instances of the {name} experiment to reproduce")
    experiment_reproduce(name, logging_dir)


@experiment.command()
@click.argument("name", nargs=1)
def run(name: str):
    print(f"Running experiment {name} interactively...")
    experiment_run(name)
