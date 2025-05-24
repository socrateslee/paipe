import json
import sys

def main():
    try:
        input_line = sys.stdin.readline()
        if not input_line:
            sys.stderr.write("Error: No input received from stdin.\n")
            sys.exit(1)
            
        request_data = json.loads(input_line)
        tool_name = request_data.get("tool_name")
        inputs = request_data.get("inputs", {})

        response = {}

        if tool_name == "echo_tool":
            response = {
                "status": "success",
                "result": inputs
            }
        elif tool_name == "error_tool":
            sys.stderr.write("Error: This is a simulated error from error_tool.\n")
            response = {
                "status": "error",
                "message": "error_tool was called and simulated an error."
            }
            print(json.dumps(response)) # Send response before exiting
            sys.exit(5) # Exit with a specific non-zero code for error_tool
        else:
            response = {
                "status": "error",
                "message": f"Unknown tool: {tool_name}"
            }
            # For unknown tools, we might still exit with 0 if the server itself didn't crash
            # Or choose a specific exit code. For now, let's assume it's not a server crash.
            print(json.dumps(response))
            sys.exit(0) # Or a different error code like 2 if unknown tool is a "failure"

        print(json.dumps(response))

    except json.JSONDecodeError:
        sys.stderr.write("Error: Invalid JSON input.\n")
        # Output a JSON error response as well, if the protocol requires it
        # This might be tricky if we can't even parse the request.
        # For now, just stderr and exit.
        # print(json.dumps({"status": "error", "message": "Invalid JSON input."}))
        sys.exit(3) # Specific exit code for JSON decode error
    except Exception as e:
        sys.stderr.write(f"An unexpected error occurred in dummy_mcp_server: {str(e)}\n")
        # print(json.dumps({"status": "error", "message": f"Unexpected server error: {str(e)}"}))
        sys.exit(4) # Specific exit code for other unexpected errors

if __name__ == "__main__":
    main()
