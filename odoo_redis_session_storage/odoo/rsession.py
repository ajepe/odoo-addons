# Copyright 2019 Babatope Ajepe
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import re
import sys
import werkzeug.contrib.sessions
from urllib import parse
import json
from odoo import http, tools
from odoo.tools.func import lazy_property


def _check_default_session_storage():
    enabled = tools.config.get("session_store", "").strip() == "redis"
    return enabled


try:
    import redis
except ImportError:
    if _check_default_session_storage():
        raise ImportError(
            "Please install package python3-redis: "
            "apt install python3-redis or pip install redis"
        )


def parse_connection_string(con):
    m = re.match("redis://(.*?):(.*?)@(.*?):(.*?)/(.*)", con).groups()
    user, password, server, port, dbindex = m
    return {"port": port, "db": dbindex, "host": server, "password": password}


class SessionRedisStore(werkzeug.contrib.sessions.SessionStore):
    def __init__(self, *args, **kwargs):
        super(SessionRedisStore, self).__init__(*args, **kwargs)
        self.expire = kwargs.get("expire", 36000)
        self.key_prefix = kwargs.get("key_prefix", "")
        con_string = tools.config.get("redis", False)
        params = parse_connection_string(con_string)
        self.redis = redis.Redis(**params)
        self._check_if_redis_server_up()

    def save(self, session):
        key = self._get_session_key(session.sid)

        data = json.dumps(session)
        self.redis.setex(name=key, value=data, time=self.expire)

    def delete(self, session):
        key = self._get_session_key(session.sid)
        self.redis.delete(key)

    def _get_session_key(self, sid):
        key = f"{self.key_prefix}{sid}"
        return key

    def get(self, sid):
        key = self._get_session_key(sid)
        data = self.redis.get(key)
        if data:
            data = json.loads(data)
            return self.session_class(data, sid, False)
        return self.session_class({}, sid, False)

    def _check_if_redis_server_up(self):
        try:
            self.redis.ping()
        except redis.ConnectionError:
            raise redis.ConnectionError(
                "Redis server seem to be down and not responding"
            )


if _check_default_session_storage():

    # Patch methods of openerp.http to use Redis instead of filesystem

    def session_gc(session_store):
        # Override to ignore file unlink
        # because sessions are not stored in files
        pass

    @lazy_property
    def session_store(self):
        # Override to use Redis instead of filestystem
        return SessionRedisStore(session_class=http.OpenERPSession)

    http.session_gc = session_gc
    http.Root.session_store = session_store
