import base64
import mimetypes
import logging
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
