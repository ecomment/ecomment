import argparse
import json
import os
import re
import sys
from json.decoder import JSONDecodeError
from typing import Any


def json_to_markup(json_data: dict[str, Any]):
    markup = ""
    for file in json_data["files"]:
        markup += "FILE_INFO\n\n"
        for key, value in file["file-data"].items():

            # Verify and stringify value.
            assert isinstance(
                value, (str, int, float)
            ), f"File header info should be simple data (i.e. not like a list): key={key}, value={value}"
            value = str(value)
            assert "\n" not in value, f"File header values should have have newlines: key={key}, value={value}"

            # Verify header key
            assert isinstance(key, str), f"File header keys should be strings: key={key}"
            assert "\n" not in value, f"File header values should have have newlines: key={key}, value={value}"
            assert ":" not in key, f"File header keys cannot contain colon (:) characters: key={key}"

            markup += f"{key}: {value}\n"
        markup += "\n"
        markup += "COMMENTS\n\n"
        for comment in file["comments"]:
            markup += "-- START COMMENT --\n"
            markup += f"line: {int(comment['line'])}\n"
            if "format" in comment:
                markup += f"format: {comment['format']}\n"
            markup += "\n"  # Extra line to between comment metadata and context/content.
            if "before-context" in comment:
                assert isinstance(comment["before-context"], str)
                lines = comment["before-context"].split("\n")
                for line in lines[:-1]:
                    markup += f">  {line}\n"
                markup += f">> {lines[-1]}\n"

            # Add the actual comment content.
            assert "content" in comment
            markup += "------------------------------------------------------------------------\n"
            lines = comment["content"].split("\n")
            for line in lines:
                markup += f"  {line}\n"
            markup += "------------------------------------------------------------------------\n"

            # Add the after-context
            if "after-context" in comment:
                assert isinstance(comment["after-context"], str)
                lines = comment["after-context"].split("\n")
                for line in lines:
                    markup += f">  {line}\n"

            markup += "-- END COMMENT --\n\n"
    return markup.strip() + "\n"  # Make sure there is just one new line at the end of the file.


def markup_to_json(markup: str):
    states = {
        "between_files": True,
        "in_file_data": True,
        "in_comments": True,
        "between_files": True,
    }
    json_data = {"files": []}
    state = "between_files"
    lines = markup.split("\n")
    index = 0

    # Use `while` loop instead of `for` loop so we can bump state without
    # processing the new line (for example, when state changes depending on
    # the first character of the line.) One consequence of this is that you must
    # be careful to use `pass` instead of `continue` along with `if...elif` instead
    # of a string of ifs. Only when you want to hit *the same line* next iteration
    # should you use `continue`.
    while True:
        line = lines[index]

        # Skip comment lines. They must start with '#', no space first!
        if line.startswith("#"):
            pass

        elif state == "between_files":
            if line == "FILE_INFO":
                json_data["files"].append({"comments": [], "file-data": {}})
                state = "in_file_data"
            else:
                assert not line.strip()  # Line should be empty.

        elif state == "in_file_data":
            if line.rstrip() == "COMMENTS":
                state = "in_comments"
            elif not line.strip():
                pass
            elif ":" in line:
                match = re.match("(^[^:]+):(.*)$", line)
                assert match is not None
                header_name = match.group(1).strip()
                header_value = match.group(2).strip()
                # There should not be duplicate filenames.
                assert header_name not in json_data["files"][-1]["file-data"]
                json_data["files"][-1]["file-data"][header_name] = header_value
            else:
                raise ValueError(f"Invalid line in the FILE_INFO section: {line}")

        elif state == "in_comments":
            if line == "FILE_INFO":
                state = "in_file_data"
            elif line.strip() == "-- START COMMENT --":
                state = "in_comment_header"
                json_data["files"][-1]["comments"].append({})
            else:
                assert not line.strip(), f"Invalid line in comments: {line}"

        elif state == "in_comment_header":
            if line.startswith(">"):
                state = "in_comment_before_context"
                continue
            elif line.startswith("-"):
                state = "in_comment_content"
            elif line.startswith("line:"):
                assert "line" not in json_data["files"][-1]["comments"][-1]
                json_data["files"][-1]["comments"][-1]["line"] = ":".join(line.split(":")[1:]).strip()
            elif line.startswith("format:"):
                assert "format" not in json_data["files"][-1]["comments"][-1]
                json_data["files"][-1]["comments"][-1]["format"] = ":".join(line.split(":")[1:]).strip()
            elif not line.strip():
                pass
            else:
                raise ValueError(f"Invalid comment_header line: {line}")

        elif state == "in_comment_before_context":
            if line.startswith(">"):
                comment = json_data["files"][-1]["comments"][-1]
                line_data = line[3:]  # Strip off '>  ' or '>> ' from the begining.
                if "before-context" in comment:
                    comment["before-context"] += "\n" + line_data
                else:
                    comment["before-context"] = line_data
            elif line.startswith("-"):
                state = "in_comment_content"
            else:
                raise ValueError(f"Invalid comment_before_context line: {line}")

        elif state == "in_comment_content":
            if line.startswith("-"):
                state = "after_comment_content"
            elif line.startswith("  ") or not line:
                comment = json_data["files"][-1]["comments"][-1]
                line_data = "" if len(line) == 0 else line[2:]  # Strip off '  '.
                if "content" in comment:
                    comment["content"] += "\n" + line_data
                else:
                    comment["content"] = line_data
            else:
                raise ValueError(f"Invalid comment_content line: {line}")

        elif state == "after_comment_content":
            if line.startswith(">"):
                state = "in_comment_after_context"
                continue  # Use this line again on the next iteration.
            elif line.strip() == "-- END COMMENT --":
                state = "in_comments"
            elif not line.strip():
                pass
            else:
                raise ValueError(f"Invalid after_comment_content line: {line}")

        elif state == "in_comment_after_context":
            if line.startswith(">"):
                comment = json_data["files"][-1]["comments"][-1]
                line_data = line[3:]  # Strip off '>  ' or '>> ' from the begining.
                if "after-context" in comment:
                    comment["after-context"] += "\n" + line_data
                else:
                    comment["after-context"] = line_data
            elif line.strip() == "-- END COMMENT --":
                state = "in_comments"
            elif not line.strip():
                pass
            else:
                raise ValueError(f"Unexpected in_comment_after_context line: {line}")

        else:
            raise ValueError(f"Unhandled or invalid parser state: {state}")

        index += 1
        if index == len(lines):
            assert state == "in_comments", f"Ending in unexpected state: {state}"
            break

    return json_data


if __name__ == "__main__":
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

    args = parser.parse_args()

    if args.out_file is not None:
        assert os.path.exists(args.out_file)

    if args.in_file is None:
        in_data = sys.stdin.read()
    else:
        assert os.path.exists(args.in_file), f"Cannot file file at '{args.in_file}'."
        with open(args.in_file, "r") as f:
            in_data = f.read()

    try:
        in_json = json.loads(in_data)
        out_data = json_to_markup(in_json)
    except JSONDecodeError as e:
        out_data = json.dumps(markup_to_json(in_data))

    if args.out_file is None:
        print(out_data)
    else:
        with open(args.out_file, "w") as f:
            f.write(out_data)
