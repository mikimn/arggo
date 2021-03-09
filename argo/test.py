from dataclasses import dataclass, asdict

from argo import argo
from argo.dataclass_utils import parser_field


@dataclass
class Arguments:
    arg1: str = parser_field(help='This is help string 1')
    arg2: bool = parser_field(help='This is help string 2')


@argo()
def main(args: Arguments):
    print('arguments:', asdict(args))


if __name__ == '__main__':
    main()
