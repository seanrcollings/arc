Spice up your script's output with some color! Implements both the basic ANSI-16 color scheme, and rgb

## `arc.color.fg`
Contains the code for coloring text elements.

### Constants
- `BLACK`
- `GREY`
- `RED`
- `GREEN`
- `YELLOW`
- `BLUE`
- `MAGENTA`
- `CYAN`
- `WHITE`
- `ARC_BLUE`

The brighter alternatives to each color is accessed through the `bright` attribute on each color. i.e. `fg.BLUE.bright`

### `fg.rgb(red: int, green: int, blue: int)`
Used to create any text color in the full RGB specturm. Each paramater's values range from [0, 255]

### `fg.hex(hex_code: str | int)`
Used to create a color using a hex code instead of the RGB values. Can be passed the hex code as a string (`'#fff'`, `'#333'`) or as a number using Python's hex shorthand (`0xfff`, `0x333`)

## `arc.color.bg`
Contains the code for coloring the background of elements.

### Constants
- `BLACK`
- `GREY`
- `RED`
- `GREEN`
- `YELLOW`
- `BLUE`
- `MAGENTA`
- `CYAN`
- `WHITE`
- `ARC_BLUE`

The brighter alternatives to each color is accessed through the `bright` attribute on each color. i.e. `bg.BLUE.bright`

### `bg.rgb(red: int, green: int, blue: int)`
Used to create any background color in the full RGB specturm. Each paramater's values range from [0, 255]

### `bg.hex(hex_code: str | int)`
Used to create a color using a hex code instead of the RGB values. Can be passed the hex code as a string (`'#fff'`, `'#333'`) or as a number using Python's hex shorthand (`0xfff`, `0x333`)

## `arc.color.effects`
Other visual effects that can be applied to text output

### Constants:
- `CLEAR`
- `BOLD`
- `ITALIC`
- `UNDERLINE`
- `STRIKETHROUGH`


## `arc.color.colorize(string: str, *codes: str | Ansi, clear: bool = True)`
`colorize()` applies an arbitrary number of colors / effects to the provided string, and adds `effects.CLEAR` to the end of the string.
```py
from arc.color import colorize, fg, bg, effects
print(colorize('This is a colored string', fg.RED, bg.GREY, effects.UNDERLINE))
```
![Output](../img/colored-output.png)