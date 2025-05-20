import sys

def get_stdio():
    if not sys.stdin.isatty():
        return sys.stdin.read()


def handle_operation(args):
    if args.operation in ['archive', 'a']:
        from . archive import archive
        print(
            archive(get_stdio() or '', args.filelist, use_stdin_as=args.stdin)
        )
