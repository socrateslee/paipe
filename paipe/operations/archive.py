'''
Convert a list of files into a markdown of file contents.
'''
import os
from typing import List, Tuple


def split_to_filelist(output):
    filelist = []
    for i in output.split():
        file = i.strip()
        if not file:
            continue
        filelist.append(file)
    return filelist


def wrap_html_comment(filename, content):
    return f'<!-- begin {filename} -->\n{content}\n<!-- end {filename} -->\n\n'


def archive_to_markdown(files, content_list: List[Tuple[str, str]]=None):
    markdown = ''
    for filename in files:
        if os.path.isfile(filename):
            with open(filename, 'r') as fd:
                markdown += wrap_html_comment(filename, fd.read())
    if content_list:
        for (filename, content) in content_list:
            markdown += wrap_html_comment(filename, content)
    return markdown


def archive(output, filelist: list | None=None, use_stdin_as: str='list'):
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
    return archive_to_markdown(filelist)