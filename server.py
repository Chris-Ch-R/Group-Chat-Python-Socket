from socket import *
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

# init server
serverSocket = socket(AF_INET , SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET , SO_REUSEADDR , 1)
serverSocket.bind((IP , PORT))

serverSocket.listen()

socket_list = [serverSocket]

clients = {}

def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False

        message_length = int(message_header.decode("utf-8").strip())
        return {
            "header" : message_header,
            "data": client_socket.recv(message_length)
        }
    except:
        return False


print("The server is ready to recieve")

# start program
while True:
    read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)

    for notified_socket in read_sockets:
        if notified_socket == serverSocket:
            client_socket , client_address = serverSocket.accept()

            user = receive_message(client_socket)
            if user is False:
                continue
            socket_list.append(client_socket)

            clients[client_socket] = user

            print(f"Accepted new connection from {client_address[0]}:{client_address[1]} username:{user['data'].decode('utf-8')}")

        else:
            message = receive_message(notified_socket)
            if message is False:
                print(f"Closed connection fron {clients[notified_socket]['data'].decode('utf-8')}")
                socket_list.remove(notified_socket)
                del clients[notified_socket]
                continue
            user = clients[notified_socket]
            print(f"Recieve message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients:
                if clients != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])
    
    for notified_socket in exception_sockets:
        socket_list.remove(notified_socket)
        del clients[notified_socket]