"""Check packed subpackage imports and conventional settings discovery."""
from helper import *
import ast
import subprocess
import zipfile
from pathlib import Path
ROOT = Path.cwd()
subprocess.run([sys.executable, 'tools/build.py'], check=True)
archive_path = ROOT / 'build/RemoteTreeFTP.sublime-package'
with zipfile.ZipFile(archive_path) as archive:
    names = archive.namelist()
    assert 'lib/__init__.py' in names and 'lib/keychain.py' in names
    assert 'keychain.py' not in names
    tree = ast.parse(archive.read('remote_tree_ftp.py'))
    internal = [n for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.level]
    assert internal and all(n.module == 'lib.keychain' for n in internal)
# Simulate Sublime's package namespace using the actual packed archive.
package = types.ModuleType('RemoteTreeFTP')
package.__path__ = [str(archive_path)]
sys.modules['RemoteTreeFTP'] = package
import importlib
keychain = importlib.import_module('RemoteTreeFTP.lib.keychain')
assert keychain.account({'host': 'test', 'username': 'u'})
commands = json.loads((ROOT / 'Default.sublime-commands').read_text())
base = '${packages}/RemoteTreeFTP/RemoteTreeFTP.sublime-settings'
assert any(c.get('command') == 'edit_settings' and c.get('args', {}).get('base_file') == base for c in commands)
menu = json.loads((ROOT / 'Main.sublime-menu').read_text())
prefs = next(x for x in menu if x.get('id') == 'preferences')
packages = next(x for x in prefs['children'] if x.get('id') == 'package-settings')
settings = packages['children'][0]['children'][0]
assert settings['command'] == 'edit_settings' and settings['args']['base_file'] == base
print('PASS: packed internal imports and direct settings entries in palette/Preferences')
