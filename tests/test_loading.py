from helper import *
listener=m.RemoteTreeFtpListener()
class Session:
 def __init__(self):self.file_states={};self.renders=0
 def owns(self,v):return {'path':'/test.txt'}
 def render(self):self.renders+=1
session=Session();listener.session_for=lambda v:session
class View:
 def is_loading(self):return self.loading
 def is_dirty(self):return self.dirty
v=View()
for loading,dirty in [(True,False),(True,True),(False,False)]:
 v.loading=loading;v.dirty=dirty;listener.on_modified(v);assert session.file_states=={}
v.loading=False;v.dirty=True;listener.on_modified(v);assert session.file_states['/test.txt']=='modified';assert session.renders==1
listener.on_modified(v);assert session.renders==1
print('PASS: loading and clean buffers ignored; actual edits marked; repeated edits do not redraw')
