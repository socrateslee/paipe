'''
The command line interface (CLI).
'''
import sys
import argparse
import asyncio
from . import util
from .models import PaipeContext
from .profiles import list_profiles, inspect_profile
from .main import run_agent

util.patch_video_mimetype()

GLOBAL_ACTION_ARGS = [
    '-h', '--help',
    '-v', '--verbose',
]

GLOBAL_ARGS = GLOBAL_ACTION_ARGS + [
    '--version'
]

SUB_COMMANDS = [
    'call',
    'op'
]

def build_call_parser(parser):
    parser.add_argument('-S', '--system-prompt', 
                       type=str,
                       help='Specify the system prompt')
    parser.add_argument('--stream', 
                       dest='stream',
                       action='store_true',
                       help='Enable stream mode (default)')
    parser.add_argument('--no-stream',
                       dest='stream', 
                       action='store_false',
                       help='Disable stream mode')
    parser.set_defaults(stream=True)
    parser.add_argument('-P', '--profile',
                        type=str,
                        help='Specify the profile to use')
    parser.add_argument('--json',
                        type=str,
                        default=None,
                        help='The JSON Schema for the result, implies --no-stream')
    parser.add_argument('--file',
                       type=str,
                       help='Read text from a file and append to the prompt')
    parser.add_argument('--model',
                       type=str,
                       default=None,
                       help='Specify the model to use(Overrides the profile)')
    parser.add_argument('-A', '--attach',
                       type=str,
                       action='append',
                       help='Add a file as attachment')
    parser.add_argument('--list',
                        nargs='?',
                        type=str,
                        default=None,
                        const=True,
                        help='List available profiles with optional prefix specified')
    parser.add_argument('--inspect',
                        type=str,
                        help='Inspect a profile.')
    parser.add_argument('-e', '--extract-code-block',
                        nargs='?',
                        type=str,
                        default=None,
                        const=True,
                        help='Extract last code block matched from the resposne, with optional language specified, implies --no-stream')
    parser.add_argument('-o', '--operation',
                        type=str,
                        action=util.DeprecatedAction,
                        deprecated='Deprecated, use `paipe op` instead',
                        help='Perform a specific operation')
    parser.add_argument('--usage',
                        action='store_true',
                        help='Show usage information in stderr.')
    parser.add_argument('prompt',
                       nargs='*',
                       type=str,
                       default='',
                       help='The prompt to process')


def build_parser(with_sub_parser: bool, default_call_parser: bool) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='paipe',
                                     description='A CLI tool for accessing the LLM API in the terminal.')

    if with_sub_parser:
        sub_parsers = parser.add_subparsers(dest='command',
                                            title=' Commands',
                                            metavar='',
                                            help='')
        call_parser = sub_parsers.add_parser('call', help='Default command(`call` can be skiped), directly call an LLM API.')
        build_call_parser(call_parser)
        command_parser = sub_parsers.add_parser('op', help='Perform a specific operation')
        from .operations.subcli import build_command_parser
        build_command_parser(command_parser)

    # Bind sub parser 'call' as root parser 
    if default_call_parser:
        build_call_parser(parser)

    parser.add_argument('-v', '--verbose',
                       action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--version',
                       action='store_true',
                       help='Show version information and quit')
    return parser


def parse_args(cmd_args: list) -> argparse.Namespace:
    # Only deal with global args
    if (set(cmd_args) & set(GLOBAL_ACTION_ARGS) != set()):
        parser = build_parser(True, True)
        args = parser.parse_args(cmd_args)
    else:
        # if --help is here, it will be parsed by global parser
        parser = build_parser(False, True)
        args, __ = parser.parse_known_args(cmd_args)
        # Check if the first argument is a sub command
        if (args.prompt and args.prompt[0] in SUB_COMMANDS):
            parser = build_parser(True, False)
            args = parser.parse_args(cmd_args)
    return args


def handle_global_args(args: argparse.Namespace):
    if args.verbose:
        util.set_verbose(True)
    else:
        util.set_verbose(False)
    if args.version:
        from . import __version__
        print(f'paipe {__version__}')
        sys.exit(0)


def handle_call(args):
    if args.list:
        profiles = list_profiles(args.list)
        sys.exit(0)
    if args.inspect:
        inspect_profile(args.inspect)
        sys.exit(0)
    context_dict = {
        'stream': args.stream,
        'prompt': ' '.join(args.prompt),
        'json_schema': args.json,
        'extract_code_block': args.extract_code_block,
        'model': args.model,
        'attachments': [],
        'usage': args.usage,
    }
    if args.file:
        with open(args.file, 'r') as f:
            context_dict['input_text'] = f.read()
    elif not sys.stdin.isatty():
            context_dict['input_text'] = sys.stdin.read()
    else:
        if not context_dict['prompt']:
            print('No prompt or input via stdin or a file with --file provided')
            sys.exit(1)        

    if args.profile:
        context_dict['profile'] = args.profile

    if args.system_prompt:
        context_dict['system_prompt'] = args.system_prompt
    else:
        context_dict['system_prompt'] = None

    if args.attach:
        context_dict['attachments'].extend(util.to_attachment_pairs(args.attach))

    if args.operation:
        from .operations import handle_operation
        handle_operation(args.operation, context_dict)
    else:
        context = PaipeContext.model_validate(context_dict)
        asyncio.run(run_agent(context))


def main():
    args = parse_args(sys.argv[1:])
    handle_global_args(args)
    if getattr(args, 'command', None) is None or args.command == 'call':
        handle_call(args)
    elif args.command == 'op':
        from .operations.base import handle_operation
        handle_operation(args)
    else:
        print(f'Unknown command: {args.command}')
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        util.logger.exception(e)
        print(f'Error: {dir(e)}')
        if hasattr(e, 'body'):
            util.logger.error(e.body)