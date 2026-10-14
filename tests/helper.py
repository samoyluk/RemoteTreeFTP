import sys, types, importlib.util, tempfile, pathlib, shutil, json, html, ftplib
class Settings(dict):
 def set(self,k,v):self[k]=v
state=Settings();s=types.ModuleType('sublime');s.load_settings=lambda n:state;s.save_settings=lambda n:None;s.command_url=lambda c,a:'subl:'+html.escape(c+' '+json.dumps(a),quote=True);s.error_message=lambda m:None
sys.modules['sublime']=s
sp=types.ModuleType('sublime_plugin');sp.WindowCommand=type('WindowCommand',(),{});sp.EventListener=type('EventListener',(),{});sys.modules['sublime_plugin']=sp
spec=importlib.util.spec_from_file_location('p','remote_tree_ftp.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Sheet:
 def set_contents(self,c):self.content=c
class Window:
 def __init__(self):self.items=[]
 def is_valid(self):return True
 def sheets(self):return self.items
 def new_html_sheet(self,n,c,group=0):
  v=Sheet();v.content=c;self.items.append(v);return v
