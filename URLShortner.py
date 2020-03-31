import http.server
import requests
from urllib.parse  import parse_qs,unquote

memory={}
form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <label>Long URI:
        <input name="longuri">
    </label>
    <br>
    <label>Short name:
        <input name="shortname">
    </label>
    <br>
    <button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''
def CheckURI(uri, timeout=5):
    '''Check whether this URI is reachable, i.e. does it return a 200 OK?

    This function returns True if a GET request to uri returns a 200 OK, and
    False if that GET request returns any other response, or doesn't return
    (i.e. times out).
    '''
    try:
        r = requests.get(uri, timeout=timeout)
        # If the GET request returns, was it a 200 OK?
        return r.status_code == 200
    except requests.RequestException:
        # If the GET request raised an exception, it's not OK.
        return False

class Shortner(http.server.BaseHTTPRequestHandler):



    def do_GET(self):
        name=unquote(self.path[1:])

        if name:
            if name in memory:
                self.send_response(303)
                self.send_header('Location', memory[name])
                self.end_headers()
            else:

                self.send_response(404)
                self.send_header('Content-type', 'text/HTML; charset=utf-8')
                self.end_headers()
                self.wfile.write('{} I dont know this url'.format(name).encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/HTML; charset=utf-8')
            self.end_headers()
            known='\n'.join('{}:{}'.format( keys , memory[keys]) for keys in sorted(memory.keys()))
            self.wfile.write(form.format(known).encode())
    def do_POST(self):
        length = int(self.headers.get('Content-length', 0))
        data=self.rfile.read(length).decode()
        url_data=parse_qs(data)
        longuri=url_data['longuri'][0]
        shortname=url_data['shortname'][0]

        if CheckURI(longuri):
            memory[shortname]=longuri
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/HTML; charset=utf-8')
            self.end_headers()
            self.wfile.write('I couldnt fetch URI {} '.format(longuri).encode())




if __name__ == '__main__':
    server_address = ('', 8009)
    httpd = http.server.HTTPServer(server_address, Shortner)
    httpd.serve_forever()


