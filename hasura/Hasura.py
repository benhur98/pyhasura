from __future__ import absolute_import, division, print_function, unicode_literals
import requests
import json
import threading
class Hasura:
    '''
    Base class for Hasura APIs
    hasura = Hasura(domain[, token[, scheme]])
    '''
    def __init__(self, domain, scheme='https'):
        self.domain = domain
        self.token = None
        self.scheme = scheme
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.data = _Data(self)
        self.auth = _Auth(self)
    def receiver(self,table):
        
        initial_count=int(self.data.count(table)["count"])
        while True:
            present_count=int(self.data.count(table)["count"])
            if(present_count is not initial_count):
                received=self.data.select(table=table,offset=(present_count-1))
                print("RT data sync is - ",received)
                
        
    def RtdbSyncReceiver(self,table=''):
        
        thread_recv=threading.Thread(target=receiver,args=(table,))
        thread_recv.daemon=True
        thread_recv.start()
        

class _Auth:
    '''
    Base class for Hasura Auth APIs
    '''
    def __init__(self, hasura):
        self.auth_url = hasura.scheme + '://auth.' + hasura.domain
        self.signup_url = hasura.scheme + '://auth.' + hasura.domain+'.hasura-app.io/v1/signup'
        self.logout_url = hasura.scheme + '://auth.' + hasura.domain+'.hasura-app.io/v1/user/logout'
        self.login_url = hasura.scheme + '://auth.' + hasura.domain+'.hasura-app.io/v1/login'
    def signup(self,hasura):
        print("--------HASURA SIGNUP SERVICE-------------\nPassword must be 8 characters or more")
        self.username=input("Enter Username :")
        self.password=input("Enter Password :")
        res = requests.post(
                self.signup_url,
                data=json.dumps({
                    'provider': "username",
                    'data': {
                        'username':self.username,
                        'password':self.password
                        }
                }),
                headers = self.headers
            )
        if(res["message"] is not None):
            print(res["message"])
            return 'retry'
        if(res["auth_token"] is not None):
            hasura.token=res["auth_token"]
            hasura.headers['Authorization'] = 'Bearer ' + hasura.token
            return 'OK'                  
    
    def login(self):
        ''' Login method '''
        print("--------HASURA LOGIN SERVICE-------------")
        self.uname_login=input("Enter Username :")
        self.psw_login=input("Enter Password :")
        res = requests.post(
                self.login_url,
                data=json.dumps({
                    'provider': "username",
                    'data': {
                        'username':self.uname_login,
                        'password':self.psw_login
                        }
                }),
                headers = self.headers
            )
        if(res["auth_token"] is not None):
            hasura.token=res["auth_token"]
            hasura.headers['Authorization'] = 'Bearer ' + hasura.token
            return 'OK'
            
        if(res["code"] is "invalid-creds"):
            return 'retry'
            
        
        

    def logout(self):
        ''' Logout method '''
        print("--------HASURA LOGOUT ROUTINE-------------")
        res=requests.post(self.logout_url,None,headers=hasura.headers)  
                
        pass

class _Data:
    '''
    Base class for Hasura Data APIs
    '''
    def __init__(self, hasura):
        self.data_url = hasura.scheme + '://data.' + hasura.domain 
        self.query_url = self.data_url + '/v1/query'
        self.headers = hasura.headers
        
    def query(self, req_type, req_args):
        ''' Generic query data method '''
        res = requests.post(
                self.query_url,
                data=json.dumps({
                    'type': req_type,
                    'args': req_args
                }),
                headers = self.headers
            )
        return res
    def insert_sync(self, table, data):
        ''' Insert data method '''
        args = locals()
        del args['self']
        res = requests.post(
                self.query_url,
                data=json.dumps({
                    'type': 'insert',
                    'args': {
                    "objects":[{
                     'value':data       
                        }]

                        }
                }),
                headers = self.headers
            )
        
        return res.json()
    def insert(self, table, objects, returning=[]):
        ''' Insert data method '''
        args = locals()
        del args['self']
        res = self.query('insert', {key : value for key, value in args.items() if value})
        return res.json()

    def update(self, table, where, _set={}, _inc={}, _mul={}, _default={}, returning=[]):
        ''' Update data method '''
        args = locals()
        del args['self']
        res = self.query('update', {'$' + key[1:] if key[0] == '_' else key : value for key, value in args.items() if value})
        return res.json()

    def delete(self, table, where, returning=[]):
        ''' Delete data method '''
        args = locals()
        del args['self']
        res = self.query('delete', {key : value for key, value in args.items() if value})
        return res.json()

    def select(self, table, columns, where={}, order_by={}, limit=10, offset=0):
        ''' Select data method '''
        args = locals()
        del args['self']
        res = self.query('select', {key : value for key, value in args.items() if value})
        return res.json()

    def count(self, table, where={}, distinct=[]):
        ''' Count method ''' 
        args = locals()
        del args['self']
        res = self.query('count', {key : value for key, value in args.items() if value})
        return res.json()['count']
