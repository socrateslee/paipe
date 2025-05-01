# Use the content in the clipboard

## In Linux

In Linux, you can use tools like `xclip` to get the content in the clipboard and pipe it to `paipe`:

```bash
xclip -o -selection clipboard | paipe "How to solve the error:"
```


## In Powershell and WSL
In Powershell, you may use the `Get-Clipboard` command to get the content in the clipboard and pipe it to `paipe`:

```
Get-Clipboard | paipe "How to solve the error:"
```

Or in WSL, you can simply call Powershell and use the `Get-Clipboard` command:

```bash
pwsh.exe -c Get-Clipboard | paipe "How to solve the error:"
```
