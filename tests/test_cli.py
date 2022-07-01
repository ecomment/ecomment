from ecomment.cli import read_program

import contextlib
import io


def test_read_inline():
    cli_args = "read tests/example-files/inline.py".split()[1:]

    string_io = io.StringIO()
    with contextlib.redirect_stdout(string_io):
        read_program(cli_args)

    inline_example_markup = string_io.getvalue()
    with open("tests/example-files/inline.ecomment", "r") as f:
        assert inline_example_markup == f.read()
