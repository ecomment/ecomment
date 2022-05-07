import json

from ecomment_json import markup_to_json, json_to_markup
from strip_ecomment import strip_file


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
    ecomments, stripped_file = strip_file(example_file, before_context=5, after_context=5, filename="example.py")
    assert stripped_file == stripped_example_file
    print(json.dumps(ecomments, indent=4))
    print(json_to_markup(ecomments))
