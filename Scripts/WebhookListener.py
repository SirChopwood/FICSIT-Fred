def start_listener(bot):

    from http.server import BaseHTTPRequestHandler,HTTPServer
    import json
    import sys
    import Config

    global bot_ref
    bot_ref = bot

    # handle POST events from github server
    # We should also make sure to ignore requests from the IRC, which can clutter
    # the output with errors
    CONTENT_TYPE = 'content-type'
    CONTENT_LEN = 'content-length'
    EVENT_TYPE = 'x-github-event'

    class MyHandler(BaseHTTPRequestHandler):
        async def do_GET(self):
            pass

        async def do_CONNECT(self):
            pass

        def do_POST(self):
            if not all(x in self.headers for x in [CONTENT_TYPE, CONTENT_LEN, EVENT_TYPE]):
                return
            content_type = self.headers['content-type']
            content_len = int(self.headers['content-length'])
            event_type = self.headers['x-github-event']

            if content_type != "application/json":
                self.send_error(400, "Bad Request", "Expected a JSON request")
                return

            data = self.rfile.read(content_len)
            if sys.version_info < (3, 6):
                data = data.decode()
            data = json.loads(data)

            self.send_response(200)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes('The fecking machine returned the message ok!?', 'utf-8'))

            with open("queue.txt", "w") as file:
                json.dump(data, file)

            return


    # Run Github webhook handling server
    try:
        server = HTTPServer((Config.SERVER_HOST, Config.SERVER_PORT), MyHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("Exiting")
        server.socket.close()