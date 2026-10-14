from helper import *
w=Window();a=m.Session(w,{'host':'test'},'');jobs=[]
a.work=lambda action,done,on_error=None:jobs.append((action,done,on_error))
a.expanded={'/','/one','/one/sub','/two'};a.browse('/one');assert a.expanded=={'/','/two'}
b=m.Session(w,{'host':'test'},'');b.work=a.work;b.restore()
class FTP:
 def mlsd(self,path):
  if path=='/two':raise ftplib.error_perm('550 missing')
  return [('file.txt',{'type':'file'})]
f=FTP();action,done,_=jobs.pop();done(action(f));assert b.expanded=={'/'}
class View:
 def __init__(self):
  self.p=str(pathlib.Path(a.cache)/'file.txt');pathlib.Path(self.p).write_bytes(b'content');self.s=Settings(remote_tree_ftp={'session':id(a),'local':self.p,'path':'/file.txt'});self.revision=1;self.dirty=False
 def settings(self):return self.s
 def file_name(self):return self.p
 def change_count(self):return self.revision
 def is_dirty(self):return self.dirty
 def set_status(self,*args):pass
v=View();a.upload(v);old=jobs.pop();assert a.file_states['/file.txt']=='uploading'
v.revision=2;v.dirty=True;old[1]({'sent': True});assert a.file_states['/file.txt']=='modified'
v.dirty=False;a.upload(v);old=jobs.pop();a.upload(v);new=jobs.pop();old[1]({'sent': True});assert a.file_states['/file.txt']=='uploading';new[2]('failure');assert a.file_states['/file.txt']=='error'
a.upload(v);jobs.pop()[1]({'sent': True});assert a.file_states['/file.txt']=='sent'
a.expanded={'/'};a.entries={'/':[('file.txt',False)]};a.active_path='/file.txt';a.render();assert 'entry selected' in a.sheet.content and '✓ на сервере' in a.sheet.content and '&amp;quot;' not in a.sheet.content
v.p+='other';a.upload(v);assert not jobs
for session in (a,b):session.pool.shutdown();shutil.rmtree(session.cache)
print('PASS: tree persistence, collapsed descendants, missing folder, modified during upload, stale completion, upload failure/success, highlight and Save As isolation')
