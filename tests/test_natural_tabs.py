from helper import *
class V:
 def __init__(self):self.s=Settings(remote_tree_ftp={'path':'/www/dataxe.ru/bad_asn/bad_provider.php','local':'/tmp/a'});self.status={};self.dirty=False
 def settings(self):return self.s
 def file_name(self):return '/tmp/a'
 def set_name(self,name):raise AssertionError('must not rename disk-backed buffers')
 def set_status(self,k,v):self.status[k]=v
v=V();w=types.SimpleNamespace(views=lambda:[v]);m.refresh_tab_names(w);m.refresh_tab_names(w);assert not v.dirty;assert v.status['remote_tree_ftp_path']=='FTP: /www/dataxe.ru/bad_asn/bad_provider.php'
assert m.working_file('/tmp/cache','/www/site/file.php')=='/tmp/cache/server/www/site/file.php'
for path in ['/../escape','/a/../escape','/a//b','/a\nDELE x']:
 try:m.working_file('/tmp/cache',path);raise AssertionError(path)
 except ValueError:pass
print('PASS: repeated activation never changes buffer name, server path retained, readable working paths, traversal rejection')
