from pathlib import Path
import yaml
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


def get_profile(profile_name: str):
    """
    Get a profile by name.
    """
    configs = load_paipe_config()
    if configs is None:
        return None
    profile_dep_list = []
    curr = profile_name
    while True:
        profile = configs.get(curr)
        if profile is None:
            return None
        profile_dep_list.append(curr)
        _from = profile.get('_from')
        if not _from:
            break
        curr = _from
    profile_result = {}
    model_settings_result = {}
    for profile_name in reversed(profile_dep_list):
        profile = configs[profile_name]
        model_settings = profile.pop('model_settings', {})
        model_settings_result.update(model_settings)
        profile_result.update(profile)
    profile_result.pop('_from', None)
    if model_settings_result:
        profile_result['model_settings'] = model_settings_result
    logger.debug(f"profile: {profile_result}")
    return profile_result


def list_profiles(prefix: str | bool = ''):
    '''
    List all profiles.
    '''
    configs = load_paipe_config()
    if configs is None:
        print("No profiles found")
        return
    if prefix is True:
        prefix = ''
    for profile_name in configs:
        if prefix and not profile_name.startswith(prefix):
            continue
        print(profile_name)