# pAIpe: Your LLM shell assistant 

[![PyPI version](https://badge.fury.io/py/paipe.svg)](https://pypi.org/project/paipe/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**pAIpe** is a command-line tool designed to streamline your interactions with Large Language Models (LLMs). It provides a flexible and configurable pipeline to process text input through various LLM providers and models, managed through profiles for ease of use and customization.

## Features

- **Command-Line Interface:**  Simple and intuitive CLI for interacting with LLMs directly from your terminal.
- **Profile-Based Configuration:**  Define and manage multiple LLM configurations (profiles) in a `paipe.yaml` file, allowing you to switch between different providers, models, and settings effortlessly.
- **Streaming Output:** Supports streaming responses from LLMs for a more interactive and real-time experience.
- **Input from Stdin or File:** Read input text from standard input for quick prompts or from files for processing larger documents.
- **Extendable Configurations:** Designed to be easily extended with new LLM providers and models by modifying the configuration file.

## Installation

```bash
# install with openai protocol supported
python -m pip install -U paipe[openai]
# install with all protocol supported
python -m pip install -U paipe[all]
```
Or install using uv(run with `uvx paipe`):

```bash
# install with openai protocol supported
uv tool install -U paipe[openai]
# install with all protocol supported
uv tool install -U paipe[all]
```

## Configuration

`paipe` is configured using a `paipe.yaml` file. This file should be placed in one of the following locations (in order of priority):

1.  Current directory (`./paipe.yaml`)
2.  User local directory (`~/.local/share/paipe/paipe.yaml`)
3.  System configuration directory (`/etc/paipe.yaml`)

If no `paipe.yaml` is found in these locations, `paipe` will prompt an error message and exit.

Here's an example of a `paipe.yaml` configuration file(access api via openrouter):

```yaml
default:
    protocol: openai
    api_key: 'YOUR_OPENROUTER_API_KEY_HERE' # Replace with your actual API key
    base_url: 'https://openrouter.ai/api/v1'
    model: 'deepseek/deepseek-chat:free'
deepseek-r1:
    protocol: openai
    api_key: 'YOUR_OPENROUTER_API_KEY_HERE' # Replace with your actual API key
    base_url: 'https://openrouter.ai/api/v1'
    model: 'deepseek/deepseek-r1:free'
```

Each section in the `paipe.yaml` file defines a **profile**.  Here's a breakdown of the profile settings:

- **`protocol`**: Specifies the LLM API protocol. Currently, `paipe` is configured to use `openai` which can interface with various providers through platforms like OpenRouter or directly with specific APIs.
- **`api_key`**: Your API key for the chosen provider.  **Replace the placeholder `'YOUR_API_KEY_HERE'` with your actual API key.**
- **`base_url`**: The API base URL for the provider. For OpenRouter, it's typically `'https://openrouter.ai/api/v1'`.
- **`model`**: The specific LLM model to use from the provider.  The available models depend on your chosen provider and API key access. Examples include `'google/gemini-2.0-pro-exp-02-05:free'`, `'qwen2-72b-instruct'`, `'deepseek/deepseek-r1:free'`, etc.

## Usage

Basic usage:

```bash
paipe <prompt>
```

This will execute `paipe` with the `<prompt>` you provide, using the `default` profile defined in your `paipe.yaml` and stream the response to your terminal.


```bash
cat essay.txt | paipe --profile deepseek-r1 "write a summary of the following text:"
```

This will read the content of `essay.txt` and send it to the `deepseek-r1` profile for processing.


```bash
paipe --list
```

This will list all the available profiles defined in your `paipe.yaml` file.

## License

`paipe` is released under the MIT License. See the `LICENSE` file for more details.