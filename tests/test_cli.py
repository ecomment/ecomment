from ecomment.cli import read_program
from ecomment.convert import markup_to_json

import contextlib
import io


def test_read_inline():
    cli_args = "read tests/example-files/inline.py".split()[1:]

    string_io = io.StringIO()
    with contextlib.redirect_stdout(string_io):
        read_program(cli_args)

    inline_example_markup = string_io.getvalue()
    markup_to_json(inline_example_markup)
    # TODO: Assert that the results are what we expect, rather than just fail
    # if they are completely mis-formatted.
