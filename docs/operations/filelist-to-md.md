# Operation filelist-to-md

The `filelist-to-md` operation is designed to convert a list of file paths, provided through standard input, into a markdown document that includes the contents of each file. This process involves reading the file paths, extracting their contents, and formatting them into a markdown document.

### Usage

To utilize the `filelist-to-md` operation, ensure the following steps are followed:

1. **Prepare the File List:**
   - Create a list of file paths that you want to convert into a markdown document.
   - This list should be provided as a single string where each file path is separated by a space or a newline.
   - You may create the list by commands like `ls` or `find -name"src/*.py"`.

2. **Run the CLI with the Operation:**
   - Use the `paipe -o filelist-to-md` or `paipe --operation filelist-to-md` and take stdin as input.

### Examples

```sh
echo "file1.txt file2.txt file3.txt" | paipe -o filelist-to-md | paipe "Summarize the contents of the files."

find -name *.py  | paipe -o filelist-to-md | paipe "Write a document for the project."

ls "*.conf" | paipe -o filelist-to-md | paipe "Anaalyze the configuration files, find unused configs."
```