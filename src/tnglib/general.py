# Copyright (c) 2015 SONATA-NFV, 2017 5GTANGO
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
#
# This work has been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the 5GTANGO
# partner consortium (www.5gtango.eu).

import requests
import logging
import json
import time
import os
import tnglib.env as env

from datetime import datetime, timedelta

LOG = logging.getLogger(__name__)


def sp_health_check():
    """Check if SP is reachable.

    :returns: bool.
    """
    url = env.root_api
    try:
        resp = requests.get(url, timeout=env.timeout)
        return True
    except:
        return False

def update_token(username, password, store_token=False):
    """Obtain a new authentication token

    :param username: A string.
    :param password: A string.
    :returns: A string containing the token.

    """

    data = {}
    data['username'] = username
    data['password'] = password

    resp = requests.post(env.session_api,
                         json=data,
                         timeout=env.timeout)
    
    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request returned with " +
                  (str(resp.status_code)))
        LOG.debug(str(resp.text))
        return False, json.loads(resp.text)

    token = json.loads(resp.text)['token']

    if store_token:
        payload = {}

        try:
            with open('/tmp/tngcli.txt', 'r') as file:
                for line in file:
                    payload = json.loads(line)
        except:
            pass

        payload[env.get_sp_path()] = {'token': token}
        #datetime to string. Return with strptime(s, format)
        exp_t = datetime.now().strftime('%Y-%m-%d %H:%M')
        payload[env.get_sp_path()]['exp_t'] = exp_t
        with open('/tmp/tngcli.txt', 'w+') as file:
            file.write(json.dumps(payload))
            file.close()

    return True, token

def get_token():
    """Obtain the token from storage
    
    :returns: A string containing the token.
    """

    try:
        with open('/tmp/tngcli.txt', 'r') as file:
            for line in file:
                payload = json.loads(line)
                return True, payload[env.get_sp_path()]['token']

    except:
        return False, 'no token file found'

def is_token_valid():
    """Check whether the token is still valid.
    
    :returns: A bool.
    """

    try:
        with open('/tmp/tngcli.txt', 'r') as file:
            for line in file:
                payload = json.loads(line)

    except:
        return False, 'no token file found'

    exp_t = payload[env.get_sp_path()]['exp_t']
    exp_t_datetime = datetime.strptime(exp_t, '%Y-%m-%d %H:%M')

    return (datetime.now() - exp_t_datetime) < timedelta(minutes=58)

def register(username, password, name='', email='', role=''):
    """Register a new user.
    
    :returns: A bool.
    """
    data = {}
    data['username'] = username
    data['password'] = password
    data['name'] = name
    data['email'] = email
    data['role'] = role

    resp = requests.post(env.user_api,
                         json=data,
                         timeout=env.timeout)
    
    env.set_return_header(resp.headers)

    if resp.status_code != 200:
        LOG.debug("Request returned with " +
                  (str(resp.status_code)))
        LOG.debug(str(resp.text))
        return False, json.loads(resp.text)

    return True, json.loads(resp.text), resp.status_code

