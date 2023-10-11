# Ginear 🍸

Ginear is the perfect blend of Git and Linear, creating a seamless integration that allows you to attach or create Linear issues with automatic branch switching.

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
