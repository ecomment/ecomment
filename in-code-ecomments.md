We want the ecomments in code to

- be very easy to write and read. 
- be easy to parse where possible, but that is not a priority in competition
  with ease of reading and writing.
- support normal commenting habits with inline and block options.
- be easy to navigate to and jump between 
- be easy to distinguish them from normal code comments.

This these principles in mind, here is the suggested ecomment format for Python
files. Other languages/file formats would be similar.

```python
"""
A file demonstrating ecomments.
"""
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
```
