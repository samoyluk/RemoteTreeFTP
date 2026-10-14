from helper import *
s.status_message=lambda text:None
state['profiles']=[{'host':'keep.example'}]
cmd=m.RemoteTreeFtpLanguageCommand();cmd.window=types.SimpleNamespace()
cmd.run('en');assert state['language']=='en';assert state['profiles'][0]['host']=='keep.example';assert m.tr('● изменён')=='● modified';assert cmd.is_checked('en')
assert m.tr('Удалить {} с сервера?\n{}\n\nОтменить удаление нельзя.{}').format('file','/a','').startswith('Delete this file')
menu=m.RemoteTreeFtpMenuCommand();assert menu.description('remote_tree_ftp_connect','Подключиться…')=='Connect…'
cmd.run('ru');assert m.tr('● изменён')=='● изменён';assert menu.description('remote_tree_ftp_connect','Подключиться…')=='Подключиться…'
cmd.run('invalid');assert state['language']=='ru'
for ru,en in m.TRANSLATIONS.items():
 import string
 fields=lambda text:[field for _,field,_,_ in string.Formatter().parse(text) if field is not None]
 assert fields(ru)==fields(en),(ru,en)
print('PASS: both languages, menu captions, persistent preference, profile preservation, format placeholders')
