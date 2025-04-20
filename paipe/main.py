import sys
import json
from pathlib import Path
import pydantic
import dydantic
import pydantic_ai.models
from pydantic_ai import Agent
from pydantic_ai.messages import BinaryContent
from .models import PaipeContext
from .util import (
    logger,
    import_module,
    extract_markdown_code_blocks,
    show_json_usage
)
from . profiles import get_profile


def import_model_module(name: str):
    module = import_module('paipe.providers', name)
    if not module:
        module = import_module('pydantic_ai.models', name)
    return module


def import_provider_module(name: str):
    return import_module('pydantic_ai.providers', name)


def get_agent_model_cls(module):
    for name in dir(module):
        obj = getattr(module, name)
        if hasattr(obj, '__mro__') and pydantic_ai.models.Model in obj.__mro__[1:]:
            return obj
    return None


def get_agent_provider_cls(module):
    for name in dir(module):
        obj = getattr(module, name)
        if hasattr(obj, '__mro__') and pydantic_ai.providers.Provider in obj.__mro__[1:]:
            return obj
    return None


def get_agent_model(model_name: str, protocol: str, provider: str, **profile):
    model_params = {}
    model_cls = get_agent_model_cls(import_model_module(protocol))
    provider_module = import_provider_module(provider)
    if provider_module:
        provider_cls = get_agent_provider_cls(provider_module)
        if provider_cls:
            provider_params = {}
            for key in provider_cls.__init__.__annotations__:
                if key == 'return':
                    continue
                if key in profile:
                    provider_params[key] = profile.pop(key)
            provider_instance = provider_cls(**provider_params)
            model_params['provider'] = provider_instance
    model_params.update(profile)
    return model_cls(model_name, **model_params)


def process_prompt(full_prompt: str, attachments: list | None = None) -> str | list:
    if not attachments:
        result = full_prompt
    else:
        result = [
            full_prompt
        ]
        for (media_type, data) in attachments:
            content = BinaryContent(
                data=data,
                media_type=media_type
            )
            result.append(content)
        else:
            pass
    return result


async def run_agent(context: PaipeContext):
    profile = get_profile(context.profile)
    if profile is None:
        print(f"Profile {context.profile} is not available in the profile.")
        sys.exit(1)

    protocol = profile.pop('protocol', None) or profile.pop('provider', None) or 'openai'
    provider = profile.pop('provider', None) or 'openai'
    model = profile.pop('model', None) or ''
    profile_system_prompt = profile.pop('system_prompt', None)
    model_settings =  profile.pop('model_settings', None)

    agent_params = {
        "system_prompt": context.system_prompt or profile_system_prompt or (),
        "model_settings": model_settings
    }
    if context.json_schema:
        agent_params['result_type'] = dydantic.create_model_from_schema(
                json.loads(context.json_schema))
        context.stream = False
    elif context.extract_code_block:
        context.stream = False
    logger.debug(f'[model to use] {context.model or model}')

    agent = Agent(get_agent_model(context.model or model, protocol, provider, **profile),
                  **agent_params)
    full_prompt  = ''
    if context.prompt:
        full_prompt += f'{context.prompt}\n'
    if context.input_text:
        full_prompt += f'{context.input_text}\n'

    processed_prompt = process_prompt(full_prompt,
                                      attachments=context.attachments)

    if context.stream:
        async with agent.run_stream(processed_prompt) as response:
            async for delta in response.stream_text(delta=True):
                print(delta, end='', flush=True)
        print()
        if context.usage:
            show_json_usage(response.usage())
    else:
        result = await agent.run(processed_prompt)
        if context.json_schema and isinstance(result.data, pydantic.BaseModel):
            print(result.data.model_dump_json())
        elif context.extract_code_block and isinstance(result.data, str):
            language = '' if context.extract_code_block is True else context.extract_code_block
            code_blocks = extract_markdown_code_blocks(
                result.data,
                language=language
            )
            if not code_blocks:
                logger.warning(f"No {language} code block detected.")
            print(code_blocks[-1] if code_blocks else '')
        else:
            print(result.data)
        if context.usage:
            show_json_usage(result.usage())
