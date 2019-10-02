import time
import socket
import threading

HEADER_LENGTH = 10

class MultiClientSimulate():

    def __init__(self, number):
        self.host = "192.168.0.143"
        self.email = 'Client-' + str(number)
        self.s = None
        self.port = 5000
    

    def create_socket(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print("Socket creation error" + str(e))    
        
    def connect_socket(self):
        try:
            self.s.connect((self.host, self.port))
            self.s.setblocking(False)
        except socket.error as e:
            print("Socket connection error: " + str(e))
            time.sleep(5)
            raise
        self.send_email()

    def send_email(self):
        try:
            email = self.email.encode('utf-8')
            email_header = f"{len(email):<{HEADER_LENGTH}}".encode('utf-8')
            self.s.send(email_header + email)
            #self.s.send(self.email.encode('utf-8'))
        except socket.error as e:
            print("Could not send hostname to server: " + str(e))
            raise 
def main():

    multiclients = [MultiClientSimulate(i) for i in range(1000)]
    
    for i, client in enumerate(multiclients):
        try:
            client.create_socket()
            client.connect_socket()
            client.send_email()
        except Exception as e:
            print(str(e))
            break
    print(f'It was possible to connect {i} clients at the same time.')
    
    for idx in range(i): 
        multiclients[idx].s.close()

    

if __name__ == "__main__":
    threading.Thread(target=main). start()
        