from helper import *
s.windows=lambda:[];s.message_dialog=lambda msg:None
errors=[];s.error_message=errors.append
w=Window();a=m.Session(w,{'host':'test'},'');a.render=lambda:None
class FTP:
 def __init__(self):self.data={'/':{'a.txt':False,'dir':True},'/dir':{}};self.calls=[]
 def mlsd(self,path):return [(n,{'type':'dir' if d else 'file'}) for n,d in self.data[path].items()]
 def storbinary(self,cmd,stream):
  path=cmd[5:];self.data['/'][path[1:]]=False;self.calls.append(('create',path,stream.read()))
 def mkd(self,path):self.data['/'][path[1:]]=True;self.data[path]={}
 def rename(self,old,new):self.data['/'][new[1:]]=self.data['/'].pop(old[1:]);self.calls.append(('rename',old,new))
 def delete(self,path):del self.data['/'][path[1:]];self.calls.append(('delete',path))
 def rmd(self,path):
  if self.data[path]:raise ftplib.error_perm('550 not empty')
  del self.data[path];del self.data['/'][path[1:]]
f=FTP()
def work(action,done,on_error=None):
 try:result=action(f)
 except Exception as e:errors.append(str(e));return
 done(result)
a.work=work
a.mutate('file','/',True,'new.txt');assert 'new.txt' in f.data['/']
count=len(f.calls);a.mutate('file','/',True,'a.txt');assert len(f.calls)==count and errors
for name in ['../oops','a/b','a\\b','..','bad\r\nDELE x','']:
 a.mutate('file','/',True,name)
assert len(f.calls)==count
a.mutate('folder','/',True,'newdir');assert f.data['/']['newdir']
a.mutate('rename','/new.txt',False,'renamed.txt');assert 'renamed.txt' in f.data['/'] and 'new.txt' not in f.data['/']
a.mutate('delete','/renamed.txt',False);assert 'renamed.txt' not in f.data['/']
f.data['/dir']['keep.txt']=False;a.mutate('delete','/dir',True);assert '/dir' in f.data
count=len(f.calls);a.mutate('delete','/',True);assert len(f.calls)==count
a.pending=1;a.mutate('file','/',True,'blocked.txt');assert 'blocked.txt' not in f.data['/'];a.pending=0
class V:
 def settings(self):return Settings(remote_tree_ftp={'path':'/a.txt'})
class W:
 def id(self):return 10
 def views(self):return [V()]
s.windows=lambda:[W()];m.SESSIONS[10]=a
assert not a.can_mutate('/a.txt',True)
m.SESSIONS.clear();s.windows=lambda:[]
# Confirm cancel does not delete anything.
a.entries={'/':[('a.txt',False)]};w.show_quick_panel=lambda labels,callback:setattr(w,'choose',callback)
s.ok_cancel_dialog=lambda *args:False
a.context_menu('/a.txt');w.choose(6);assert 'a.txt' in f.data['/']
a.pool.shutdown();shutil.rmtree(a.cache)
print('PASS: create, rename, delete, collisions, invalid names, nonempty folder, root protection, pending/open-file guard, cancelled deletion')
