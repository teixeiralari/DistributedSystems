import socket
import select
import pickle
import sys
import threading
import pandas as pd

HEADER_LENGTH = 10


class Server():

    def __init__(self):
        self.s = None
        self.host = ""
        self.port = 5000
        self.sockets_list = list()
        self.clients_email = list()
        self.clients = dict()

    def create_socket(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sockets_list.append(self.s)

            #Allow reuse addr
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error as msg:
            print("Socket creation error: " + str(msg))
     
     # Binding the socket and listening for connections
    def bind_socket(self):
        try:
            print("Binding the Port: " + str(self.port))
            self.s.bind((self.host, self.port))
            self.s.listen(5)
        except socket.error as msg:
            print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
            #Recursion - call the bind_socket() until binded
            self.bind_socket()
    
    def format_message(self, message, HEADER_LENGTH=10):
        if type(message) != str:
            
            data = pickle.dumps({'clients': message})
            data_header = f"{len(data):<{HEADER_LENGTH}}".encode('utf-8')
            return data_header, data

        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        return message_header, message
    
    def receive_message(self, client_socket):

        try:

            
            message_header = client_socket.recv(HEADER_LENGTH)

          
            if not len(message_header):
                return False

          
            message_length = int(message_header.decode('utf-8').strip())

            # Return an object of message header and message data
            return {'header': message_header, 'data': client_socket.recv(message_length)}

        except:

            return False


    def send_messages_log_file(self):
        log_file = pd.read_csv('log.txt', sep=';')
        aux_file = log_file[log_file.status == 'Pending']

        if aux_file['status'].nunique() > 0:
            for index, row in aux_file.iterrows():
                sender = row['sender']
                destination = row['receiver']
                message = row['message']
                message_header, message_data = self.format_message(message)
                
                try:
                    header_dest, dest = self.format_message(destination)
                    socket_client_destination = self.get_socket(self.clients, {'header': header_dest, 'data': dest})

                    header_cmd, cmd = self.format_message('response')
                    header_server, response_server = self.format_message('You have a message from user: ' + sender)
                    
                    socket_client_destination.send(header_cmd + cmd + header_server + response_server + message_header+ message_data)
                    
                    log_file.at[index, 'status'] = 'OK'

                except:
                    continue
                
        log_file.to_csv('log.txt', sep=';', index=False)      

    def append_log_file(self, sender, receiver, message, status):
        with open('log.txt', 'a') as f:
            f.write(sender + ';' + receiver + ';' + message + ';' + status + '\n')


    def start_server(self):
        while True:
            
            #Start thread to check if there are messages to send in log file
            threading.Thread(target=self.send_messages_log_file).start()
            
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list)

            # Iterate over notified sockets
            for notified_socket in read_sockets:

                # If notified socket is a server socket - new connection, accept it
                if notified_socket == self.s:

                    # Accept new connection
                    client_socket, client_address = self.s.accept()

                    
                    user = self.receive_message(client_socket)

        
                    if user is False:
                        continue

                    # Add accepted socket to select.select() list
                    self.sockets_list.append(client_socket)

                    # Also save username and username header
                    self.clients[client_socket] = user
                    
                    self.clients_email.append(user['data'])

                    print('Accepted new connection from {}:{}, email: {}'.format(*client_address, user['data'].decode('utf-8')))
                
                
                # Else existing socket is sending a message
                else:

                    # Receive message
                    message = self.receive_message(notified_socket)

                    # If False, client disconnected, cleanup
                    if message is False:
                        print('Closed connection from: {}'.format(self.clients[notified_socket]['data'].decode('utf-8')))

                        # Remove from list for socket.socket()
                        self.sockets_list.remove(notified_socket)

                        user = self.clients[notified_socket]
                        
                        # Remove from our list of users
                        del self.clients[notified_socket]
                        
                        #Remove from user email list
                        self.clients_email.remove(user['data'])

                        continue
                    
                    user = self.clients[notified_socket]

                    print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')


                    if message['data'].decode('utf-8') == 'list':
                        header_cmd, cmd = self.format_message('list')
                        message_header, message = self.format_message(self.clients_email)
                        notified_socket.send(header_cmd + cmd + message_header + message)
                    
                    elif message['data'].decode('utf-8') == 'send':
                        status = 'Pending'
                        email_destination = self.receive_message(notified_socket)
                        msg_destination = self.receive_message(notified_socket)

                      
                        
                        if email_destination['data'] in self.clients_email:
                            socket_client_destination = self.get_socket(self.clients, email_destination)
                            
                            try:
                                header_cmd, cmd = self.format_message('response')
                                header_server, response_server = self.format_message('You have a message from user: ' + user['data'].decode('utf-8'))
                                
                                socket_client_destination.send(header_cmd + cmd + header_server + response_server + msg_destination['header'] + msg_destination['data'])
                                
                                header_server, response_server = self.format_message('Your message was sent succesfully to user: ' + email_destination['data'].decode('utf-8'))
                                notified_socket.send(header_server + response_server)

                                status = 'OK'

                            except:
                                header_cmd, cmd = self.format_message('send')
                                header_server, response_server = self.format_message('Could not send your message now, user is disconnected')
                                notified_socket.send(header_cmd + cmd + header_server + response_server)
                                
                        else:
                            
                            header_cmd, cmd = self.format_message('send')
                            header_server, response_server = self.format_message('Email not found or user is disconnected. If user exist, your message will be send later.')
                            notified_socket.send(header_cmd + cmd + header_server + response_server)

                        threading.Thread(target=self.append_log_file, args=(user["data"].decode("utf-8"), 
                                                email_destination["data"].decode("utf-8"),
                                                msg_destination["data"].decode("utf-8"),
                                                status,)).start()
                

            # handle some socket exceptions
            for notified_socket in exception_sockets:

                # Remove from list for socket.socket()
                self.sockets_list.remove(notified_socket)

                # Remove from our list of users
                del self.clients[notified_socket]
        self.s.close()
    
    def get_socket(self, client_socket, val): 

        for socket, email in client_socket.items(): 

            if val == email: 

                return socket 

        return "socket doesn't exist"

def main():
    server = Server()
    server.create_socket()
    server.bind_socket()
    server.start_server()


if __name__ == '__main__':
    threading.Thread(target=main).start()