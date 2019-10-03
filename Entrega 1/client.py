import socket
import select
import errno
import sys, os
import pickle
import time
import threading, queue

HEADER_LENGTH = 10



class Client():

    def __init__(self, email):
        self.host = "10.246.88.138"
        self.port = 5000
        self.s = None
        self.email = email


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
    
    def menu(self):
        print('================ MENU ================\n')
        print('COMMANDS\n')
        print('list: list all clients connected\n')
        print('send: send message to user\n')
        print('quit: quit connection \n')
        print('menu: show this menu\n')
        print('history: show message history')

    
    def work_send_message(self):
        # Wait for user to input a message
        message = input(f'{self.email} > ')

        if message == "quit":
                print('We are closing your chat')
                self.s.close()
                os._exit(0)

        if message == "menu":
            self.menu()
        

        # If message is not empty - send it
        if message:
            
            if message == "send":
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')

                email_client_send = input('Type email destination: ')
                msg = input('Type your message: ')

                email_client_send = email_client_send.encode('utf-8')
                email_header = f"{len(email_client_send):<{HEADER_LENGTH}}".encode('utf-8')

                
                msg = msg.encode('utf-8')
                msg_header = f"{len(msg):<{HEADER_LENGTH}}".encode('utf-8')

                self.s.send(message_header + message + email_header + email_client_send + msg_header + msg)

            # Encode message to bytes, prepare header and convert to bytes, like for email above, then send
            else:
                message = message.encode('utf-8')
                message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
                self.s.send(message_header + message)

        #out_queue.put(message)
        

    def work_receive_message(self):
        try:
            # Now we want to loop over received messages (there might be more than one) and print them
            while True:

                # Receive our "header" containing email length, it's size is defined and constant
                header_cmd = self.s.recv(HEADER_LENGTH)
                # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
                if not len(header_cmd):
                    print('Connection closed by the server')
                    os._exit(0)

                # Convert header to int value
                cmd_len = int(header_cmd.decode('utf-8').strip())

                # Receive and decode email
                cmd = self.s.recv(cmd_len).decode('utf-8')
                
                if cmd == 'list':
                # Now do the same for message (as we received email, we received whole message, there's no need to check if it has any length)
                    message_header = self.s.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    
                    message = pickle.loads(self.s.recv(message_length))

                    print('------------ CLIENTS ------------')
                    for email in message['clients']:
                        print(email.decode('utf-8'))
                
                elif cmd == 'send':
                    message_header = self.s.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = self.s.recv(message_length)

                    msg = message.decode('utf-8')
                    print(msg + '\n')
                
                elif cmd == 'response':
                    server_header = self.s.recv(HEADER_LENGTH)
                    server_length = int(server_header.decode('utf-8').strip())
                    server_message = self.s.recv(server_length)

                    msg_server = server_message.decode('utf-8')

                    message_header = self.s.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = self.s.recv(message_length)

                    msg = message.decode('utf-8')

                    print(msg_server)
                    print('New message: ' + msg + '\n')
                
                elif cmd == 'history':
                    print(cmd)
                    message_header = self.s.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    
                    as_sender = pickle.loads(self.s.recv(message_length))
                   
                    message_header = self.s.recv(HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    
                    as_receiver = pickle.loads(self.s.recv(message_length))
                    
                    if len(as_sender['clients']) > 0:
                        print(' ---- MESSAGE THAT YOU SENT ----\n')
                        for m in as_sender['clients']:
                            if m[3] == 'OK':
                                status = 'Sent'
                            else:
                                status = 'Not sent yet'
                            print(f'Destination: {m[1]}\nMesssage: {m[2]}\nStatus: {status}\n')
                    else:
                        print('You have not sent any messages yet')

                    if len(as_receiver['clients']) > 0:
                        print(' ---- MESSAGE THAT YOU RECEIVED ----\n')
                        for m in as_receiver['clients']:
                            if m[3] == 'OK':
                                status = 'Sent'
                            else:
                                status = 'Not sent yet'
                            print(f'Sender: {m[0]}\nMessage: {m[2]}\nStatus: {status}\n')
                    else:
                        print('You have not received any messages yet')
                else:
                    print(cmd)
        except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                    print(str(e))
                    os._exit(0)
                                

        except Exception as e:
            # Any other exception - something happened, exit
            print(str(e))
            os._exit(0)


    
    def start_client(self):
        while True:
            #try:
            t1 = threading.Thread(target=self.work_receive_message)
            t1.daemon = True
            t1.start()

            t2 = threading.Thread(target=self.work_send_message)
            t2.daemon = True
            t2.start()
        self.s.close()
    

def main():
    email = input('Email: ')

    while True:
        try:
            client = Client(email)
            client.create_socket()
            client.connect_socket()
        except Exception as e:
            print("Error on socket connections: ".format(e))
        else:
            break
    try:
        client.menu()
        client.start_client()
    except Exception as e:
        print('Error: ' + str(e))
    client.s.close()


if __name__ == '__main__':
    while True:
        main()