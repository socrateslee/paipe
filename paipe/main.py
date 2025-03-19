import os
import sys
import glob
import json
import importlib
from pathlib import Path
import yaml
import pydantic
import dydantic
import pydantic_ai.models
from pydantic_ai import Agent
from .models import PaipeContext
from .util import logger


def load_paipe_config():
    """
    Load paipe.yaml config file with priority:
    ./ > ~/.local/share/paipe/ > /etc/
    """
    config_locations = [
        Path('./paipe.yaml'),  # Current directory
        Path.home() / '.local' / 'share' / 'paipe' / 'paipe.yaml',  # User local
        Path('/etc/paipe.yaml')  # System config
    ]
    for config_path in config_locations:
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML in {config_path}: {e}")
                continue
            except Exception as e:
                print(f"Error reading {config_path}: {e}")
                continue
    print("No valid paipe.yaml configuration found")
    return None


def extract_modules(path: str):
    """
    Extract all Python module names from a directory path,
    excluding __init__.py files.
    """
    modules = []
    for file in os.listdir(os.path.dirname(path)):
        if file.endswith('.py') and file != '__init__.py':
            file_name = os.path.basename(file)
            module = file_name[:-3]
            modules.append(module)
    return modules


def import_module(name: str):
    try:
        return importlib.import_module(f'.providers.{name}', package='paipe')
    except ImportError as e:
        print(f"Error importing module {name}: {e}")
        pass
    full_module_path = f'pydantic_ai.models.{name}'
    module = importlib.import_module(full_module_path)
    return module


def get_agent_model_cls(module):
    for name in dir(module):
        obj = getattr(module, name)
        if hasattr(obj, '__mro__') and pydantic_ai.models.Model in obj.__mro__[1:]:
            return obj
    return None


def process_prompt(full_prompt: str, attachments: list | None = None) -> str | list:
    if not attachments:
        result = full_prompt
    else:
        result = [
            {
                "type": "text",
                "text": full_prompt
            }
        ]
        for data_type, attachment in attachments:
            if data_type == 'image':
                result.append({
                    "type": "image_url",
                    "image_url": {'url': attachment}
                })
            elif data_type == 'video':
                result.append({
                    "type": "video_url",
                    "video_url": {'url': attachment}
                })
            else:
                pass
    return result


async def run_agent(context: PaipeContext):
    configs = load_paipe_config()
    profile = configs[context.profile]

    provider = profile.pop('provider', None) or 'openai'
    model = profile.pop('model', None) or ''
    profile_system_prompt = profile.pop('system_prompt', None)
    model_settings =  profile.pop('model_settings', None)

    agent_model_cls = get_agent_model_cls(import_module(provider))
    agent_params = {
        "system_prompt": context.system_prompt or profile_system_prompt or (),
        "model_settings": model_settings
    }
    if context.json_schema:
        agent_params['result_type'] = dydantic.create_model_from_schema(
                json.loads(context.json_schema))
        context.stream = False
    logger.debug(f'[model to use] {context.model or model}')

    agent = Agent(agent_model_cls(context.model or model, **profile),
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
    else:
        result = await agent.run(processed_prompt)
        if context.json_schema and isinstance(result.data, pydantic.BaseModel):
            print(result.data.model_dump_json())
        else:
            print(result.data)


def list_profiles():
    '''
    List all profiles.
    '''
    configs = load_paipe_config()
    if configs is None:
        print("No profiles found")
        return
    for profile_name in configs:
        print(profile_name)