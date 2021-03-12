from dataclasses import dataclass

from arggo import arggo
from arggo.dataclass_utils import parser_field


@dataclass
class Arguments:
    name: str = parser_field(help="The user's name.")
    should_greet: bool = parser_field(help="Whether or not I should greet the user")


@arggo()
def main(args: Arguments):
    if args.should_greet:
        print(f"Greetings, {args.name}!")


if __name__ == "__main__":
    main()
