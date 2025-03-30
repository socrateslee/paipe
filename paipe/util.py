import base64
import mimetypes
import logging
import importlib
import re
from typing import Generator

logger = logging.getLogger('paipe')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


def set_verbose(verbose: bool):
    if verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


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