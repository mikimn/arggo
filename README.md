# :ship: Arggo
![Coverage](docs/assets/coverage.svg)
![Build Status](https://github.com/mikimn/arggo/actions/workflows/python-package.yml/badge.svg)
![PyPI version](https://badge.fury.io/py/arggo.svg)
> The no-brainer Python package for experiment management

:warning: This library is still in early development. We welcome contributors and early feedback :construction:
___

:ship: Arggo is a Python library for managing experiment runs in a clean and elegant manner.

Core features:
* :bar_chart: Dataclass-powered automatic argument parsing
* :football: No more passing `args` around. `arggo.consume` makes it easy for every function to consume argument objects!
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

**Note**: Arggo relies on the first `configure()` it uses to load everything, initialize the work directory and
configure parametes. Future versions will make `consume` automatically find
the appropriate type parameter to inject the arguments object into, and consequently
`configure()` will throw an error when used more than once.

## Contributing

We welcome early adopters and contributors to this project! See the [Contributing](CONTRIBUTING.md) section for details.

## License

This project is open-sourced under the MIT license. See [LICENSE](LICENSE.md) for details.

## Attributions

Icons made by [Freepik](https://www.freepik.com) from [www.flaticon.com](https://www.flaticon.com/)
