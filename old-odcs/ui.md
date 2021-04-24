# ARC UI
Going foward, ARC will have some support for various text-based UI components that can be used to spice up user input gathering.

Currently, the only component implemented is the `SelectionMenu`

# SelectionMenu
Used to ask the user to select a response from a defined list of items.

## Usage `ui.SelectionMenu(options: List[str], format_str: str, selected_format_str: str)`
Creates a keyboard-navigable list of `options`.

`format_str` determines how each element in the list appears
- the formatted string has two available tokens: `index` and `string`
- default is: `"({index}) {string}"`

`selected_format_str` determines how the currently selected item in the list appears.
- Has the same tokens as `format_str`
- default is `fg.RED + effects.BOLD + "({index}) {string}" + effects.CLEAR`

The list can be navigated with the arrow keys, w/s or j/k. With the chosen option highlighted, pressing enter will pick it. The menu will then return back to the caller a tuple contained the index and string that the user selected

## Example
```py
from arc.ui import SelectionMenu

reg_str = fg.BLACK.bright
+ bg.BLACK
+ effects.ITALIC
+ "  ({index})  {string}  "
+ effects.CLEAR

selected_str =fg.BLACK.bright
+ bg.WHITE
+ effects.BOLD
+ "  ({index})  {string}  "
+ effects.CLEAR

selected = SelectionMenu(
    ["option1", "option2", "option3"],
    format_str=reg_str
    selected_format_str=selected_str
).run()
```

If the user selected `option2` from that list, `selected` would then be the tuple `(1, "option2")`
