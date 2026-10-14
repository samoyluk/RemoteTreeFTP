"""Build only distributable files; never include user data or development files."""
from pathlib import Path
import zipfile
import ast
import json

ROOT = Path(__file__).resolve().parents[1]
FILES = [".python-version", "remote_tree_ftp.py", "keychain.py", "Main.sublime-menu",
         "Default.sublime-commands", "RemoteTreeFTP.sublime-settings", "README.md",
         "README.ru.md", "LICENSE", "CHANGELOG.md", "VERSION"]
for name in FILES:
    text = (ROOT / name).read_text(encoding="utf-8")
    if name.endswith(".py"):
        ast.parse(text)
    if name.endswith((".sublime-menu", ".sublime-commands", ".sublime-settings")):
        json.loads(text)
out = ROOT / "build" / "RemoteTreeFTP.sublime-package"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for name in FILES:
        archive.write(ROOT / name, name)
with zipfile.ZipFile(out) as archive:
    assert archive.testzip() is None
print(out)
