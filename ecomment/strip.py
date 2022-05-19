"""
A function for stripping ecomment files.
"""
import re
from dataclasses import dataclass
from typing import Literal, Optional, List, Tuple, Dict

# There are obviously edge cases that this does not solve.
# But for now I just want to get it working.
multiline_regex = re.compile(r"\s*#\s*ecomment:[ ]?(.*)")
inline_regex = re.compile(r".*#\s*ecomment:[ ]?(.*)")
inline_regex_striper = re.compile(r"\s*#\s*ecomment:[ ]?.*$")
comment_line_regex = re.compile(r"\s*#[ ]?(.*)")
ecomment_start_regex = re.compile(r"\s*#\s*@ecomment-start")
ecomment_end_regex = re.compile(r"\s*#\s*@ecomment-end")


@dataclass
class Comment:
    before_context: str
    line: int
    content: List[str]
    after_context: str
    type: Literal["inline", "multiline", "start_end"]

    def json(self):
        return {
            "before_context": self.before_context,
            "line": self.line,
            "content": "\n".join(self.content),
            "after_context": self.after_context,
            "type": self.type,
        }


def strip_file(
    file_content: str, context: int = 5, filename: Optional[str] = None
) -> Tuple[Dict[str, dict], str]:
    """Strip the ecomments out of a file.

    Parameters
    ----------
    file_content : str
        A string with the contents of the file to strip the ecomments of.
    context : int
        The number of lines before and after the comment to save as context.
    filename : Optional[str], None
        The name of the file to save in the metadata.

    Returns
    -------
    ecomment_file_json : dict[str, dict]
        A json object containing the ecomments with context and metadata.
    striped_file : str
        The file content striped of the ecomments.
    """
    state = "outside_comments"
    comments = []
    lines = file_content.split("\n")
    striped_lines = []
    for index, line in enumerate(lines):
        if state == "outside_comments":
            match = multiline_regex.match(line)
            if match is not None:
                content_start = match.group(1)
                before_context = "\n".join(lines[max(index - context, 0) : index])
                comments.append(
                    Comment(
                        before_context=before_context,
                        line=index,
                        content=[] if content_start.strip() == "" else [content_start],
                        after_context="",
                        type="multiline",
                    )
                )
                state = "in_multiline_comment"
                # Do not add a line to striped_lines because this line was just a comment.
                continue

            match = inline_regex.match(line)
            if match is not None:
                content_start = match.group(1)
                if content_start.strip() == "":
                    print(f"Inline ecomment without content: {line}.")
                    continue
                comments.append(
                    Comment(
                        before_context="\n".join(line[max(index - context, 0) : index]),
                        line=index,
                        content=[content_start],
                        after_context="\n".join(line[index + 1 : index + 1 + context]),
                        type="inline",
                    )
                )
                # No need to update the state since we return to the previous state immediately.
                # But we do need to strip the rest of this line out and append to striped_lines.
                striper_matches = re.findall(inline_regex_striper, line)
                assert len(striper_matches) == 1
                striped_lines.append(line.removesuffix(striper_matches[0]))
                continue

            match = ecomment_start_regex.match(line)
            if match is not None:
                state = "in_start_end_ecomment"
                comments.append(
                    Comment(
                        before_context="\n".join(
                            lines[max(index - context, 0) : index]
                        ),
                        line=index,
                        content=[],
                        after_context="",
                        type="start_end",
                    )
                )
                continue

            striped_lines.append(line)

        elif state == "in_multiline_comment":
            comment_match = comment_line_regex.match(line)
            if comment_match is None:
                state = "outside_comments"
                comments[-1].after_context = "\n".join(
                    lines[index + 1 : index + 1 + context]
                )
                # TODO: Need to reprocess this line. May contain an inline comment.
                striped_lines.append(line)
            else:
                content = comment_match.group(1)
                comments[-1].content.append(content)

        elif state == "in_start_end_ecomment":
            comment_match = comment_line_regex.match(line)
            if comment_match is None:
                raise NotImplementedError("Unterminated start_end comment")
            content = comment_match.group(1)
            if content.startswith("@ecomment-end"):
                state = "outside_comments"
                comments[-1].after_context = "\n".join(
                    lines[index + 1 : index + 1 + context]
                )
            else:
                comments[-1].content.append(content)

        else:
            raise ValueError(f"Unknown state: {state}")

    ecomment_file_json = {
        "file-data": {},
        "comments": [comment.json() for comment in comments],
    }

    if filename is not None:
        ecomment_file_json["file-data"]["filename"] = filename

    return ecomment_file_json, "\n".join(striped_lines)
