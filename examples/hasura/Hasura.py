from __future__ import absolute_import, division, print_function, unicode_literals
import requests
import json
import threading
import time
import tkinter as tk
from tkinter import filedialog
import playy
class Hasura:
    '''
    Base class for Hasura APIs
    hasura = Hasura(domain[, token[, scheme]])
    '''

    def __init__(self, domain, scheme='https'):
        self.domain = domain
        self.token = None
        self.scheme = scheme
        self.root=tk.Tk()
        self.play=None
        self.root.withdraw()
        self.file_path=None
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.data = _Data(self)
        self.auth = _Auth(self)
    def file_upload(self):
        print("--------HASURA FILE UPLOAD SERVICE-------------\n");
        print("select file path ? click enter to continue !")
        input()
        self.file_path = filedialog.askopenfilename()
        url_upload="https://filestore."+self.domain+".hasura-app.io/v1/file"

        res = requests.post(
            url_upload,
            data={'file':open(self.file_path, 'rb')},
            # data=json.dumps((self.file_path.split('/')[-1]), open(self.file_path, 'rb')),
            headers=({'Authorization':self.headers['Authorization']})
        )
        print(res)





    def RtdbSyncReceiver(self, table=''):
        def parser(rec):


            try:
                rec = json.loads(rec)
                if(rec["option"] == "play"):
                    print("true")
                    self.play=playy.Song(rec["url"])
                    self.play.initalize()
                    self.play.play()
                if(rec["option"] == "stop"):
                    self.play.stop()
            except:
                pass
        def receiver(self, table):
            print("Stream service started on table - ",table)

            initial_count = int(self.data.count_new(table))

            while True:

                present_count = int(self.data.count_new(table))

                if (present_count is not initial_count):
                    initial_count = present_count
                    received = self.data.select_new(table=table, offset=(present_count - 1))
                    print("RT data sync is - ", received)
                    parser(received[0]['value'])
        thread_recv = threading.Thread(target=receiver, args=(self,table,))
        # thread_recv.daemon = True
        thread_recv.start()


class _Auth:
    '''
    Base class for Hasura Auth APIs
    '''

    def __init__(self, hasura):
        self.headers=hasura.headers
        self.auth_url = hasura.scheme + '://auth.' + hasura.domain
        self.signup_url = hasura.scheme + '://auth.' + hasura.domain + '.hasura-app.io/v1/signup'
        self.logout_url = hasura.scheme + '://auth.' + hasura.domain + '.hasura-app.io/v1/user/logout'
        self.login_url = hasura.scheme + '://auth.' + hasura.domain + '.hasura-app.io/v1/login'

    def signup(self, hasura):
        print("--------HASURA SIGNUP SERVICE-------------\nPassword must be 8 characters or more")
        self.username = input("Enter Username :")
        self.password = input("Enter Password :")
        res = requests.post(
            self.signup_url,
            data=json.dumps({
                'provider': "username",
                'data': {
                    'username': self.username,
                    'password': self.password
                }
            }),
            headers=self.headers
        )
        try:

            if (res.json()["message"] is not None):
                print(res.json()["message"])
                return 'retry'
        except:
            pass

        if (res.json()["auth_token"] is not None):
            hasura.token = res.json()["auth_token"]
            hasura.headers['Authorization'] = 'Bearer ' + hasura.token
            return 'OK'

    def select(self, table, columns, where={}, order_by={}, limit=10, offset=0):
        ''' Select data method '''
        args = locals()
        del args['self']
        res = self.query('select', {key: value for key, value in args.items() if value})
        return res.json()

    def login(self,hasura):
        ''' Login method '''
        print("--------HASURA LOGIN SERVICE-------------")
        self.uname_login = input("Enter Username :")
        self.psw_login = input("Enter Password :")
        res = requests.post(
            self.login_url,
            data=json.dumps({
                'provider': "username",
                'data': {
                    'username': self.uname_login,
                    'password': self.psw_login
                }
            }),
            headers=self.headers
        )

        try:

            if (res.json()["code"] is "invalid-creds"):
                return 'retry'
        except:
            pass
        if (res.json()["auth_token"] is not None):
            hasura.token = res.json()["auth_token"]
            hasura.headers['Authorization'] = 'Bearer ' + hasura.token
            return 'OK'


    def logout(self):
        ''' Logout method '''
        print("--------HASURA LOGOUT ROUTINE-------------")
        res = requests.post(self.logout_url, None, headers=hasura.headers)

        pass


class _Data:
    '''
    Base class for Hasura Data APIs
    '''

    def __init__(self, hasura):
        self.data_url = hasura.scheme + '://data.' + hasura.domain+'.hasura-app.io'
        self.query_url = self.data_url + '/v1/query'
        self.hasura=hasura

    def query(self, req_type, req_args):
        ''' Generic query data method '''
        res = requests.post(
            self.query_url,
            data=json.dumps({
                'type': req_type,
                'args': req_args
            }),
            headers=self.headers
        )
        return res

    def insert_sync(self, table, data):
        self.headers = self.hasura.headers
        ''' Insert data method '''
        args = locals()
        del args['self']
        res = requests.post(
            self.query_url,
            data=json.dumps({
    "type": "insert",
    "args": {
        "table": table,
        "objects": [
            {
                "value": data
            }
        ]
    }
}),
            headers=self.headers
        )

        return res.json()

    def insert(self, table, objects, returning=[]):
        ''' Insert data method '''
        args = locals()
        del args['self']
        res = self.query('insert', {key: value for key, value in args.items() if value})
        return res.json()

    def update(self, table, where, _set={}, _inc={}, _mul={}, _default={}, returning=[]):
        ''' Update data method '''
        args = locals()
        del args['self']
        res = self.query('update',
                         {'$' + key[1:] if key[0] == '_' else key: value for key, value in args.items() if value})
        return res.json()

    def delete(self, table, where, returning=[]):
        ''' Delete data method '''
        args = locals()
        del args['self']
        res = self.query('delete', {key: value for key, value in args.items() if value})
        return res.json()

    def select_new(self, table, offset=0):
        ''' Select data method '''
        res = requests.post(
            self.query_url,
            data=json.dumps({
    "type": "select",
    "args": {
        "table": table,
        "columns": [
            "*"
        ],
        "offset": offset
    }
}),
            headers=self.hasura.headers
        )
        return res.json()

    def count(self, table, where={}, distinct=[]):
        ''' Count method '''
        args = locals()
        del args['self']
        res = self.query('count', {key: value for key, value in args.items() if value})
        return res.json()['count']

    def count_new(self, table):
        ''' Count method '''

        res = requests.post(
            self.query_url,
            data=json.dumps({
    "type": "count",
    "args": {
        "table": table,
        "where": {}
    }
}),
            headers=self.hasura.headers
        )

        return res.json()['count']
