# Argo
> The no-brainer Python package for experiment management

___

Argo is a Python library for managing experiment runs in a clean and elegant manner.

Core features:
* Dataclass-powered automatic argument parsing 
* Automatic directory creation for different runs

Argo is largely inspired by 
[Hydra](https://hydra.cc/) 
and the `HfArgumentParser` utility from 
[🤗 Transformers](https://github.com/huggingface/transformers).

## Installation
To install Argo, run
```shell script
pip install argo
```

## Getting Started
The simplest use case of Argo is to setup arguments for a script.
Start by defining arguments in a data class:
```python
from dataclasses import dataclass
from argo.dataclass_utils import parser_field

@dataclass
class Arguments:
    name: str = parser_field(help="The user's name.")
    should_greet: bool = parser_field(help="Whether or not I should greet the user")
```

Then, annotate your main function to magically receive an arguments class :
```python
from argo import argo

@argo()
def main(args: Arguments):
    if args.should_greet:
        print(f"Greetings, {args.name}!")
```
Test by running
```shell script
python main.py --name John --should_greet
```
Outputs
```shell script
Greetings, John!
```

That's it!

## Features

TBD

## Contributing

TBD

## License

This project is open-sourced under the MIT license. See [LICENSE](LICENSE) for details