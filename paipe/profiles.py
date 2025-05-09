import platform
from pathlib import Path
import yaml
from .util import logger


def get_config_locations():
    """
    Return the config locations based on current OS
    """
    if platform.system() == 'Windows':
        return [
            Path('./paipe.yaml'),  # Current directory
            Path.home() / '.paipe' / 'paipe.yaml',  # User home
            Path('C:\\ProgramData\\paipe\\paipe.yaml')  # System config
        ]
    else:
        return [
            Path('./paipe.yaml'),  # Current directory
            Path.home() / '.local' / 'share' / 'paipe' / 'paipe.yaml',  # User local
            Path('/etc/paipe.yaml')  # System config
        ]


def load_paipe_config():
    """
    Load paipe.yaml config file with priority:
    ./ > ~/.local/share/paipe/ > /etc/
    """
    config_locations = get_config_locations()
    for config_path in config_locations:
        if config_path.exists():
            try:
                logger.debug(f"Loading config from {config_path}")
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML in {config_path}: {e}")
                continue
            except Exception as e:
                logger.error(f"Error reading {config_path}: {e}")
                continue
    logger.error("No valid paipe.yaml configuration found")
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
        logger.error("No profiles found")
        return
    if prefix is True:
        prefix = ''
    for profile_name in configs:
        if prefix and not profile_name.startswith(prefix):
            continue
        print(profile_name)


def inspect_profile(profile_name: str):
    '''
    Inspect a profile.
    '''
    profile = get_profile(profile_name)
    if profile is None:
        logger.error(f"Profile {profile_name} not found")
        return
    if api_key := profile.get('api_key'):
        profile['api_key'] = f'{api_key[:5]}****{api_key[-5:]}'
    print(yaml.dump(profile, sort_keys=False))