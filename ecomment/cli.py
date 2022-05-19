"""
Strip ecomments out of a Python file and send them to an ecomment file.
"""
import argparse
import json
from json.decoder import JSONDecodeError
import sys
import os

from . import strip, convert


def read_program(cli_args):
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(prog="ecomment strip")
    parser.add_argument("file", nargs="+")
    parser.add_argument(
        "-c",
        "--context",
        type=int,
        default=5,
        help="Number of lines to include before and after the comment",
    )
    parser.add_argument("-o", "--output", type=str, default=None, help="Output file")
    parser.add_argument("-j", "--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "-s",
        "--strip",
        action="store_true",
        help="Strip the comments out of the files.",
    )
    args = parser.parse_args(cli_args)

    # Strip the ecomments from the files.
    ecomments = []
    for file in args.file:
        with open(file, "r") as f:
            ecomments_json, stripped_content = strip.strip_file(
                f.read(), args.context, file
            )
        if args.strip:
            with open(file, "w") as f:
                f.write(stripped_content)
        ecomments.append(ecomments_json)

    # Format ecomments as markdown or JSON text.
    if args.json:
        formatted_output = json.dumps(ecomments, indent=4)
    else:
        markup_ecomments = [convert.json_to_markup(ecomment) for ecomment in ecomments]
        formatted_output = "\n\n".join(markup_ecomments)

    # Write ecomments to file or print to stdout.
    if args.output:
        with open(args.output, "w") as f:
            f.writelines(formatted_output.split("\n"))
    else:
        print(formatted_output)


def load_program(cli_rgs):
    pass


def convert_program(cli_args):
    parser = argparse.ArgumentParser(
        description="""Convert ecomment markup file and json file formats.

The CLI is partiall inspired from pandoc.

The input file type is infered. The output file type is the opposite of the input type.
That is, `ecomment-json -i input.ecomment` will write the json version of that file to
stdout."""
    )

    parser.add_argument(
        "-i",
        "--in",
        desc="A path to an existing ecomment json or markup file. If not provided it will be read from stdin.",
        dest="in_file",
        type=str,
        nargs="?",
        required=False,
    )

    parser.add_argument(
        "-o",
        "--out",
        dest="out_file",
        desc="A path to write the resulting ecomment json or markup file. If not provided, the result will be written to stdout.",
        type=str,
        nargs="?",
        required=False,
    )

    args = parser.parse_args(cli_args)

    if args.out_file is not None:
        assert os.path.exists(args.out_file)

    if args.in_file is None:
        in_data = sys.stdin.read()
    else:
        assert os.path.exists(args.in_file), f"Cannot file at '{args.in_file}'."
        with open(args.in_file, "r") as f:
            in_data = f.read()

    try:
        in_json = json.loads(in_data)
        out_data = convert.json_to_markup(in_json)
    except JSONDecodeError as e:
        out_data = json.dumps(convert.markup_to_json(in_data))

    if args.out_file is None:
        print(out_data)
    else:
        with open(args.out_file, "w") as f:
            f.write(out_data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="strip, read, or load/write")
    args = parser.parse_args(sys.argv[1:2])

    assert args.program in ("read", "write", "convert")
    if args.program == "read":
        read_program(sys.argv[2:])
    elif args.program == "write":
        load_program(sys.argv[2:])
    elif args.program == "convert":
        convert_program(sys.argv[2:])


if __name__ == "__main__":
    # Run with `python -m ecomment.cli` from the root directory of the repository.
    # See https://stackoverflow.com/questions/72852/how-to-do-relative-imports-in-python
    main()
