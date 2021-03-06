from hasura import Hasura
import playy
def main():
    
    print("DEMO RT database sender..")
    table=input("Enter table name :")
    hasura.RtdbSyncReceiver(table)
    
    
def start():
    mode=input('''
Enter options:
1.SignUp
2.Login
        ''')
    
    if mode is '1':
            resp=hasura.auth.signup(hasura)
            if resp is 'OK':
                print("Success ! ,Login to continue")
                start()
            if resp is 'retry':
                print('invalid password/username ! Retry_')
                start()
    if mode is '2':
            resp=hasura.auth.login(hasura)
            if resp is 'OK':
                print("Success !")
                main()
            if resp is 'retry':
                print('invalid password/username ! Retry !')
                start()
            

if __name__=="__main__":
    domain=input("Enter Your Cluster ID:")
    hasura=Hasura.Hasura(domain)
    start()
    
