'''
Convert a list of files into a markdown of file contents.
'''
import os
from typing import List, Tuple, Literal, TypeVar

WrapType = Literal['html', 'markdown', 'none']


def split_to_filelist(output):
    filelist = []
    for i in output.split():
        file = i.strip()
        if not file:
            continue
        filelist.append(file)
    return filelist


def wrap_html_comment(filename, content):
    '''
    Wrap content in html comment, aka. <!--- comment --->
    '''
    return f'<!-- begin {filename} -->\n{content}\n<!-- end {filename} -->\n\n'


def wrap_markdown_comment(filename, content):
    '''
    Wrap content in markdown comment, aka. [comment]: #
    '''
    return f'[begin {filename}]: #\n{content}\n[end {filename}]: #\n\n'


def wrap_none(__, content):
    return content


def get_wrap_method(wrap: WrapType):
    if wrap == 'markdown':
        return wrap_markdown_comment
    elif wrap == 'none':
        return wrap_none
    else:
        return wrap_html_comment


def archive_to_markdown(files,
                        content_list: List[Tuple[str, str]],
                        wrap_method=None
    ):
    wrap_method = wrap_method or wrap_none
    markdown = ''
    for filename in files:
        if os.path.isfile(filename):
            with open(filename, 'r') as fd:
                markdown += wrap_method(filename, fd.read())
    if content_list:
        for (filename, content) in content_list:
            markdown += wrap_method(filename, content)
    return markdown


def archive(output,
            filelist: list | None=None,
            use_stdin_as: str='list',
            wrap: Literal['html', 'markdown', 'none']=None
    ):
    '''
    Convert the filelist to content markdown.
    '''
    if filelist is None:
        filelist = []
    content_list = []
    if use_stdin_as == 'list':
        pipe_filelist = split_to_filelist(output)
        filelist.extend(pipe_filelist)
    else:
        content_list.append(('STDIN', output))
    wrap_method = get_wrap_method(wrap)
    return archive_to_markdown(filelist, content_list, wrap_method=wrap_method)