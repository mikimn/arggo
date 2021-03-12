from dataclasses import dataclass
from enum import Enum

from arggo import arggo
from arggo.dataclass_utils import parser_field, enum_field


class GreetingType(Enum):
    NORMAL = 1
    ENGAGING = 2


@dataclass
class Arguments:
    name: str = parser_field(help="The user's name.")
    should_greet: bool = parser_field(help="Whether or not I should greet the user")
    greeting: str = parser_field(
        help="A list of possible greetings", choices=["Hello", "Greetings", "Regards"]
    )
    type: GreetingType = enum_field(GreetingType, required=True)


@arggo()
def main(args: Arguments):
    print(args)
    if args.should_greet:
        stop = "." if args.type == GreetingType.NORMAL else " :)"
        print(f"{args.greeting}, {args.name}{stop}")


if __name__ == "__main__":
    main()
