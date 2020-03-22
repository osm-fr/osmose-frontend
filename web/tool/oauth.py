#! /usr/bin/env python
#-*- coding: utf-8 -*-

from rauth import OAuth1Service, OAuth1Session
import requests

################################################################################

oauth_client_key = "zGtBQ4zQfaWqy0G3HtRua2d00gvIcSfS4iHHwH2s"
oauth_client_secret = "2KOQG8eUVvcHcTGV5I12XsseRuaeBW0vcmRTTuli"
oauth_server = "https://www.openstreetmap.org/oauth/"

################################################################################

oauth_request_token = oauth_server + "request_token"
oauth_access_token = oauth_server + "access_token"
oauth_authorize = oauth_server + "authorize"


oauth = OAuth1Service(
    consumer_key=oauth_client_key,
    consumer_secret=oauth_client_secret,
    request_token_url=oauth_request_token,
    access_token_url=oauth_access_token,
    authorize_url=oauth_authorize)

def fetch_request_token():
    request_token, request_token_secret = oauth.get_request_token()
    authorize_url = oauth.get_authorize_url(request_token)
    return (authorize_url, (request_token, request_token_secret))

def fetch_access_token(oauth_tokens, request):
    session = oauth.get_auth_session(oauth_tokens[0], oauth_tokens[1], method='POST')
    return (session.access_token, session.access_token_secret)

def _session(oauth_tokens):
    return OAuth1Session(oauth_client_key,
        oauth_client_secret,
        access_token=oauth_tokens[0],
        access_token_secret=oauth_tokens[1])

def get(oauth_tokens, url):
    resp = _session(oauth_tokens,).get(url)
    if resp and resp.status_code == requests.codes.ok:
        return resp.text
    else:
        raise Exception(resp.status_code)

def put(oauth_tokens, url, data=None):
    headers = {'content-type': 'text/xml'}
    resp = _session(oauth_tokens).put(url, data=data, headers=headers)
    print(resp)
    if resp and resp.status_code == requests.codes.ok:
        return resp.text
    else:
        raise Exception(resp.status_code)

def post(oauth_tokens, url, data):
    headers = {'content-type': 'text/xml'}
    resp = _session(oauth_tokens).post(url, data=data, headers=headers)
    print(resp)
    if resp and resp.status_code == requests.codes.ok:
        return resp.text
    else:
        raise Exception(resp.status_code)
