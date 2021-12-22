---
title: Home
---
# Overview
*arc* is a tool for building declartive, and highly extendable CLI applications for Python ^3.9 based on Pyton type-hints

*arc's* features include:

* Command line arguments based on Python type hints
* Arbitrary command nesting
* Automatic `--help` documentation generation
* Dynamic command loading at runtime
* Single and multi-command modes

## Installation
*arc* can be installed with pip
```
$ pip install arc-cli
```

## Example
To start off, here's a simple example application that can be used to greet someone

```py title="hello.py"
--8<-- "examples/hello.py"
```
!!! tip
    The above example, and all examples in this documentation are complete
    and should run as-is. Additionally *all* examples are available in the
    [source repo](https://github.com/seanrcollings/arc/tree/master/docs/examples)


```console
--8<-- "examples/outputs/hello_exec"
```
And a quick demonstration of the documention generation:
```console
--8<-- "examples/outputs/hello_help"
```
Pretty cool, huh?
