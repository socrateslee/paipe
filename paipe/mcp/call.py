import subprocess
import json
import sys

def parse_tool_args(tool_args_str: str) -> dict:
    """
    Parses the tool arguments string (e.g., 'key1=value1;key2=value2') into a dictionary.
    """
    if not tool_args_str:
        return {}
    
    args_dict = {}
    try:
        pairs = tool_args_str.split(';')
        for pair in pairs:
            if not pair:  # Handle empty strings that might result from trailing semicolons
                continue
            if '=' not in pair:
                raise ValueError(f"Invalid argument format: '{pair}'. Expected 'key=value'.")
            key, value = pair.split('=', 1)
            args_dict[key.strip()] = value.strip()
    except ValueError as e:
        print(f"Error parsing tool arguments: {e}", file=sys.stderr)
        # Or raise a custom exception, for now, returning partial or empty dict
        # For robustness, decide if to proceed with partially parsed args or fail completely
        return {} # Or raise e
    return args_dict

def run_mcp_call(script_path: str, tool_name: str, tool_args_str: str):
    """
    Executes a tool in a target script using the Machine-readable Communication Protocol (MCP).

    Args:
        script_path: Path to the Python script to execute (e.g., xxxx.py).
        tool_name: The name of the tool to call within the script.
        tool_args_str: A string of tool arguments in the format 'key1=value1;key2=value2'.
    """
    try:
        inputs = parse_tool_args(tool_args_str)
    except Exception as e: # Catching potential errors from parse_tool_args if it re-raises
        print(f"Failed to parse tool arguments: {e}", file=sys.stderr)
        sys.exit(1)

    request_data = {
        "tool_name": tool_name,
        "inputs": inputs
    }
    json_request_string = json.dumps(request_data)

    # For now, script_path is assumed to be just the path to the python script.
    # e.g., xxxx.py. Enhancements for xxxx.py:mcp_server_name can be added later.

    try:
        process = subprocess.Popen(
            ['python', script_path], # This will make Python exit with 2 if script_path is not found
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=json_request_string)

        # Attempt to parse stdout as JSON first, as the script might provide a JSON error response
        # even if it exits with a non-zero code.
        if stdout:
            try:
                response_json = json.loads(stdout)
                print(json.dumps(response_json, indent=2))
            except json.JSONDecodeError:
                # If stdout is not empty but not JSON, print error and the raw output
                print(f"Error: Could not decode JSON response from script '{script_path}'.", file=sys.stderr)
                print(f"Raw stdout from script:\n{stdout}", file=sys.stderr)
                # If the script also had an error exit code, we'll exit with that.
                # Otherwise, exit with 1 to indicate this JSON decode problem.
                if process.returncode == 0:
                    sys.exit(1) 
        elif process.returncode != 0: 
            # if stdout is empty and there's an error code, it's likely a script crash before JSON output
            print(f"Error executing script '{script_path}'. No JSON output received.", file=sys.stderr)

        if process.returncode != 0:
            print(f"Script '{script_path}' exited with code {process.returncode}.", file=sys.stderr)
            if stderr: # Print script's stderr if any
                print(f"Script stderr:\n{stderr}", file=sys.stderr)
            sys.exit(process.returncode) # Exit with the script's actual return code
        elif not stdout and process.returncode == 0:
            # Edge case: script exited 0 but sent no stdout. This is unusual for MCP.
            print(f"Warning: Script '{script_path}' exited successfully but produced no output.", file=sys.stderr)


    except FileNotFoundError: # This covers if 'python' executable itself is not found
        print(f"Error: Python executable not found. Please ensure Python is installed and in PATH.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    # Example usage for testing run_mcp_call directly
    # Create a dummy script for testing:
    # echo 'import sys, json; data = json.load(sys.stdin); print(json.dumps({"status": "success", "data_received": data}))' > /tmp/dummy_mcp_script.py
    print("Testing run_mcp_call...")
    # Test 1: Valid call
    print("\n--- Test 1: Valid Call ---")
    run_mcp_call("/tmp/dummy_mcp_script.py", "test_tool", "param1=value1;param2=value2")

    # Test 2: Empty tool_args_str
    print("\n--- Test 2: Empty tool_args_str ---")
    run_mcp_call("/tmp/dummy_mcp_script.py", "another_tool", "")

    # Test 3: Tool args with spaces
    print("\n--- Test 3: Tool args with spaces ---")
    run_mcp_call("/tmp/dummy_mcp_script.py", "space_tool", "  param1 = value with spaces  ; param2=another value ")
    
    # Test 4: Malformed tool_args_str (will be handled by parse_tool_args and potentially exit)
    # print("\n--- Test 4: Malformed tool_args_str ---")
    # parse_tool_args("param1value1") # Test parse_tool_args directly for this case

    # Test 5: Script not found
    print("\n--- Test 5: Script not found ---")
    run_mcp_call("/tmp/non_existent_script.py", "test_tool", "param1=value1")
    
    # Test 6: Script errors (e.g., script prints non-JSON or exits with error)
    # echo 'import sys; print("This is not JSON"); sys.exit(1)' > /tmp/dummy_error_script.py
    print("\n--- Test 6: Script returns non-JSON and error code ---")
    run_mcp_call("/tmp/dummy_error_script.py", "error_tool", "p1=v1")

    # echo 'import sys, json; data = json.load(sys.stdin); print("this is not json")' > /tmp/dummy_nonjson_output_script.py
    print("\n--- Test 7: Script returns non-JSON output ---")
    run_mcp_call("/tmp/dummy_nonjson_output_script.py", "nonjson_tool", "p1=v1")
