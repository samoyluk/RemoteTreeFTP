from helper import *
assert m.numeric_mode('0755')=='755'
for invalid in ['888','66','7555x','777\r\nDELE x','-1','']:
 try:m.numeric_mode(invalid);raise AssertionError(invalid)
 except ValueError:pass
assert m.unix_list_modes(['-rw-rw-rw- 1 user group 12 Sep 13 12:00 file name.txt','drwxrwxrwx 2 u g 4096 Sep 13 2026 folder','-rwsr-Sr-t 1 u g 1 Sep 13 2026 special'])=={'file name.txt':'666','folder':'777','special':'7745'}
w=Window();a=m.Session(w,{'host':'test'},'')
class FTP:
 def mlsd(self,path):return [('folder',{'type':'dir','unix.mode':'0777'}),('file name.txt',{'type':'file','perm':'rw'})]
 def retrlines(self,cmd,cb):cb('-rw-rw-rw- 1 u g 1 Sep 13 12:00 file name.txt')
 def sendcmd(self,cmd):self.cmd=cmd;return '200 CHMOD successful'
f=FTP();rows=a.listing(f,'/');assert a.permissions['/folder']=='777';assert a.permissions['/file name.txt']=='666'
a.entries['/']=rows;a.expanded={'/'};a.render();assert 'class="mode"' in a.sheet.content and '>666</a>' in a.sheet.content
s.windows=lambda:[];s.message_dialog=lambda msg:None
w.show_input_panel=lambda caption,value,cb,*args:setattr(w,'accept',cb)
jobs=[];a.work=lambda action,done,on_error=None:jobs.append((action,done,on_error))
a.edit_permissions('/folder');w.accept('0755');action,done,_=jobs.pop();done(action(f));assert f.cmd=='SITE CHMOD 755 /folder' and a.permissions['/folder']=='755'
a.edit_permissions('/folder');w.accept('999');assert not jobs
class Denied(FTP):
 def sendcmd(self,cmd):raise ftplib.error_perm('550 denied')
a.edit_permissions('/folder');w.accept('777');action,done,_=jobs.pop()
try:action(Denied());raise AssertionError()
except ftplib.error_perm:pass
assert a.permissions['/folder']=='755'
a.pool.shutdown();shutil.rmtree(a.cache)
print('PASS: octal validation, UNIX LIST and MLSD parsing, clickable rights, CHMOD, rejected modes and server denial')
