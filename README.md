# :ship: Arggo
![Coverage](docs/assets/coverage.svg)
![Build Status](https://github.com/mikimn/arggo/actions/workflows/python-package.yml/badge.svg)
![PyPI version](https://badge.fury.io/py/arggo.svg)
> The no-brainer Python package for experiment management

:warning: This library is still in early development. We welcome contributors and early feedback :construction:
___

:ship: Arggo is a Python toolkit for managing reproducible runs in a clean and elegant manner.

Core features:
* :bar_chart: Automatic dataclass-powered argument parsing and injection.
* :computer: Powerful CLI for run management and bootstrapping
* :arrows_counterclockwise: Reproducibility - re-run previously saved :ship: Arggo runs with a single command.
* :lock: Isolation - :ship: Arggo creates a new running directory for each run by default.

Upcoming:
* :surfer: Versatility – Arggo is plugin-based, and all behaviors can be controlled for, configured, or disabled.

:ship: Arggo is largely inspired by
[Hydra](https://hydra.cc/) and the `HfArgumentParser` utility from
[🤗 Transformers](https://github.com/huggingface/transformers).

## Table of Contents

* [Installation](#installation)
* [Getting Started](#getting-started)
* [Usage](#usage)
* [Features](#features)

## Installation
To install Arggo, run
```shell script
pip install arggo
```

## Getting Started
The simplest use case of Arggo is to setup arguments for a script.
Start by defining arguments in a data class:
```python
from dataclasses import dataclass
from arggo.dataclass_utils import parser_field

@dataclass
class Arguments:
    name: str = parser_field(help="The user's name.")
    should_greet: bool = parser_field(help="Whether or not I should greet the user")
```

Then, annotate your main function to magically receive an arguments class :

```python
import arggo


@arggo.consume
def main(args: Arguments):
    if args.should_greet:
        print(f"Greetings, {args.name}!")
```
Test by running
```shell script
python main.py --name John --should_greet
```
Outputs
```text
Greetings, John!
```

That's it!

## Usage

### Configuration

You can configure Arggo by using `arggo.configure()` instead, like so:

```python
import arggo


@arggo.configure(
    parser_argument_index=1,
    logging_dir="my_logs"
)
def greet_user(count: int, args: Arguments):
    numeral = {1: "st", 2: "nd", 3: "rd"}
    numeral = numeral[count] if count in numeral else 'th'
    if args.should_greet:
        print(f"Greetings for the {count}{numeral} time, {args.name}!")


def main():
    for i in range(4):
        greet_user(i)


main()
```

Running
```shell script
python main.py --name John
```
Outputs
```text
Greetings for the 0th time, John!
Greetings for the 1st time, John!
Greetings for the 2nd time, John!
Greetings for the 3rd time, John!
```

The `consume` and `configure()` decorators work for any function, and guarantee that the same objects are provided each time.

**Note**: Arggo relies on the first `consume`/`configure()`-decorated call in a process to load everything and
initialize the work directory; calling that same decorated function again (e.g. in a loop, as above) reuses it.
Calling a *different* `consume`/`configure()`-decorated entry point in the same process instead raises
`ArggoAlreadyConfiguredError`, since only one entry point's configuration can be in effect per process.

### Meta-arguments

Arggo attaches meta-arguments to each script, allowing for some extra functionality.
To view all possible meta-arguments, run your script with the `--arggo_help` flag
```shell
python main.py --arggo_help
```

These names are reserved by Arggo and cannot be used as dataclass field names:

* `arggo_help`
* `arggo_interactive`
* `arggo_reproduce`
* `wandb_disable`

If a field collides with one of these, Arggo raises `ArggoReservedError`. Rename the field, or opt out with
`@arggo.configure(override_reserved_arguments=True)` if you're sure the collision is intentional.

#### Interactive Runs

You can provide arguments to a program interactively by supplying the `--arggo_interactive` flag:
```shell
python main.py --arggo_help
```

### Command Line Interface

Arggo powers a CLI for many useful actions. To view more information, run
```shell
arggo-cli --help
```

#### Creating a New Experiment

```shell
arggo-cli experiment create <experiment_name>
```

This command automatically creates a starter file `<experiment_name>.py`

#### Reproducing an Existing Experiment

To reproduce results of a previous experiment run, type
```shell
arggo-cli experiment reproduce <experiment_name>
```

This looks for any experiments in the `logs/` folder, and allows you to interactively choose which one to reproduce.

### Plugins

#### Weights & Biases

If [`wandb`](https://pypi.org/project/wandb/) is installed, Arggo automatically logs each run's parameters to it as
a config dict, and records the run's id/name/url in the saved `parameters.json`. Pass `--wandb_disable` to opt out
for a single run, even with `wandb` installed.

## Development

### Running tests

To run all tests:
```shell
python -m pytest --cov=arggo
```

## Contributing

We welcome early adopters and contributors to this project! See the [Contributing](CONTRIBUTING.md) section for details.

## License

This project is open-sourced under the MIT license. See [LICENSE](LICENSE.md) for details.

## Attributions

Icons made by [Freepik](https://www.freepik.com) from [www.flaticon.com](https://www.flaticon.com/)
