# XNav

A universal tool to detect clickable GUI widgets, regardless accessibility support.

## Idea

Thanks to the poor accessibility support of most modern softwares, we need a universal way to detect the region where lays clickable GUI widgets.

Most modern UI design adds **hover** effect buttons, buttons change color and style when mouse is hovering it.

This explains our approach. Scan the whole screen, moving mouse to every possible location. If underlying pixels changed, meaning a hover effect is used on the widget. Indicating this is likely a clickable widget.

## Workflow

1. move mouse to screen top left (0, 0).
2. hide mouse to prevent mouse showing up in screenshot.
3. capture a full screenshot (3840x2160).
4. define a 192x108 grids (20 pixel interval).
5. iterate over each grid, for each grid:
    1. move mouse to the center of the grid.
    2. wait a frame for application to update hover render.
    3. capture a screenshot in the grid rect.
    4. compare the grid screenshot with original full screenshot at the same grid rect.
    5. if any pixel different, mark as **dirty grid**.
6. created a 192x108 matrix of dirty grids.
7. plot a image, draw 30% transparent red rects for all dirty grids.
8. show the image in fullscreen (feh -F).


## Product Stages

[ ] Feasibility Study
[ ] Proof-of-concept: Python version
[ ] Final production: C++ version
