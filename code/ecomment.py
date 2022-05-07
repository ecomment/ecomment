"""
Strip ecomments out of a Python file and send them to an ecomment file.
"""
import argparse
import json
import sys
from strip_ecomment import strip_file
from ecomment_json import json_to_markup


CONTEXT_DEFAULT = 5
UNSET_CONTEXT = -1


def read_program(cli_args):
    # Parse the command line arguments.
    parser = argparse.ArgumentParser(prog="ecomment strip")
    parser.add_argument("file", nargs="+")
    parser.add_argument(
        "-b", "--before", type=int, default=UNSET_CONTEXT, help="Number of lines to include before the comment"
    )
    parser.add_argument(
        "-a", "--after", type=int, default=UNSET_CONTEXT, help="Number of lines to include after the comment"
    )
    parser.add_argument(
        "-c",
        "--context",
        type=int,
        default=UNSET_CONTEXT,
        help="Number of lines to include before and after the comment",
    )
    parser.add_argument("-o", "--output", type=str, default=None, help="Output file")
    parser.add_argument("-j", "--json", action="store_true", help="Output JSON")
    parser.add_argument("-s", "--strip", action="store_true", help="Strip the comments out of the files.")
    args = parser.parse_args(cli_args)

    # Deduce the context size to save.
    default_context = args.context if args.context != UNSET_CONTEXT else CONTEXT_DEFAULT
    before_context = args.before if args.before != UNSET_CONTEXT else default_context
    after_context = args.after if args.after != UNSET_CONTEXT else default_context

    # Strip the ecomments from the files.
    ecomments = []
    for file in args.file:
        with open(file, "r") as f:
            ecomments_json, stripped_content = strip_file(f.read(), before_context, after_context, file)
        if args.strip:
            with open(file, "w") as f:
                f.write(stripped_content)
        ecomments.append(ecomments_json)

    # Format ecomments as markdown or JSON text.
    if args.json:
        formatted_output = json.dumps(ecomments, indent=4)
    else:
        markup_ecomments = [json_to_markup(ecomment) for ecomment in ecomments]
        formatted_output = "\n\n".join(markup_ecomments)

    # Write ecomments to file or print to stdout.
    if args.output:
        with open(args.output, "w") as f:
            f.writelines(formatted_output.split("\n"))
    else:
        print(formatted_output)


def load_program(cli_rgs):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("program", help="strip, read, or load/write")
    args = parser.parse_args(sys.argv[1:2])

    assert args.program in ("read", "write")
    if args.program == "read":
        read_program(sys.argv[2:])
    if args.program in ("write"):
        load_program(sys.argv[2:])
