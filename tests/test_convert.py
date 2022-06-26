from ecomment.convert import json_to_markup, markup_to_json

example_ecomment = """
FILE_INFO

# Here is all the metadata for the comment file as a whole.
filename: test.txt
filehash: 24329wfpoijr3aw90843489
gitcommit: 1230498uij4nq3wfe4frq3k40q39o8uir

COMMENTS

-- START COMMENT --
line: 123
format: plain text

# Give some context preceeding the comment.
>  Context is added like this. You can put as much context in here as you want.
>  But we recommend just a couple lines. Mostly these files will be consumed by
>  some application that shows the comments in the the file, with all the context
>  there is. But text is cheap. So why not make the comment files themselves
>> readable contain a small amount of context?
------------------------------------------------------------------------
  This is a comment. Please read carefully.
  
  You should always put the commented on line(s) in double >>
------------------------------------------------------------------------
>  These are the lines after the comment. Just a couple to make things readable.
>  > Q: Why did the dog catcher always catch the big dogs?
>  > A: Because he got paid by the pound.
>  (See how `>` characters at the begning of the context line does not break anything.

-- END COMMENT --

# This is probably not the best way to do it.

-- START COMMENT -- 
line: 432
format: plain text

>  for year in range(70):
>      for month in range(12):
>          for day in range(30):
>              days_to_live += 1
------------------------------------------------------------------------
  I think there is a more efficient way of doing this.
  
  Also, as you can see, if I put a line like this in the comment
  ----------------------------------------------------------------------
  It looks kind of messy, but it does not break the format because of the
  white space before.
------------------------------------------------------------------------
>  
>  days_left = days_to_live - days_lived
>  print(f"You have {days_left} days left to live."

-- END COMMENT --


-- START COMMENT -- 
line: 433
format: plain text

>          for day in range(30):
>              days_to_live += 1
>  
>  days_left = days_to_live - days_lived
------------------------------------------------------------------------
  Well this is a depressing program.

  It's also depressing that we cannot see these comments in the same
  context, since they are right next to each other that would be kind
  of nice.
------------------------------------------------------------------------
>  print(f"You have {days_left} days left to live."
>  todo = input("What are you going to do?")

-- END COMMENT --
"""


def test_markup_to_json_no_fail():
    json = markup_to_json(example_ecomment)
    assert len(json["files"]) == 1
    file = json["files"][0]
    assert len(file["comments"]) == 3
    assert file["file_data"]["filename"] == "test.txt"
    assert file["file_data"]["filehash"] == "24329wfpoijr3aw90843489"
    assert file["file_data"]["gitcommit"] == "1230498uij4nq3wfe4frq3k40q39o8uir"
    assert (
        file["comments"][-1]["content"]
        == """
Well this is a depressing program.

It's also depressing that we cannot see these comments in the same
context, since they are right next to each other that would be kind
of nice.
""".strip()
    )


def test_markup_to_json_and_back():
    first_json = markup_to_json(example_ecomment)
    markup = json_to_markup(first_json)
    second_json = markup_to_json(markup)
    assert first_json == second_json
