# Ginear 🍸

[![PyPI version](https://badge.fury.io/py/ginear.svg)](https://badge.fury.io/py/ginear)

Ginear is the perfect blend of Git and Linear, creating a seamless integration that allows you to attach or create Linear issues with automatic branch switching.

![ginear](https://github.com/warlo/ginear/assets/5417271/607660c6-e49e-4244-bcf9-327004c94e02)

## Prerequisites

Before using Ginear, make sure you have the following prerequisites installed:

- [fzf](https://github.com/junegunn/fzf): Ginear relies on this utility for fuzzy searching.

```bash
brew install fzf
```

## Installation

You can install Ginear using pip:

```python
pip install ginear
```

## Getting Started

To start using Ginear, simply run the following command:

```bash
gin
```

On your initial run, Ginear will onboard you to set the correct environment variables for your project. These variables are stored in a `.ginear` config file in your `$HOME`, which Ginear will use to provide a tailored integration experience. This configuration ensures that Ginear seamlessly connects Git and Linear for your specific project.

## Command Overview

Ginear offers the following commands to enhance your workflow:

### `gin`

The `gin` command allows you to attach to an existing Linear issue or create a new one. When you run `gin`, Ginear will prompt you to select an existing issue from the list or create a new one.

### `gin create`

Use `gin create` to create a new Linear issue directly from the command line. Ginear will guide you through the issue creation process and automatically handle branch switching if necessary.

### `gin project`

With `gin project`, you can switch to a different Linear project within your organization. This command allows you to change your project context, and Ginear will adapt to the selected project's settings.

### `gin team`

The `gin team` command allows you to switch between different teams within your organization. When you run `gin team`, Ginear will prompt you to select the team you want to work with from a list of available options.
