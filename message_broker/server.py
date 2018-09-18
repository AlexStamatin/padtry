import datetime
import socket
from Client import Client
import json
import requests
import threading
import queue
import xmltodict
import dicttoxml
import sys
from xml.parsers.expat import ExpatError
from io import StringIO


def parse_json(response_text):
    return json.loads(response_text)

def parse_xml(response_text):
    response_dict = dict(xmltodict.parse(response_text)['port'])
    response_dict["message_type"]  = response_dict.pop("message_type")
    response_dict["message_format"]  = response_dict.pop("message_format")
    return response_dict

def dict_to_sendable(recipient, message):
    if recipient.message_format == 'json':
        return json.dumps(message).encode()
    elif recipient.message_format == 'xml':
        return dicttoxml.dicttoxml(message)
    else:
        return

def send_ack(recipient):
    message = dict_to_sendable(recipient, {"name" : "greeting", "text" : "Nice to meet you {}".format(recipient.port) })
    if message:
        recipient.connection.sendall(message)

def manage_message(message_dict):
    if message_dict['name'] == 'handshake':
        l_lock = threading.Lock()
        with l_lock:
            recipient = Client(message_dict['port'], message_dict['message_format'], conn, message_dict['message_type'])
            print(recipient.to_string())
            recipients.append(recipient)
            send_ack(recipient)
    else:
        message_queue.put(message_dict)

# Function for handling connections. This will be used to create threads
def client_thread(conn):
    # infinite loop so that function do not terminate and thread do not end.
    while True:
        # Receiving from client
        received = conn.recv(1024)
        if not received:
            break
        message_dict = process(received)
        manage_message(message_dict)

    # came out of loop
    conn.close()

def send_error_message(client_message):
    pass

def process(client_message):
    return transform(client_message)

def transform(client_message):
    client_message = client_message.decode()
    try:
       return parse_json(client_message)
    except json.decoder.JSONDecodeError:
        return parse_xml(client_message)
    except ExpatError:
        send_error_message(client_message)

def handle_commands(command):
    pass

def find_recipients(message_type):
    addressed_clients = []
    for client in recipients:
        if client.message_type == message_type:
            addressed_clients.append(client)
    return addressed_clients


def send_message(client, message):
    message = dict_to_sendable(client, message)
    if message:
        payload = message.encode()
        client.connection.sendall(payload)

def process_message():
    while True:
        if len(recipients):
            while not message_queue.empty():
                message = message_queue.get()
                if message.name == 'message':
                    l_lock = threading.Lock()
                    with l_lock:
                        addressed_clients = find_recipients(message.message_type)
                        for client in addressed_clients:
                            send_message(client, message)


HOST = ''
PORT = 7070
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print('Socket created')
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
print('Socket bind complete')
s.listen(10)
print('Socket now listening')
recipients = []
message_queue = queue.Queue()
message_thread = threading.Thread(target=process_message)
message_thread.start()
# now keep talking with the client
while 1:
    try:
        # wait to accept a connection - blocking call
        conn, addr = s.accept()
        print('Connected with ' + addr[0] + ':' + str(addr[1]))
        # start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
        t = threading.Thread(target=client_thread, args=(conn,))
        t.start()
    except KeyboardInterrupt:
        s.close()