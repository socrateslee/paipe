# Resposne in JSON Format

## Use `model_setting`

If a model API support `response_format`, you can use `model_setting` to specify the response format. There may be 2 ways for a model API to support `response_format`.

1. The model API support `response_format` as `{"type": "json_schema"}`. In this case, you neeed to specify the json_schema in the config as below:

```paipe.yaml
profile-json:
    provider: openai
    api_key: '<YOUR_API_KEY>'
    base_url: '<YOUR_BASE_URL>'
    model: '<YOUR_MODEL>'
    model_settings:
        response_format:
            type: json_schema
            json_schema:
                name: answer
                schema:
                    type: object
                    properties:
                        mask:
                            type: string
```

The config may be used as below:

```bash
$ paipe -P profile-json "The world is full of [mask]. Find a proper word to fill the mask."
{
  "mask": "wonder"
}
```

2. The model API support `response_format` as `{"type": "json_object"}`. In this case, you can write a config as below:

```paipe.yaml
profile-json:
    provider: openai
    api_key: '<YOUR_API_KEY>'
    base_url: '<YOUR_BASE_URL>'
    model: '<YOUR_MODEL>'
    model_settings:
        response_format:
            type: json_object
```

The config could be used as below:

```bash
$ paipe -P profile-json "The world is full of [mask]. Replace mask with proper word, return in JSON format {\"answer\": \"<ANSWER>\"}"
{"answer": "wonder"}
```

## Use `--json`

The model API may not support `response_format`, in this case, you can use `--json` to specify the response format. `--json` leverages the pydantic_ai to use the tool calling to generate JSON response. For example, 

```bash
$ paipe --json '{"type": "object", "properties": {"name": {"type": "string"}}}' \
"What is the biggest planet in the solar system?"
{"name":"Jupiter"}
```

## Use `--extract`/`-e`

If the model response is in  format but wrapped in a markdown code block, you can use `--extract`/`-e` to extract the JSON result. Here's an example:

```bash
$ paipe --extract json "The world is full of [mask]. Find a proper word to fill the mask and return in JSON format."
{"mask": "wonder"}
```

In this example, `--extract json` tells `paipe` to extract the last JSON code block from the response. You can also use `--extract` with other languages or without specifying a language to extract the last code block.

```bash
$ paipe --extract -- "The world is full of [mask]. Find a proper word to fill the mask and return in JSON format."
{"mask": "wonder"}
```