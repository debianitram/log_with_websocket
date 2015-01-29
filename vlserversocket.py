#!/usr/bin/env python
#-*- encoding:utf-8 -*-

# debianitram (at) gmail.com

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import threading
from tailer import tail, follow


listeners = []


class TailThread(threading.Thread):
    def __init__(self):
        super(TailThread, self).__init__()
        self.name == self.__class__.__name__
        self.end_loop = False
        self.filename = 'log.log'

    def run(self):
        while not self.end_loop:
            if listeners:
                f_follow = follow(open(self.filename))
                for l in f_follow:
                    for c in listeners:
                        print('Client: %s - Text: %s' % (c, l))
                        c.write_message(l)

                    if not listeners:
                        f_follow.close()
                        break


class GetHandler(tornado.web.RequestHandler):
    def get(self):
        if self.request.arguments.get('message'):
            message = self.request.arguments.get('message')[0]
        else:
            message = 'No send message'

        print('Message: ', message)
        for client in listeners:
            client.write_message(message)


class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self, params):
        print('Connected')
        print('Params: %s' % params) # Type of params is unicode
        listeners.append(self)

    def on_message(self, message):
        pass

    def on_close(self):
        print('Close')
        listeners.remove(self)


if __name__ == '__main__':
    urls = [
            (r'/', GetHandler),
            (r'/realtime/(.*)', RealtimeHandler)
    ]

    tail_thread = TailThread()
    tail_thread.start()  # Run thread! 
    
    application = tornado.web.Application(urls, auto_reload=True)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8080, address="0.0.0.0")
    tornado.ioloop.IOLoop.instance().start()
