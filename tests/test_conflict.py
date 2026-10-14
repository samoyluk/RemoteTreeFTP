from helper import *
import hashlib
w=Window();a=m.Session(w,{'host':'test'},'');a.render=lambda:None;a.backup_folder=lambda path:str(pathlib.Path(a.cache)/'backups')
class View:
 def __init__(self):
  self.p=str(pathlib.Path(a.cache)/'file.txt');pathlib.Path(self.p).write_bytes(b'local');self.s=Settings(remote_tree_ftp={'session':id(a),'local':self.p,'path':'/file.txt'})
 def settings(self):return self.s
 def file_name(self):return self.p
 def change_count(self):return 1
 def is_dirty(self):return False
 def set_status(self,*a):pass
v=View();jobs=[];a.work=lambda action,done,on_error=None:jobs.append((action,done,on_error));menus=[];a.conflict_menu=lambda *args:menus.append(args)
class FTP:
 def __init__(self,data):self.data=data;self.writes=0
 def retrbinary(self,cmd,write):write(self.data)
 def storbinary(self,cmd,stream):self.data=stream.read();self.writes+=1
hashof=lambda b:hashlib.sha256(b).hexdigest()
a.remote_hashes['/file.txt']=hashof(b'original');f=FTP(b'original');a.upload(v);act,done,_=jobs.pop();done(act(f));assert f.data==b'local' and a.remote_hashes['/file.txt']==hashof(b'local')
f.data=b'foreign';a.upload(v);act,done,_=jobs.pop();done(act(f));assert f.writes==1 and a.file_states['/file.txt']=='conflict' and len(menus)==1
# Confirmation is tied to the server bytes that were shown.
f.data=b'new foreign';a.upload(v,expected_remote=hashof(b'foreign'));act,done,_=jobs.pop();done(act(f));assert f.writes==1 and a.file_states['/file.txt']=='conflict'
a.upload(v,expected_remote=hashof(b'new foreign'));act,done,_=jobs.pop();done(act(f));assert f.writes==2 and f.data==b'local'
# Matching bytes are already synchronized, no redundant write.
a.upload(v);act,done,_=jobs.pop();done(act(f));assert f.writes==2
# Missing baseline fails closed when remote differs.
a.remote_hashes.clear();f.data=b'unknown';a.upload(v);act,done,_=jobs.pop();done(act(f));assert f.writes==2 and a.file_states['/file.txt']=='conflict'
# Read failure never reaches STOR.
class Broken(FTP):
 def retrbinary(self,*args):raise ftplib.error_perm('550 missing')
a.upload(v);act,done,failed=jobs.pop();broken=Broken(b'')
try:act(broken);raise AssertionError()
except ftplib.error_perm as e:failed(str(e))
assert broken.writes==0 and a.file_states['/file.txt']=='error'
a.pool.shutdown();shutil.rmtree(a.cache)
print('PASS: unchanged server upload; conflict blocks STOR; confirmed overwrite rechecks; identical bytes skip STOR; unknown baseline and read errors cannot overwrite')
