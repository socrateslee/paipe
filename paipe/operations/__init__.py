from . import archive


def handle_operation(operation, context_dict):
    if operation == 'filelist-to-md':   
        print(archive.archive(context_dict['input_text']))
    else:
        print(f'Unknown operation: {operation}')
