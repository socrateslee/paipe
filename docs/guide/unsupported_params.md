# Unsupported Parameters

To deal with the problem of the different parameters of different providers of the same API protocol, e.g., the `openai` API protocol is wildly compatible with most of the LLM API proivders, but different providers have may have different parameters for their own specific features.

To deal with the problem with `openai` protocol, you may specify `extra_headers`, `extra_` and `extra_body` in model_settings part of the profile.

For example, OpenRouter has a parameter []`transfrom`](https://openrouter.ai/docs/features/message-transforms) to mitigate the API from raising error where the size of prompt is too large(exceeding the context length of the model). You write a profile to pass the parameter in the `extra_body` field:

```yaml
openrouter:
    provider: openai
    api_key: '<Your OpenRouter API Key>'
    base_url: 'https://openrouter.ai/api/v1'
    model: 'openrouter/auto'
    model_settings:
      extra_body: 
        transforms: ["middle-out"]
```

Then you can use the profile with `paipe`:

```bash
paipe -P openrouter --file a-very-large-file.txt Summarize the following text:
```