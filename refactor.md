# Refactor
*Reafactor of Script class defined in src/arc/script/script.py*

## Why? 
The Script Class is getting difficult to wield and 
modify and I think it needs a refactor. It handles
too many checks and variables to be easy to change.

## Proposed Refactors / Reworks
Ideally, the outward facing script API should main 
exactly the same. (Which really only means the 
\__call__ method, everything else is private)

### 1. Multiple Script Objects
Create a script_factory function that takes in a
series of arguements and decides what kind of script
object to return. Each script object would inherit from
a `Script` super class that would provide a series of 
useful methods and also enforce that each follows the same
API pattern.

