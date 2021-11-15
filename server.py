import socket
import select

HEADER_LENGTH = 64

IP = "192.168.56.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#bind the scoket
server_socket.bind((IP, PORT))

#start listening
server_socket.listen(2)

#list for sockets
sockets_list = [server_socket]

#to keet track of various clients
clients = {}

print(f'Listening for connections on {IP} : {PORT}...')

def receive_message(client_socket):

    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):
            return False

        #get the message length
        message_length = int(message_header.decode('utf-8').strip())

        #receive data
        data = client_socket.recv(message_length)
        if data == '.':
            return False

        return {'header': message_header, 'data': data}

    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)

    #iterate through all sockets
    for notified_socket in read_sockets:

        #adding new connection
        if notified_socket == server_socket:

            client_socket, client_address = server_socket.accept()

            #Receiving the username
            user = receive_message(client_socket)

            if user is False:
                continue

            sockets_list.append(client_socket)

            #storing the details of the new added user in client dictionary
            clients[client_socket] = user

            print('Accepted new connection from {} : {}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:
            #receive message from client
            message = receive_message(notified_socket)

            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            #taking details of the current client (user)
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            for client_socket in clients:

                #do not sent the message to the sender as well
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:

        sockets_list.remove(notified_socket)
        del clients[notified_socket]