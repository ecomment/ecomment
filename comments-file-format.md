# The Comments File Format

There should be a universal code commenting file format that all the IDEs can
read and write, just like diff files. That way someone can review your MR in
their IDE and send you the comments file, which you import into your IDE where
you can see the comments and edit the code right there.

If done right, this could not just be limited to code, but to any text file.
And there could be a garden of applications for reading commented text files
(well, reading text files along with the comments intended for that file in a
separate comments file).

All the file needs to contain is a list of line numbers and comments to go with
them. The applications that use these files are responsible keeping track of
lines that the user adds and bumping the line number for the comments found
after the newly added line. They could allow the user to drag the comments
around as well.

This avoids the complexity and foolhardy-ness of trying to anchor the text of
the comment somewhere based on some snippet of the text of the file. Some files
might not have a unique line among them to anchor too. And when you edit the
anchor you do not want the comment to just disappear. There is an interesting
case for expanding from just a line number and a comment, to a line number, a
character range, and a comment.

Here is the data we can take for each comment:

- A comment (required, obviously)
- A single line number (optional, you should be able to comment on the whole
  file)
  - If a line number, an optional character range.
- A range of line numbers (so you can comment on a block).
- Two (line number, character) tuples for the start/end of a very precise block
  (may be useful for commending JSON files, for example).
- Before/after context (optional)
- Application defined metadata like "resolved"/"unresolved"
- Comment format metadata like "html"/"gitlab-markdown-1.2.3"

Here is what you can put in each comment file:

- A file hash (strongly encouraged!)
- A file name (also strongly encouraged!)
- A git commit hash (strongly encouraged if the file is in a Git repository!)

The comments would be plan text. It would be up to the application if they
wanted to render it as some markup language.

## Use Cases

- Comment on some code in the comfort of your IDE and then share the comments
  with your teammate.
- Edit your code with the comments from the merge request right in your IDE.

## Example

```
HEADER

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
```

