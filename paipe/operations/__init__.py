from . import filelist


def handle_operation(operation, context_dict):
    if operation == 'filelist-to-md':
        print(filelist.stdin_to_markdown(context_dict['input_text']))
    else:
        print(f'Unknown operation: {operation}')
