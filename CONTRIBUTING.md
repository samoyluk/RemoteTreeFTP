# Contributing

Use Sublime Text 4 on macOS for editor checks. Clone this repository as RemoteTreeFTP
under Packages only for development; remove duplicate packed installs during testing.

Run `python3 tools/test.py` and `python3 tools/build.py` before submitting changes.
The regression suite uses stubs; also test relevant changes in the real editor.
Keep user data, passwords, downloaded server files and machine-specific paths out of commits.
Preserve both UI languages and their format placeholders. Avoid default key bindings
and native context-menu entries. Report problems via GitHub Issues with sanitized errors.
