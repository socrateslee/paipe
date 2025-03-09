'''
Convert a list of files into a markdown of file contents.
'''
import os


def split_to_filelist(output):
    filelist = []
    for i in output.split():
        file = i.strip()
        if not file:
            continue
        filelist.append(file)
    return filelist


def filelist_to_markdown(files):
    markdown = ''
    for file in files:
        if os.path.isfile(file):
            markdown += f'``` title="{file}" \n{open(file).read()}\n```\n\n'
    return markdown


def stdin_to_markdown(output):
    '''
    Convert the filelist to content markdown.
    '''
    filelist = split_to_filelist(output)
    return filelist_to_markdown(filelist)