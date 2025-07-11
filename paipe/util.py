import sys
import os
import json
import base64
import mimetypes
import logging
import importlib
import inspect
import re
import argparse
from typing import Callable, Generator, Dict, Any
import pydantic_ai.result

logger = logging.getLogger('paipe')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def set_verbose(verbose: bool):
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


class DeprecatedAction(argparse.Action):
    def __init__(self, option_strings, deprecated=False, help=None, **kwargs):
        if help is not None:
            if deprecated:
                help += ' (DEPRECATED)'
        super().__init__(option_strings, help=help, **kwargs)
        self.deprecated = deprecated

    def __call__(self, parser, namespace, values, option_string=None):
        if self.deprecated:
            logger.warning(
                self.deprecated if isinstance(self.deprecated, str)\
                      else f'{self.option_strings[0]} is deprecated.'
                )
        setattr(namespace, self.dest, values)


def file_as_data_url(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        data = f.read()
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'
    data_type = 'text'
    if mime_type.startswith('image/'):
        data_type = 'image'
    elif mime_type.startswith('video/'):
        data_type = 'video'
    return (data_type, f'data:{mime_type};base64,{base64.b64encode(data).decode("utf-8")}')


def to_attachment_pairs(file_path_list: list[str]) -> Generator[tuple[bytes, str], None, None]:
    for file_path in file_path_list:
        data = open(file_path, 'rb').read()
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        yield (mime_type, data)


def import_module(parent_module: str, name: str):
    '''
    Import a module from a parent module.
    '''
    try:
        return importlib.import_module(f'{parent_module}.{name}')
    except ImportError as e:
        return None


def find_cls(module, base_class):
    '''
    Find a class in a module that inherits from a base class.
    '''
    for name in dir(module):
        obj = getattr(module, name)
        if hasattr(obj, '__mro__') and base_class in obj.__mro__[1:]:
            return obj
    return None


def find_all_cls(module, base_class):
    '''
    Find all classes in a module that inherit from a base class.
    '''
    classes = []
    for name in dir(module):
        obj = getattr(module, name)
        if hasattr(obj, '__mro__') and base_class in obj.__mro__[1:]:
            classes.append(obj)
    return classes


def list_sub_modules(parent_module):
    '''
    List sub modules of a module.
    '''
    sub_modules = []
    module_path = parent_module.__file__
    py_files = [f for f in os.listdir(os.path.dirname(module_path)) if f.endswith('.py')]
    for py_file in py_files:
        module_name = py_file[:-3]
        if module_name == '__init__':
            continue
        sub_modules.append(module_name)
    return sub_modules


def extract_markdown_code_blocks(markdown: str, language: str = '') -> list:
    """
    Extract code blocks from a markdown document.

    Args:
        markdown: The markdown text to process
        language: Optional language filter (case insensitive)

    Returns:
        A list of extracted code blocks
    """
    pattern = r'```([\w+-]*)\n(.*?)\n```'
    matches = re.findall(pattern, markdown, re.DOTALL)
    if language:
        return [code for lang, code in matches
                if lang.lower() == language.lower()]
    else:
        return [code for _, code in matches]


def patch_video_mimetype():
    @property
    def is_image(self) -> bool:
        """Return `True` if the media type is an image type."""
        return self.media_type.startswith(('image/', 'video/'))
    from pydantic_ai.messages import BinaryContent
    BinaryContent.is_image = is_image
    logger.debug("Patched pydantic_ai.messages.BinaryContent.is_image")


def show_json_usage(usage: pydantic_ai.result.Usage,
                    file=None):
    if file is None:
        file = sys.stderr
    print("Usage:", json.dumps(usage.__dict__), file=file)


def init_via_annotations(cls: type, params: Dict[str, Any]):
    '''
    Initialize a class with parameters via annotations.
    '''
    init_params = {}
    for key in cls.__init__.__annotations__:
        if key == 'return':
            continue
        if key in params:
            init_params[key] = params.pop(key)
    return cls(**init_params)


def kwargs_by_func_def(func: Callable, kwargs: Dict[str, Any]) -> Dict[str, Any]:
    '''
    Filter kwargs by function definition.
    '''
    func_def = inspect.signature(func)
    return {k: v for k, v in kwargs.items() if k in func_def.parameters}