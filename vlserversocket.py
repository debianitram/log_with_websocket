#!/usr/bin/env python
#-*- encoding:utf-8 -*-
# debianitram (at) gmail.com

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import threading
import time
import json

from tailer import tail, follow
import config


service_clients = {key: {} for key in config.services.keys()}
service_clients.update(init={})


class ListenersThread(threading.Thread):
    def __init__(self):
        super(ListenersThread, self).__init__()
        self.name == self.__class__.__name__
        self.end_loop = False

    def run(self):
        while not self.end_loop:
            time.sleep(1)
            for service in service_clients.keys():

                # Ignore Init
                if service == 'init':
                    continue
                
                if service_clients[service]:
                    f_follow = follow(open(config.services[service]['path_log']))
                    for line in f_follow:
                        for socket in service_clients[service].values():
                            socket.write_message(line)

                        if not service_clients[service]:
                            f_follow.close()



class GetHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(GetHandler, self).__init__(application, request, **kwargs)
        self.add_header('Access-Control-Allow-Origin', '*')
    

    def get(self):

        identify = self.request.arguments.get('identify', [None])[0]
        srvs = self.request.arguments.get('srvs', [None])[0]
        cmds = self.request.arguments.get('cmds', [None])[0]

        if cmds == 'get-list':
            self.set_header('Content-Type', 'application/json; charset=UTF-8')
            self.write(self.get_list_service())
        

        if srvs in service_clients and identify and \
            not(identify in service_clients.get(srvs)):

            # If new connection.
            if identify in service_clients['init']:
                client = {identify: service_clients['init'].pop(identify)}
                service_clients[srvs].update(client)
                # print('=== New Client', client)

            else:
                # Small service_clients
                s = {k: v for k, v in service_clients.items() if not k in (srvs, 'init')}

                for service in s.keys():
                    if identify in s[service]:
                        client = {identify: s[service].pop(identify)}
                        service_clients[srvs].update(client)
                        # print('=== Change Client', client)
                        break

            self.first_read_log(srvs, client[identify])


    def first_read_log(self, service, socket):
        ''' First read of log '''       
        first_read = tail(open(config.services[service]['path_log']),
                          config.first_read_lines)
        socket.write_message('\n'.join(first_read))


    def get_list_service(self):
        list_services = [key for key in config.services.keys()]
        return json.dumps(list_services)



class RealtimeHandler(tornado.websocket.WebSocketHandler):
    def open(self, username):
        self.identify = username
        init_client = {self.identify: self}
        service_clients['init'].update(init_client)
        # print('=== Connect User: %s' % self.identify)  // define logger

    def on_message(self, service):
        ''' receivd message from client '''
        pass

    def check_origin(self, origin):
        ''' Accept connection from 0.0.0.0/0'''
        return True

    def on_close(self):
        for service in service_clients.keys():
            for identify, socket in service_clients[service].items():
                if self == socket:
                    del service_clients[service][identify]
                    # print('=== Closed!')  // define logger
                    break



if __name__ == '__main__':
    urls = [
            (r'/', GetHandler),
            (r'/realtime/(.*)', RealtimeHandler)
    ]

    try:
        listeners_thread = ListenersThread()
        listeners_thread.start()  # Run thread!

        application = tornado.web.Application(urls, auto_reload=True)
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(8797, address="0.0.0.0")
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        raise
