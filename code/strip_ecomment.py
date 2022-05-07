"""
A function for stripping ecomment files.
"""
import re
from dataclasses import dataclass
from typing import Optional

# There are obviously edge cases that this does not solve.
# But for now I just want to get it working.
multiline_regex = re.compile(r"\s*#\s*ecomment:[ ]?(.*)")
inline_regex = re.compile(r".*#\s*ecomment:[ ]?(.*)")
inline_regex_striper = re.compile(r".*([\s]?#\s*ecomment:[ ]?.*)")
comment_line_regex = re.compile(r"\s*#[ ]?(.*)")


@dataclass
class Comment:
    before_context: str
    line_number: int
    content: list[str]
    after_context: str
    inline: bool

    def json(self):
        return {
            "before_context": self.before_context,
            "line_number": self.line_number,
            "content": self.content,
            "after_context": self.after_context,
            "inline": self.inline,
        }


def strip_file(
    file_content: str, before_context: int = 5, after_context: int = 5, filename: Optional[str] = None
) -> tuple[dict[str, dict], str]:
    """Strip the ecomments out of a file.

    Parameters
    ----------
    file_content : str
        A string with the contents of the file to strip the ecomments of.
    before_context : int
        The number of lines before the comment to save as context.
    active_context : int
        The number of lines after the comment to save as context.
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
                comments.append(
                    Comment(
                        before_context="\n".join(line[max(index - before_context, 0) : index]),
                        line_number=index,
                        content=[] if content_start.strip() == "" else [content_start],
                        after_context="",
                        inline=False,
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
                        before_context="\n".join(line[max(index - before_context, 0) : index]),
                        line_number=index,
                        content=[content_start],
                        after_context="\n".join(line[index + 1 : index + 1 + after_context]),
                        inline=True,
                    )
                )
                # No need to update the state since we return to the previous state immediately.
                # But we do need to strip the rest of this line out and append to striped_lines.
                striper_match = inline_regex_striper.match(line)
                assert striper_match is not None
                to_strip = striper_match.group(1)
                striped_lines.append(line.removesuffix(to_strip))
                continue

        if state == "in_multiline_comment":
            comment_match = comment_line_regex.match(line)
            if comment_match is None:
                state = "outside_comments"
                comments[-1].after_context = "\n".join(line[index + 1 : index + 1 + after_context])
            else:
                content = comment_match.group(1)
                comments[-1].content.append(content)

    ecomment_file_json = {
        "file-data": {},
        "comments": [comment.json() for comment in comments],
    }

    if filename is not None:
        ecomment_file_json["file-data"]["filename"] = filename

    return ecomment_file_json, "\n".join(striped_lines)