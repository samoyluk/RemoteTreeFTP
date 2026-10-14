from helper import *
cmd = m.RemoteTreeFtpSettingsCommand()
commands = []
cmd.window = types.SimpleNamespace(run_command=lambda name, args: commands.append((name, args)))
state['profiles'] = [{'host': 'existing.example'}]
cmd.run()
name, args = commands[-1]
assert name == 'edit_settings'
assert args['base_file'] == '${packages}/RemoteTreeFTP/RemoteTreeFTP.sublime-settings'
assert state['profiles'][0]['host'] == 'existing.example'
print('PASS: resource-aware split settings and profile preservation')
