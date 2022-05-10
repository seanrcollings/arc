This tutorial will be all about writing a *simple* grep clone in *arc*.

When completed our grep clone will be able to:

- Accept a `PATTERN` to search for
- Accept any number of `FILES` to search
- Ouptut lines of the `FILES` that match the `PATTERN` to stdout, with coloring


## 1. Setup

To begin with we need to scaffold the project

Install arc if you haven't already
```console
$ pip install arc-cli
```

And create a file called `grep_clone.py` that contains the following:
```py title="examples/grep_clone/1_grep_clone.py"
--8<-- "examples/grep_clone/1_grep_clone.py"
```
This is just some simple scaffolding to get us started. Run it to make sure eveything is in order.
```console
--8<-- "examples/outputs/1_grep_clone"
```

## 2. Arguments
Next, we're going to want to add arguments to the command. For now, we'll only be implementing the `PATTERN` and `FILES` arguments. All of grep's many flags will be left alone for now.

```py title="examples/grep_clone/2_grep_clone.py"
--8<-- "examples/grep_clone/2_grep_clone.py"
```

```console
--8<-- "examples/outputs/2_grep_clone"
```

As you can see, we've already got a validated regex pattern, and file handles to each of the specified files.

## 3. Functionality

With type handling / data validation *already* out of the way, the implentation will be fairly straightfoward.

```py title="examples/grep_clone/3_grep_clone.py"
--8<-- "examples/grep_clone/3_grep_clone.py"
```
Let's run this over a couple of *arc's* documentation files searching for references to *arc*
```console
--8<-- "examples/outputs/3_grep_clone"
```