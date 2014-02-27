#! /usr/bin/env python
#-*- coding: utf-8 -*-

from rauth import OAuth1Service, OAuth1Session
import requests

################################################################################

oauth_client_key = "lVhUDUfU4LL52nWRBNqO2JpdmQdwRIDZ2iMdVp8s"
oauth_client_secret = "ATIOP1AbYcQRvXbWYD2JWs4EZDG1GBT2Z4eK5E5a"
oauth_request_token = "http://www.openstreetmap.org/oauth/request_token"
oauth_access_token = "http://www.openstreetmap.org/oauth/access_token"
oauth_authorize = "http://www.openstreetmap.org/oauth/authorize"

################################################################################

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

def get(oauth_tokens, url):
    session = OAuth1Session(oauth_client_key,
        oauth_client_secret,
        access_token=oauth_tokens[0],
        access_token_secret=oauth_tokens[1])

    resp = session.get(url)
    if resp and resp.status_code == requests.codes.ok:
        return resp.text
