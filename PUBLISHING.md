# Release and Package Control checklist

## Verification status

Automated regression tests cover backups, conflicts, file operations, localization,
permissions, profiles, tab behavior, load events and split settings. They use test doubles.
The maintainer has used earlier versions in Sublime on macOS. A complete isolated
Package Control installation/update test and exhaustive real-server tests have not
been recorded for this release. Do not mark those tests complete without performing them.

## Before claiming a stable release

- Install with Package Control in a clean Sublime profile using Add Repository.
- Confirm that packed imports work and Settings opens defaults/user settings side by side.
- Test FTP and explicit FTPS on a disposable server; do not use production files.
- Open and immediately close a file; edit/save, disconnect, reconnect and retry a failed upload.
- Create, rename and delete disposable files/folders; change/read numeric permissions.
- Change the server file externally and confirm that upload stops with a conflict.
- Review/restore a backup and confirm Cmd+S does not auto-upload restored copies.
- Test English/Russian, Keychain access/refusal, and upgrading with existing user settings.
- Record editor build, OS and server versions and results in the release notes.

## Publish a release

1. Update VERSION, CHANGELOG.md and relevant documentation.
2. Run `python3 tools/test.py` and `python3 tools/build.py`.
3. Commit all public source files; create a semantic version tag (initial tag: 0.1.0).
4. Push the tag; publish a GitHub release with build/RemoteTreeFTP.sublime-package attached.
5. Do not move an already published tag. Use a new version for fixes.

`.gitattributes` excludes tests and maintainer files from Package Control's git archive.
The explicit build script excludes them from the manual release asset too.

## Submit to Package Control

Fork https://github.com/sublimehq/package_control_channel and add this entry in
alphabetical order to `repository/r.json`:

```json
{
    "name": "RemoteTreeFTP",
    "details": "https://github.com/samoyluk/RemoteTreeFTP",
    "labels": ["utilities"],
    "releases": [
        {"sublime_text": ">=4107", "platforms": ["osx"], "tags": true}
    ]
}
```

Follow the current checklist at
https://github.com/sublimehq/package_control_channel/blob/master/.github/PULL_REQUEST_TEMPLATE.md
and the guide at https://docs.sublimetext.io/guide/package-control/submitting.html .
Only claim checkboxes supported by actual verification. A submission does not mean acceptance.

Suggested description:

RemoteTreeFTP adds a persistent FTP/explicit FTPS tree in a dedicated editor group,
with numeric chmod, remote-content conflict checks, local pre-upload version history,
and English/Russian UI. It targets the NppFTP-style browsing workflow and complements
existing transfer/sync packages. macOS is the initial supported platform. No default
key bindings or native context-menu entries are added; file actions live inside its tree.
