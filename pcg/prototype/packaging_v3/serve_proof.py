"""Local same-origin proof server; never changes the hosting repository."""
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from pathlib import Path
import argparse,urllib.parse
p=argparse.ArgumentParser();p.add_argument('--proof',type=Path,required=True);p.add_argument('--port',type=int,default=8042);a=p.parse_args()
proof=a.proof.resolve();site=Path('/workspace/pcg-preview-host/site').resolve()
class Handler(SimpleHTTPRequestHandler):
    def translate_path(self,path):
        path=urllib.parse.unquote(urllib.parse.urlsplit(path).path)
        if path.startswith('/gunman-rush-previews/'):
            root=site;rel=path[len('/gunman-rush-previews/'):]
        else:root=proof;rel=path.lstrip('/')
        candidate=(root/rel).resolve()
        if candidate!=root and root not in candidate.parents:return str(root/'__blocked__')
        return str(candidate)
ThreadingHTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
