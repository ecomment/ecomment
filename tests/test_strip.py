import json

from ecomment.convert import json_to_markup
from ecomment.strip import strip_file


example_file = """
from shapely.ops import Point  # ecomment: This should be imported from `shapely.geometry` instead.


grid = []
for x in range(100):
    for y in range(100):
        grid.append(Point(x, y))
# @ecomment-start
# If you want this grid to be from 0-100, then you'll need to take the
# values from range(101). The range(100) is [0, 1, ..., 99].
# 
# You also might want to wrap this into a function and parameterize the 100.
# @ecomment-end

# Falling points
while True:
    new_grid = []
    for point in grid:
        y = point.y - 0.1
        new_grid.append(Point(point.x, y))

    print_grid(grid)  # print the new grid.
    grid = new_grid
# ecomment:
# This looks like an infinite loop. I don't see a break anywhere.
# 
# Maybe you want to break when the last row of points goes below the horizon?
# 
# Also, the 0.1 looks like something you might want to adjusted. Maybe you should
# pull it out into a `fall_rate` variable or something?
"""

stripped_example_file = """
from shapely.ops import Point


grid = []
for x in range(100):
    for y in range(100):
        grid.append(Point(x, y))

# Falling points
while True:
    new_grid = []
    for point in grid:
        y = point.y - 0.1
        new_grid.append(Point(point.x, y))

    print_grid(grid)  # print the new grid.
    grid = new_grid
"""


def test_strip_file():
    ecomments, stripped_file = strip_file(
        example_file, context=5, filename="example.py"
    )
    assert stripped_file == stripped_example_file
    print(json.dumps(ecomments, indent=4))
    print(json_to_markup({"files": [ecomments]}))


def test_strip_line_numbers():
    """Test that the line number associated with each comment is correct.

    Historically, the line number included lines that were added to the file in
    ecomments further up. But we want the line number in the original file, not
    the file with ecomments added to it. This tests that our line numbers
    associate with the original, un-commented file.
    """
    ecomments, _ = strip_file(example_file, context=5, filename="example.py")
    assert len(ecomments["comments"]) == 3

    sorted_comments = sorted(ecomments["comments"], key=lambda comment: comment["line"])
    assert sorted_comments[0]["line"] == 2
    assert sorted_comments[1]["line"] == 8
    assert sorted_comments[2]["line"] == 18


def test_inline_context():
    """Test that the before and after contexts are correct in the inline case.

    Before, we were indexing into the current 'line' object instead of the
    'lines' object to get the before and after context when processing inline
    comments. That resulted in each "line" of context being only one character.
    """
    ecomments, _ = strip_file(example_file, context=5, filename="example.py")
    inline_comments = [
        comment for comment in ecomments["comments"] if comment["type"] == "inline"
    ]
    assert len(inline_comments) == 1

    assert inline_comments[0]["before_context"] == (
        "\n"
        "from shapely.ops import Point  "
        "# ecomment: This should be imported from `shapely.geometry` instead."
    )
    assert inline_comments[0]["after_context"] == (
        "\n\ngrid = []\nfor x in range(100):\n    for y in range(100):"
    )
