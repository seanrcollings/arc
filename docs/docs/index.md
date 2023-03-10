---
title: Home
---
# Overview
*arc* is a tool for building declarative, and highly extendable CLI applications for Python ^3.10.

## Features

*arc's* features include:

* [Command line Arguments, Options, and Flags](./usage/parameters/intro.md) - Using Python function arguments
* [Data Validation](./usage/parameters/types/types-intro.md) - Via Python type hints
* [Subcommands](./usage/subcommands.md) - Breaking functionality into discrete components
* [Documentation](./usage/documentation-generation.md) - Automatic `--help` generation from your command definitons
* [User Extension](./usage/command-autoloading.md) - Dynamic command loading at runtime

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
--8<-- "examples/outputs/hello"
```

### Automatic Documentation
And a quick demonstration of the documention generation:
```console
--8<-- "examples/outputs/hello_help"
```
Pretty cool, huh? *arc* will pull *all* of the information that it needs from your [function docstrings and parameter definitons.](usage/documentation-generation.md)

### Configuration
*arc* is easily configurable via the `#!python arc.configure()` function.

For example, you can set a version string for you application. This will add a `--version` flag to your application.

```py title="examples/hello_configuration.py"
--8<-- "examples/hello_configuration.py"
```

```console
--8<-- "examples/outputs/hello_configuration"
```


*View the [reference](reference/config.md#arc.config.configure) for details on all the configuration options*
