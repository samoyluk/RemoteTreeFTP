# RemoteTreeFTP

A browsable FTP/FTPS file tree for Sublime Text 4, inspired by the workflow of NppFTP.
Open remote files, edit them beside the tree, and upload changes with conflict checks
and local backups.

[Русская инструкция](README.ru.md) · [Releases](https://github.com/samoyluk/RemoteTreeFTP/releases)

## Requirements

- Sublime Text 4, build 4107 or newer.
- macOS is the initial supported platform. Windows/Linux are not yet validated.
- An FTP or **explicit FTPS** account. SFTP and implicit FTPS are not supported.
- Package Control for the recommended installation method.

## Install

### Through Package Control before catalog acceptance

1. In Sublime Text, open **Tools → Install Package Control** if Package Control is not installed.
2. Press **Cmd+Shift+P**, choose **Package Control: Add Repository**, and paste:
   ```text
   https://github.com/samoyluk/RemoteTreeFTP
   ```
3. Open the command palette again and choose **Package Control: Install Package**.
4. Search for **RemoteTreeFTP** and select it.
5. Restart Sublime Text. Open **File → RemoteTreeFTP**.

The public repository and a release tag must exist for these steps to work.
The package is not yet accepted into the default catalog. Once accepted,
you can skip Add Repository and install it directly by name.

### Manual installation on macOS

1. Download **RemoteTreeFTP.sublime-package** from [Releases](https://github.com/samoyluk/RemoteTreeFTP/releases/latest).
   Use the package asset, not GitHub's “Source code” ZIP.
2. Quit Sublime Text with **Cmd+Q**.
3. In Finder, press **Cmd+Shift+G** and enter:
   ```text
   ~/Library/Application Support/Sublime Text/Installed Packages/
   ```
4. Copy **RemoteTreeFTP.sublime-package** into this folder. Choose **Replace** when updating.
5. Start Sublime Text. The **File → RemoteTreeFTP** menu should appear.

Do not double-click the package. Copy it into **Installed Packages**, not **Packages**.
For a portable or nonstandard Sublime installation, use **Browse Packages**,
go one folder up, and locate **Installed Packages** there.

### Existing manual installations

Keep your `User/RemoteTreeFTP.sublime-settings` file: it holds your profiles and language.
If you previously unpacked the plugin into `Packages/RemoteTreeFTP`, that directory
can override the installed archive. Move only that plugin directory outside Packages
before switching installation methods. Do not remove the User directory or other plugins.
Package Control handles subsequent updates once it manages the installation.

## First connection

1. Choose **File → RemoteTreeFTP → Language / Язык → English** if needed.
2. Choose **Add Server…** and enter a name, host, username, port, starting folder,
   protocol, and upload mode. Typical FTP/explicit FTPS port: `21`.
3. Choose **Connect…**, select the server and enter its password.
4. On macOS, optionally save the password in Keychain, or use it only for this session.
5. A separate Sublime window opens: folders on the left, file editor on the right.

Use **Edit Server…** to edit a profile and **Connect with Another Password…** to replace
an old password. Profiles are preserved when you update the plugin.

## Working with files

- Click a folder to expand/collapse it. Expanded folders are remembered per connection.
- Click a file to download and open it. Its server path is shown in the status bar.
- With upload on save enabled, **Cmd+S** saves locally and uploads to the server.
- For manual mode, save locally and choose **File → RemoteTreeFTP → Upload Current File**.
- File badges distinguish modified, uploading, uploaded, failed and conflicting states.
- Click **⋯** for creation, rename, deletion, path copying, permissions and version history.
- Click a permissions badge to enter numeric modes such as `644`, `755` or `777`.
  Only the selected item is changed; there is no recursive chmod.
- **Refresh Tree** rereads expanded folders. **Disconnect** stops further queued operations;
  an already running transfer may complete.

The tree occupies an editor group; it is not Sublime's native sidebar. Standard tab
hover text shows the local working path, which includes the remote directory structure.
No default keyboard shortcuts or native right-click menu entries are added.

## Conflicts and backups

Before uploading, the plugin rereads the server file and checks it against the downloaded
version. A conflict offers cancellation, a text comparison, or an explicitly confirmed
overwrite. FTP cannot make checking and writing atomic: another client can still modify
a file in the short interval between these operations.

Before overwriting, the previous server contents are backed up locally. If backup creation
fails, the upload stops. The latest **10 copies per file and connection** are retained.
Backups are made before uploads, not before deletion.

Choose **⋯ → Version history…** to view a backup, compare it with the server, or restore
it into a separate editable working copy. **Restored copies never upload automatically**,
even on Cmd+S. Review them, save, and use **Upload Current File** explicitly.
Restoring a deleted server file is not supported. Text comparison supports UTF-8 files;
binary/non-UTF-8 files still receive byte-level conflict checks.

## Settings and local storage

**Settings (File)…** opens defaults on the left and user settings on the right.
Edit only the right-hand side. You can use the wizard instead of editing JSON.

```json
{
    "language": "en",
    "profiles": [
        {
            "name": "My server",
            "host": "ftp.example.com",
            "port": 21,
            "protocol": "ftps",
            "username": "my-login",
            "remote_path": "/www",
            "encoding": "utf-8",
            "passive": true,
            "upload_on_save": true
        }
    ]
}
```

Passwords are not written to the profile file. macOS may ask for Keychain access.
The standard Sublime password input is not guaranteed to mask characters.
FTP is unencrypted; explicit FTPS validates the server certificate.

Profiles: `Packages/User/RemoteTreeFTP.sublime-settings`.
Tree state: `Packages/User/RemoteTreeFTP-tree.sublime-settings`.
Backups: `RemoteTreeFTP Backups` beside Packages and Installed Packages, normally
`~/Library/Application Support/Sublime Text/RemoteTreeFTP Backups/`.
Backups are not encrypted, have no overall size limit, and remain associated with their
old path after remote rename. Working copies remain in system temporary folders named
`RemoteTreeFTP-*`; they are not automatically deleted, to preserve unsent edits.

## Troubleshooting

- **No menu:** check that the archive is in Installed Packages, restart, and look for
  `RemoteTreeFTP` in Sublime's console errors. Check `ignored_packages` and unpacked overrides.
- **Permissions show “—”:** the server did not report Unix mode information. This does
  not mean `000`. Changing permissions requires server support for `SITE CHMOD`.
- **Connection failure:** check host, port, protocol, login, starting folder and passive mode.
  SFTP accounts require a different client.
- **Old password:** choose **Connect with Another Password…**. Old Keychain entries can
  be removed in macOS Keychain Access by searching for RemoteTreeFTP.
- **Upload failure:** your saved local copy is retained. Fix the connection and retry manually.

Report issues at [GitHub Issues](https://github.com/samoyluk/RemoteTreeFTP/issues).
Include the plugin version, Sublime build, macOS version and sanitized error text.
Do not attach passwords or confidential server contents.

## Development and verification

```sh
python3 tools/test.py
python3 tools/build.py
```

The suite uses a simulated Sublime API and FTP objects; it is not an end-to-end test
of the real editor, server or Keychain dialogs. See [PUBLISHING.md](PUBLISHING.md)
for the manual release checklist. Tests and maintainer files are excluded from packages.

MIT license. Maintained by [samoyluk](https://github.com/samoyluk).
