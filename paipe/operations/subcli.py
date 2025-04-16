import argparse


def build_command_parser(commond_parser: argparse.ArgumentParser):
    sub_parsers = commond_parser.add_subparsers(dest='operation',
                                                 help='Operations')
    cmd_archive = \
        sub_parsers.add_parser('archive',
                                help='Archive files into a text file')
    cmd_archive.add_argument(
        '--stdin',
        type=str, default='list', choices=['list', 'content'],
        help='Use stdin as list of filenames to archive, or simply as content to archive')
    cmd_archive.add_argument(
        'filelist',
        type=str, nargs='*', metavar='FILENAME',
        help='Lisf of filenames to archvie')
