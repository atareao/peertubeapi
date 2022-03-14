#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2022 Lorenzo Carbonell <a.k.a. atareao>

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
import toml
import time


class PeerTube:
    def __init__(self, path):
        self.path = path
        self.conf = self.__read_configuration()
        self.login()
        #self.logout()

    def get_user_info(self):
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/users/me"
        print(url)
        token_type = self.conf['token']['token_type']
        access_token = self.conf['token']['access_token']
        headers = {
                "Authorization": f"{token_type} {access_token}",
                }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return {}


    def logout(self):
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/users/revoke-token"
        token_type = self.conf['token']['token_type']
        access_token = self.conf['token']['access_token']
        headers = {
                "Authorization": f"{token_type} {access_token}",
                }
        try:
            requests.post(url, headers=headers)
        finally:
            self.conf['token']['expires_in'] = 0
            self.conf['token']['refresh_token_expires_in'] = 0
            self.__save_conf()
            print("===")

    def login(self):
        if self.conf['client']['client_id'] == "" or \
                self.conf['client']['client_secret'] == "":
            self.__login_prerequisite()
        ts = int(time.time())
        if self.conf['token']['token_type'] == '' or \
                self.conf['token']['access_token'] == '' or \
                self.conf['token']['access_token'] == '' or \
                ts > self.conf['token']['refresh_token_expires_in']:
            self.__get_access_token()
        elif ts > self.conf['token']['expires_in']:
            self.__get_refresh_token()

    def __read_configuration(self):
        conf = {}
        try:
            conf = toml.load(self.path)
        except Exception as exception:
            print(exception)
        return conf

    def __login_prerequisite(self):
        base_url = self.conf['credentials']['base_url']
        url = f"{base_url}/oauth-clients/local"
        response = requests.get(url)
        if response.status_code == 200:
            self.conf['client'] = response.json()
            self.__save_conf()
        else:
            raise Exception

    def __get_access_token(self):
        client_id = self.conf['client']['client_id']
        client_secret = self.conf['client']['client_secret']
        base_url = self.conf['credentials']['base_url']
        username = self.conf['credentials']['username']
        password = self.conf['credentials']['password']
        url = f"{base_url}/users/token"
        data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "password",
                "response_type": "code",
                "username": username,
                "password": password
                }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            data = response.json()
            ts = int(time.time())
            data['expires_in'] += ts
            data['refresh_token_expires_in'] += ts
            self.conf['token'] = data
            self.__save_conf()
        else:
            raise Exception

    def __get_refresh_token(self):
        base_url = self.conf['credentials']['base_url']
        client_id = self.conf['client']['client_id']
        client_secret = self.conf['client']['client_secret']
        refresh_token = self.conf['token']['refresh_token']
        url = f"{base_url}/users/token"
        data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
                }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            data = response.json()
            ts = int(time.time())
            data['expires_in'] += ts
            data['refresh_token_expires_in'] += ts
            self.conf['token'] = data
            self.__save_conf()
        else:
            print(response.status_code)
            self.conf['token']['refresh_token_expires_in'] = 0
            self.__save_conf()

    def __save_conf(self):
        with open(self.path, 'w') as fw:
            toml.dump(self.conf, fw)



if __name__ == '__main__':
    import os
    from dotenv import load_dotenv
    load_dotenv()
    path = os.getenv("PT_PATH")
    peerTube = PeerTube(path)
    print(peerTube.get_user_info())
