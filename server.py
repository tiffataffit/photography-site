#!/usr/bin/env python3
"""
Local dev server for upload.html.
Run: python3 server.py
Then open: http://localhost:8765/upload.html
"""
import http.server, subprocess, json, os

ROOT = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        if self.path == '/git-push':
            self._run(['git', 'add', '.'])
            commit = self._run(['git', 'commit', '-m', 'Update photos'])
            push = self._run(['git', 'push'])
            ok = push['code'] == 0
            msg = push['out'] or push['err'] or commit['out'] or 'Nothing to push.'
            self._json({'ok': ok, 'msg': msg.strip()})

        elif self.path == '/deploy':
            result = self._run(['/opt/homebrew/bin/gh', 'workflow', 'run', 'deploy.yml'])
            ok = result['code'] == 0
            self._json({'ok': ok, 'msg': (result['out'] or result['err'] or 'Deployed.').strip()})

        else:
            self.send_error(404)

    def _run(self, cmd):
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        return {'code': r.returncode, 'out': r.stdout, 'err': r.stderr}

    def _json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # suppress request logs

if __name__ == '__main__':
    server = http.server.HTTPServer(('localhost', 8765), Handler)
    print('Server running at http://localhost:8765/upload.html')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
