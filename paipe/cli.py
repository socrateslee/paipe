'''
The command line interface (CLI).
'''
import sys
import argparse
import asyncio
import yaml
from pathlib import Path
from paipe import util
from paipe.models import PaipeContext
from paipe.profiles import list_profiles
from paipe.main import run_agent

util.patch_video_mimetype()


def parse_args():
    parser = argparse.ArgumentParser(description='Command line argument parser')
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
    parser.add_argument('-e', '--extract-code-block',
                        nargs='?',
                        type=str,
                        default=None,
                        const=True,
                        help='Extract last code block matched from the resposne, with optional language specified, implies --no-stream')
    parser.add_argument('-o', '--operation',
                        type=str,
                        help='Perform a specific operation')
    parser.add_argument('--usage',
                        action='store_true',
                        help='Show usage information in stderr.')
    parser.add_argument('-v', '--verbose',
                       action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--version',
                       action='store_true',
                       help='Show version information and quit')
    parser.add_argument('prompt',
                       nargs='?',
                       type=str,
                       default='',
                       help='The prompt to process')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.verbose:
        util.set_verbose(True)
    else:
        util.set_verbose(False)
    if args.list:
        profiles = list_profiles(args.list)
        sys.exit(0)
    elif args.version:
        from . import __version__
        print(f'paipe {__version__}')
        sys.exit(0)
    context_dict = {
        'stream': args.stream,
        'prompt': args.prompt,
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


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        util.logger.exception(e)
        if hasattr(e, 'body'):
            util.logger.error(e.body)