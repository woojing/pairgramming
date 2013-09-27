# -*- coding: utf-8 -*-
"""
    Simple sockjs-tornado chat application. By default will listen on port 8080.
"""
import sys
import os
import json
from urllib import urlencode
import tornado.ioloop
import tornado.web
from tornado import gen
from tornado.httpclient import AsyncHTTPClient

import sockjs.tornado

sys.path.append( os.path.join(os.path.dirname(__file__), '..') )
os.environ['DJANGO_SETTINGS_MODULE'] = 'dj_backend.settings'
from importlib import import_module
from django.conf import settings
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

DJ_BACKEND = 'http://localhost:8000'

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render('index.html')


class ChatConnection(sockjs.tornado.SockJSConnection):
    """Chat connection implementation"""
    session_blocks = dict()
    session_code_storage = dict()
    http_client = AsyncHTTPClient()

    def on_open(self, info):
        self.joined_session = []

    @gen.coroutine
    def on_message(self, message):
        recv_data = json.loads(message)

        if recv_data['type']=='session_join':
            session_name = recv_data['data']
            if self.session_blocks.get(session_name, False) == False:
                self.session_blocks[session_name] = set()
            session_id = self.session.conn_info.cookies['sessionid'].value
            dj_session = SessionStore(session_key=session_id)
            dj_user_id = dj_session.get('_auth_user_id')
            if dj_user_id:
                user_response = yield self.http_client.fetch(DJ_BACKEND + '/api/users/%d/?format=json' % dj_user_id)
                dj_user = json.loads(user_response.body)
                self.dj_user = dj_user
                self.user_name = self.dj_user['username']
            else:
                self.user_name = dj_session.get('insta_name')
                self.dj_user = None
            self.session_blocks[session_name].add(self)
            self.joined_session.append(session_name)
            self.session_list_update(session_name)
            send_data = {}
            send_data['type'] = 'code_update'
            send_data['data'] = self.session_code_storage[session_name]
            self.send(json.dumps(send_data))
        elif recv_data['type']=='code_update':
            session_name = recv_data['session']
            send_data = {}
            send_data['type'] = 'code_update'
            send_data['data'] = recv_data['data']
            self.session_code_storage[session_name] = recv_data['data']
            self.broadcast(self.session_blocks[session_name] - set([self]), json.dumps(send_data))
        elif recv_data['type']=='chat_message_send':
            session_name = recv_data['session']
            send_data = {}
            send_data['type'] = 'chat_message_receive'
            chat_data = {'username': self.user_name}
            if self.dj_user:
                chat_data['avatar_url'] = self.dj_user['avatar_url']
            chat_data['message'] = recv_data['data']
            send_data['data'] = json.dumps(chat_data)
            self.broadcast(self.session_blocks[session_name], json.dumps(send_data))
        elif recv_data['type']=='run_code':
            session_name = recv_data['session']
            code = recv_data['data']
            language = recv_data['language']
            post_data = urlencode({'code': code, 'language': language})
            result = yield self.http_client.fetch(DJ_BACKEND + '/pair_session/run_code/',
                method='POST', body=post_data)
            result_data = {'result': result.body}
            send_data = {}
            send_data['type'] = 'run_code_result'
            send_data['data'] = json.dumps(result_data)
            self.broadcast(self.session_blocks[session_name], json.dumps(send_data))

    def on_close(self):
        for session in self.joined_session:
            self.session_blocks[session].remove(self)
            self.session_list_update(session)
        

    def session_list_update(self, session_name):
        session_list = []
        for session in self.session_blocks[session_name]:
            user = {'username': session.user_name}
            if session.dj_user:
                user['avatar_url'] = session.dj_user['avatar_url']
            session_list.append(user)
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
