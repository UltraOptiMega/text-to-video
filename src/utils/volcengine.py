import datetime
from collections import OrderedDict
import json
from urllib.parse import urlencode, quote

from loguru import logger
from flask import current_app

from volcengine.auth.SignerV4 import SignerV4
from volcengine.auth.SignParam import SignParam
from volcengine.Credentials import Credentials

import requests


def get_token(access_key, access_secret, tts_appkey, token_version='volc-auth-v1', region='cn-north-1', service='sami', expiration=24 * 3600):
    payload = {
        'appkey': tts_appkey,
        'token_version': token_version,
        'expiration': expiration,
    }

    sign = SignerV4()

    param = SignParam()
    param.path = '/'
    param.method = 'POST'
    param.host = 'open.volcengineapi.com'
    param.body = json.dumps(payload)
    param.date = datetime.datetime.utcnow()

    query = OrderedDict()
    query['Action'] = 'GetToken'
    query['Version'] = '2021-07-27'

    param.query = query

    header = OrderedDict()
    contentType = 'application/json; charset=utf-8'
    header['Host'] = 'open.volcengineapi.com'
    header['Content-Type'] = contentType
    param.header_list = header

    cren = Credentials(access_key, access_secret, service, region)

    result = sign.sign_only(param, cren)

    url = f'https://{param.host}?Action={query["Action"]}&Version={query["Version"]}'
    headers = {
        'Host': param.host,
        'Content-Type': 'application/json; charset=utf-8',
        'X-Date': result.xdate,
        'X-Content-Sha256': result.xContextSha256,
        'Authorization': result.authorization,
    }

    x = requests.post(url, json=payload, headers=headers)
    logger.info('get token response, status_code: {}, text: {}', x.status_code, x.text)
    resp = x.json()
    return resp['token']
