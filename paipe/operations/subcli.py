import argparse


def build_command_parser(commond_parser: argparse.ArgumentParser):
    sub_parsers = commond_parser.add_subparsers(dest='operation',
                                                help='Operations')
    cmd_archive = \
        sub_parsers.add_parser('archive', aliases=['a'],
                               help='Archive files into a text file')
    cmd_archive.add_argument(
        '--stdin',
        type=str, default='list', choices=['list', 'content'],
        help='Use stdin as list of filenames to archive, or simply as content to archive')
    cmd_archive.add_argument(
        '--wrap',
        type=str, default='html', choices=['html', 'markdown', 'none'],
        help='''The method to wrap the content of each file(and mark the filename)
html: use <!-- -->
markdown: use []: #
none: do nothing
''')
    cmd_archive.add_argument(
        'filelist',
        type=str, nargs='*', metavar='FILENAME',
        help='List of filenames to archvie')
