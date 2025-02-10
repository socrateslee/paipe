# pAIpe Installation Guide

This document provides instructions on how to install and configure **pAIpe**, your LLM shell assistant.

## Installation

You can install pAIpe using pip:

```bash
python -m pip install -U paipe
```

Alternatively, if you have `uv` installed, you can use:

```bash
uv tool install -U paipe
```

## Configuration

`paipe` uses a `paipe.yaml` file for configuration.  This file defines *profiles*, each representing a specific LLM configuration (provider, model, API key, etc.).

### Configuration File Location

`paipe` searches for `paipe.yaml` in the following locations, in order of priority:

1.  **Current Directory:** `./paipe.yaml` (The directory where you run the `paipe` command)
2.  **User Local Directory:** `~/.local/share/paipe/paipe.yaml`
3.  **System Configuration Directory:** `/etc/paipe.yaml`

If no `paipe.yaml` file is found in any of these locations, `paipe` will display an error message and exit.  You *must* create a configuration file to use `paipe`.

### Example `paipe.yaml` (OpenRouter)

Here's an example configuration file using OpenRouter as the LLM provider:

```yaml
default:
    provider: openai
    api_key: 'YOUR_OPENROUTER_API_KEY_HERE' # Replace with your actual API key
    base_url: 'https://openrouter.ai/api/v1'
    model: 'deepseek/deepseek-chat:free'
deepseek-r1:
    provider: openai
    api_key: 'YOUR_OPENROUTER_API_KEY_HERE' # Replace with your actual API key
    base_url: 'https://openrouter.ai/api/v1'
    model: 'deepseek/deepseek-r1:free'
test: # just for test
    provider: test
```

**Important:**  Replace `YOUR_OPENROUTER_API_KEY_HERE` with your actual OpenRouter API key.

### Profile Settings

paipe leverage `pydantic_ai` to access different types of LLM APIs. Each profile in `paipe.yaml` is used to configure the sub module in `pydantic_ai.models` w.r.t. the provider type of the profile.

For most APIs are compitable with OpenAI API, you may setup your profiles like the following:

*   **`provider`**:  Use `openai`.
*   **`api_key`**: Your API key for the chosen provider.  **You must replace the placeholder with your actual API key.**
*   **`base_url`**: The API base URL for the provider (e.g.,  `https://openrouter.ai/api/v1` for OpenRouter).
*   **`model`**: The specific LLM model to use (e.g., `deepseek/deepseek-chat:free`, `qwen2-72b-instruct`,  `google/gemini-2.0-pro-exp-02-05:free`). Available models depend on your provider and API key.

You can add more profiles to your `paipe.yaml` file to switch between different LLMs and configurations(vis `paipe -P <profile name>`).

