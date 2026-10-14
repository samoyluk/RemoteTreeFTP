from helper import *
w=Window();a=m.Session(w,{'host':'test'},'');a.backup_folder=lambda path:str(pathlib.Path(a.cache)/'history');a.render=lambda:None
for i in range(12):a.save_backup('/x',str(i).encode())
files=sorted(pathlib.Path(a.backup_folder('/x')).glob('*.bak'));assert len(files)==10;assert [f.read_bytes() for f in files]==[str(i).encode() for i in range(2,12)]
assert not list(pathlib.Path(a.backup_folder('/x')).glob('.pending-*'))
class View:
 def __init__(self,path):self.path=path;self.s=Settings()
 def settings(self):return self.s
 def file_name(self):return self.path
 def set_status(self,*a):pass
 def change_count(self):return 1
 def is_dirty(self):return False
w.num_groups=lambda:2
opened=[]
def open_file(path,**kw):v=View(path);opened.append(v);return v
w.open_file=open_file
w.views=lambda:opened
jobs=[];a.work=lambda action,done,on_error=None:jobs.append((action,done,on_error))
class FTP:
 def __init__(self):self.writes=0
 def retrbinary(self,cmd,write):write(b'current')
 def storbinary(self,*args):self.writes+=1
f=FTP();a.restore_backup('/x',b'older');action,done,_=jobs.pop();done(action(f));v=opened[-1]
assert pathlib.Path(v.path).read_bytes()==b'older' and v.s['remote_tree_ftp']['manual_only'];assert f.writes==0
listener=m.RemoteTreeFtpListener();listener.session_for=lambda view:a
listener.on_post_save(v);assert not jobs and f.writes==0
# Backup error must abort before STOR.
def fail(*args):raise OSError('disk full')
a.save_backup=fail;a.upload(v);action,done,failed=jobs.pop()
try:action(f);raise AssertionError('should fail')
except OSError as e:failed(str(e))
assert f.writes==0 and a.file_states['/x']=='error'
a.pool.shutdown();shutil.rmtree(a.cache)
print('PASS: ten-copy retention, atomic files, exact restore bytes, no automatic restored upload, backup failure blocks STOR')
