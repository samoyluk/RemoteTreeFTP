from helper import *
messages=[];s.message_dialog=messages.append
class WizardWindow:
 def show_input_panel(self,caption,value,callback,*a):self.caption=caption;self.value=value;self.input=callback
 def show_quick_panel(self,items,callback,**kw):self.items=items;self.pick=callback
w=WizardWindow();cmd=m.RemoteTreeFtpProfileCommand();cmd.window=w
state['profiles']=[{'name':'old','host':'old.host','port':21,'username':'u','passive':False}]
cmd.run()
for value in ['New','ftp.example.com','me','2121','www']:w.input(value)
w.pick(1);w.pick(0)
assert len(state['profiles'])==2 and state['profiles'][1]['remote_path']=='/www' and state['profiles'][1]['protocol']=='ftps'
cmd.run(edit=True);w.pick(0)
for value in ['Renamed','old.host','u','21','/']:w.input(value)
w.pick(0);w.pick(1)
assert state['profiles'][0]['passive'] is False and state['profiles'][0]['upload_on_save'] is False
before=list(state['profiles']);cmd.run();w.input('cancelled');assert state['profiles']==before
for key in state['profiles'][0]:assert key not in ('password',)
# The keychain lookup must not depend on profile name or directory.
spec=importlib.util.spec_from_file_location('kc','lib/keychain.py');kc=importlib.util.module_from_spec(spec);spec.loader.exec_module(kc)
p={'host':'HOST','username':'u'};assert kc.account(p)==kc.account(dict(p,name='renamed',remote_path='/other'))
assert kc.account(p)!=kc.account(dict(p,username='other'))
print('PASS: add/edit profiles, preserve advanced fields, cancel without save, no password settings, keychain account isolation')
