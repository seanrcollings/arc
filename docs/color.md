# Color Module
Spice up your script's output with some color! Implements both the basic ANSI-16 color scheme, and rgb

## `arc.color.fg`
Contains the code for coloring text elements.

### Constants Defined Here:
- BLACK
- RED
- GREEN
- YELLOW
- BLUE
- MAGENTA
- CYAN
- WHITE

The brighter alternatives to each color is accessed through the `bright` attribute on each color. i.e. `fg.WHITE.bright`

### `fg.rgb(red: int, green: int, blue: int)`
Used to create any text color in the full RGB specturm. Each paramater's values range from [0, 255]


## `arc.color.bg`
Contains the code for coloring the background of elements.

### Constants Defined Here:
- BLACK
- RED
- GREEN
- YELLOW
- BLUE
- MAGENTA
- CYAN
- WHITE

The brighter alternatives to each color is accessed through the `bright` attribute on each color. i.e. `bg.WHITE.bright`

### `bg.rgb(red: int, green: int, blue: int)`
Used to create any background color in the full RGB specturm. Each paramater's values range from [0, 255]

## `arc.color.effects`
Other visual effects that can be applied to text output

### Constants Defined Here:
- CLEAR
- BOLD
- ITALIC
- UNDERLINE
- STRIKETHROUGH