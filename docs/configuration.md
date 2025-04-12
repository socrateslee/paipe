# Configuration

`paipe` uses a YAML file (`paipe.yaml`) to manage different LLM configurations, referred to as "profiles". This file allows you to easily switch between different providers, models, and API keys.

## Configuration File Location

`paipe` searches for `paipe.yaml` in the following locations, in order of precedence:

1.  **Current Working Directory:** `./paipe.yaml` (The directory where you run the `paipe` command)
2.  **User Local Data Directory:** `~/.local/share/paipe/paipe.yaml` (A user-specific directory)
3.  **System Configuration Directory:** `/etc/paipe.yaml` (A system-wide directory)

If no `paipe.yaml` file is found in any of these locations, `paipe` will display an error message and exit.

## `paipe.yaml` Structure

The `paipe.yaml` file uses a simple YAML structure. The top-level keys represent profile names, which could be specified by `paipe -P <profile_name>`. One of which is named `default`, can be called without the `-P` parameter. Each profile contains settings for connecting to an LLM.

For example:

```yaml
default:
    provider: openai
    api_key: 'YOUR_OPENROUTER_API_KEY_HERE'  # Replace with your actual API key
    base_url: 'https://openrouter.ai/api/v1'
    model: 'deepseek/deepseek-chat:free'

deepseek-r1:
    provider: openai
    api_key: 'YOUR_OPENROUTER_API_KEY_HERE'  # Replace with your actual API key
    base_url: 'https://openrouter.ai/api/v1'
    model: 'deepseek/deepseek-r1:free'

another-profile:  # Example with different settings
    provider: openai  #Currently, paipe is configured to use `openai`
    api_key: 'YOUR_API_KEY'
    base_url: 'https://api.example.com/v1'  #  A different base URL
    model: 'some-other-model'
```

### Profile Settings

Each profile in `paipe.yaml` can contain the following settings:

-   **`protocol`** *(required)*:  The LLM protocol. For example, `openai` allows it to connect to various LLM providers as long as the provider's API is compatible with the OpenAI API structure.
-   **`api_key`** *(required)*:  Your API key for the selected LLM provider. **Crucially, replace placeholder values like `'YOUR_OPENROUTER_API_KEY_HERE'` with your actual API key.**
-   **`base_url`** *(required)*:  The base URL for the LLM provider's API. For OpenRouter, this is `https://openrouter.ai/api/v1`. For direct connections to other providers, consult their documentation for the correct base URL. Note that `base_url` is not required for OpenAI's own API.
-   **`model`** *(required)*:  The name of the specific LLM model you want to use. Available models depend on your provider and API key. Examples are `'deepseek/deepseek-chat:free'`, `'google/gemini-2.0-pro-exp-02-05:free'`, and  `'qwen2-72b-instruct'`. Consult your provider's documentation for a list of available models.

### Default Profile

The `_from` key specifies the source profile to inherit settings from. This allows you to create profiles that build upon existing configurations, reducing redundancy and simplifying management. For example, you can define a base profile with common settings and then create specialized profiles that inherit from it and override only the necessary parameters.
`paipe.yaml` *must* contains a profile called `default`. This profile will be launched automatically, if no other profile is specified via `-P` or `--profile`. 

### Multiline System Prompt

You can also specify a multiline system prompt for a profile. This is useful for providing detailed instructions or context to the LLM. To define a multiline system prompt, use the `>` character to indicate the start of the prompt and ensure that each line is properly indented. For example:

```yaml
profile_name:
    system_prompt: >
      This is a multiline system prompt.
      It can span multiple lines and include
      complex instructions for the LLM.
```
Run `paipe --list` to see the list of available profiles from your configurations.

## Protocols

Here are several protocols that `paipe` supports:

### mistral
Use the official API of [Mistral AI](https://mistral.ai), set `mistral` for protocol. Example:

```
mistral:
    protocol: mistral
    api_key: <YOUR_MISTRAL_API_KEY>
    model: mistral-large-latest
```

The full list of available models can be found [here](https://docs.mistral.ai/getting-started/models/models_overview/).

### groq
Use the official API of [Groq](https://groq.com), set `groq` for protocol. Example:

```
groq-mixtral:
    protocol: groq
    api_key: <YOUR_GROQ_API_KEY>
    model: 'mixtral-8x7b-32768'
```

The full list of available models can be found [here](https://console.groq.com/docs/models). And the groq API is also compatible with OpenAI API, so you can use `openai` as the provider(set base_url as https://api.groq.com/openai/v1).

### Cohere
Use the official API of [Cohere](https://cohere.com), set `cohere` for protocol. Example:

```
cohere:
    protocol: cohere
    api_key: <YOUR_COHERE_API_KEY>
    model: 'command-r-plus-08-2024'
```

The full list of available models can be found [here](https://docs.cohere.com/v2/docs/models).