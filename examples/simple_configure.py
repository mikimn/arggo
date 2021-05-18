import os
from dataclasses import dataclass
import sys

sys.path.append(os.getcwd())
sys.path.append("../")
import arggo
from arggo.dataclass_utils import parser_field


@dataclass
class Arguments:
    name: str = parser_field(help="The user's name.")
    should_greet: bool = parser_field(help="Whether or not I should greet the user")


@arggo.configure(parser_argument_index=1, logging_dir="my_logs")
def greet_user(count: int, args: Arguments):
    numeral = {1: "st", 2: "nd", 3: "rd"}
    numeral = numeral[count] if count in numeral else "th"
    if args.should_greet:
        print(f"Greetings for the {count}{numeral} time, {args.name}!")


def main():
    for i in range(4):
        greet_user(i)


if __name__ == "__main__":
    main()
