import argparse
import sys # Ensure sys is imported
from .call import run_mcp_call

def build_mcp_parser(mcp_parser: argparse.ArgumentParser):
    """
    Builds the argument parser for the MCP subcommand.
    """
    # Add subparsers for mcp subcommands, e.g., 'call'
    # Make mcp_command required
    sub_parsers = mcp_parser.add_subparsers(dest='mcp_command',
                                            title='MCP Commands',
                                            metavar='',
                                            help='Use `paipe mcp <command> --help` for more information on a command.',
                                            required=True)

    # MCP 'call' subcommand
    call_parser = sub_parsers.add_parser('call', help='Call a tool from a script.')
    call_parser.add_argument('script_path',
                             type=str,
                             help='The script path (e.g., xxxx.py or xxx.py:mcp)')
    call_parser.add_argument('tool_name',
                             type=str,
                             help='The tool name')
    call_parser.add_argument('tool_args',
                             type=str,
                             help='The tool arguments string')

def handle_mcp_command(args: argparse.Namespace):
    """
    Handles the MCP subcommands.
    """
    if args.mcp_command == 'call':
        run_mcp_call(args.script_path, args.tool_name, args.tool_args)
    else:
        print(f"Unknown MCP command: {args.mcp_command}")
        # Optionally, print help or exit with an error code
        # mcp_parser.print_help() # This would require passing mcp_parser or making it accessible
        sys.exit(1)
