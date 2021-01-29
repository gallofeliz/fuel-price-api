#!/usr/bin/env python

import http.server, json, logging, os, socketserver, requests

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')

port = int(os.environ.get('PORT', 8080))

def fioulreduc_read(cp, qqt):
  session = requests.session()

  session.get(
    'https://www.fioulreduc.com/commande/devis',
    params={'q': qqt, 'z': cp, 'e': '', 'ske': '1', 'p': '1'}
  )
  response = session.get('https://www.fioulreduc.com/api/active-funnel').json()

  logging.info(response)

  if not response['activeFunnel']:
    raise Exception('Invalid request (zip ?)')

  price = response['activeFunnel']['products']['1']
  qt = response['activeFunnel']['qt']
  zcp = response['activeFunnel']['zipcode']

  if int(qt) != int(qqt):
    raise Exception('Invalid qqt')

  if zcp != cp:
    raise Exception('Invalid cp')

  return {
    'price': price * qt,
    'price/l': price,
  }

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if (self.path == '/favicon.ico'):
            return

        parts = self.path.split('?')[0][1:].split('/')

        if len(parts) != 2:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(bytes(str('Invalid request'), 'utf8'))
            return

        try:
            data = fioulreduc_read(parts[0], parts[1])

            self.send_response(200)
            self.send_header('Content-type','application/json')
            self.end_headers()
            self.wfile.write(bytes(json.dumps(data), 'utf8'))
        except Exception as inst:
             self.send_response(500)
             self.send_header('Content-type','text/html')
             self.end_headers()
             self.wfile.write(bytes(str(inst), 'utf8'))
             logging.exception('Error')

httpd = socketserver.TCPServer(('', port), Handler)
try:
   httpd.serve_forever()
except KeyboardInterrupt:
   pass
httpd.server_close()
