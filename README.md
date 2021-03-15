# <img src="./docs/assets/ship.png" width="50" /> Arggo
> The no-brainer Python package for experiment management

:warning: This library is still in early development. We welcome contributors and early feedback :construction:
___

Arggo is a Python library for managing experiment runs in a clean and elegant manner.

Core features:
* Dataclass-powered automatic argument parsing
* Automatic directory creation for different runs

Arggo is largely inspired by
[Hydra](https://hydra.cc/) and the `HfArgumentParser` utility from
[🤗 Transformers](https://github.com/huggingface/transformers).

## Table of Contents

* [Installation](#installation)
* [Getting Started](#getting-started)
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
from arggo import arggo

@arggo()
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

## Features

:construction: To-do list:

* [ ] Proof-of-concept for dataclass arguments
* [ ] Automatic working directory management
* [ ] Service integration

## Contributing

We welcome early adopters and contributors to this project! See the [Contributing](CONTRIBUTING.md) section for details.

## License

This project is open-sourced under the MIT license. See [LICENSE](LICENSE.md) for details.

## Attributions

Icons made by [Freepik](https://www.freepik.com) from [www.flaticon.com](https://www.flaticon.com/)
