# -*- coding: utf-8 -*-
import sys
import os
import json
import random
import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPClient

import sockjs.tornado

sys.path.append( os.path.join(os.path.dirname(__file__), '..') )
os.environ['DJANGO_SETTINGS_MODULE'] = 'dj_backend.settings'
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore
# import ipdb; ipdb.set_trace()

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render('index.html')


class ChatConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""
    # Class level variable
    # participants = set()
    session_blocks = dict()
    http_client = AsyncHTTPClient()
    # http_client = HTTPClient()

    def on_open(self, info):
        # Send that someone joined
        # self.broadcast(self.participants, "Someone joined.")
        # Add client to the clients list
        # self.participants.add(self)
        self.joined_session = []

    @gen.coroutine
    def on_message(self, message):
        recv_data = json.loads(message)
        session_id = self.session.conn_info.cookies['sessionid'].value
        dj_session = SessionStore(session_key=session_id)
        dj_user_id = dj_session.get('_auth_user_id')
        user_response = yield self.http_client.fetch('http://localhost:8000/api/users/%d/?format=json' % dj_user_id)
        dj_user = json.loads(user_response.body)

        if recv_data['type']=='session_join':
            session_name = recv_data['data']
            if self.session_blocks.get(session_name, False) == False:
                self.session_blocks[session_name] = set()
            self.user_name = dj_user['username']
            self.session_blocks[session_name].add(self)
            self.joined_session.append(session_name)
            self.session_list_update(session_name)
        elif recv_data['type']=='code_update':
            session_name = recv_data['session']
            send_data = {}
            send_data['type'] = 'code_update'
            send_data['data'] = recv_data['data']
            self.broadcast(self.session_blocks[session_name] - set([self]), json.dumps(send_data))

    def on_close(self):
        for session in self.joined_session:
            self.session_blocks[session].remove(self)
            self.session_list_update(session)
        

    def session_list_update(self, session_name):
        session_list = []
        for session in self.session_blocks[session_name]:
            session_list.append({'user_name':session.user_name})
        send_data = {}
        send_data['type'] = 'session_list_update';
        send_data['data'] = json.dumps(session_list)
        self.broadcast(self.session_blocks[session_name], json.dumps(send_data))

if __name__ == "__main__":
    import logging
    logging.getLogger().setLevel(logging.INFO)

    # 1. Create chat router
    ChatRouter = sockjs.tornado.SockJSRouter(ChatConnection, '/chat')

    # 2. Create Tornado application
    app = tornado.web.Application(
            [(r"/", IndexHandler)] + ChatRouter.urls,
            debug=True
    )

    # 3. Make Tornado app listen on port 8080
    app.listen(8888)

    # 4. Start IOLoop
    tornado.ioloop.IOLoop.instance().start()