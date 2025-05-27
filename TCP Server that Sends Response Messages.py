
# SERVER CODE (step3_server.py)
import socket
import threading
import time
from datetime import datetime

class ResponseServer:
    def __init__(self, host='localhost', port=12345, max_clients=10):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.active_clients = 0
        self.client_lock = threading.Lock()
        self.message_count = 0
        
    def handle_client(self, client_socket, address, client_id):
        """Handle individual client connection with responses"""
        with self.client_lock:
            self.active_clients += 1
            current_clients = self.active_clients
        
        print(f"Client {client_id} ({address}) connected. Active clients: {current_clients}")
        
        # Send welcome message
        welcome_msg = f"Welcome Client {client_id}! You are connected to the server."
        client_socket.send(welcome_msg.encode('utf-8'))
        
        try:
            while True:
                # Receive message from client
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                
                self.message_count += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] Client {client_id}: {message}")
                
                if message.lower() == 'quit':
                    goodbye_msg = f"Goodbye Client {client_id}! Connection closing."
                    client_socket.send(goodbye_msg.encode('utf-8'))
                    break
                
                # Send response back to client
                response = f"Server received: '{message}' (Message #{self.message_count}) at {timestamp}"
                client_socket.send(response.encode('utf-8'))
                    
        except ConnectionResetError:
            print(f"Client {client_id} disconnected unexpectedly")
        except Exception as e:
            print(f"Error handling client {client_id}: {e}")
        finally:
            client_socket.close()
            with self.client_lock:
                self.active_clients -= 1
                remaining_clients = self.active_clients
            print(f"Client {client_id} disconnected. Active clients: {remaining_clients}")

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        server_socket.bind((self.host, self.port))
        server_socket.listen(self.max_clients)
        
        print(f"Response Server listening on {self.host}:{self.port}")
        print(f"Maximum clients supported: {self.max_clients}")
        
        client_counter = 0
        
        try:
            while True:
                client_socket, address = server_socket.accept()
                client_counter += 1
                
                with self.client_lock:
                    if self.active_clients >= self.max_clients:
                        print(f"Maximum clients reached. Rejecting client {address}")
                        reject_msg = "Server full. Please try again later."
                        client_socket.send(reject_msg.encode('utf-8'))
                        client_socket.close()
                        continue
                
                client_thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address, client_counter)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nServer shutting down...")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = ResponseServer()
    server.start_server()


# CLIENT CODE (step3_client.py)
import socket
import threading
import sys

class ResponseClient:
    def __init__(self, client_name="Client"):
        self.client_name = client_name
        self.client_socket = None
        self.connected = False
        
    def receive_messages(self):
        """Thread to receive messages from server"""
        while self.connected:
            try:
                response = self.client_socket.recv(1024).decode('utf-8')
                if response:
                    print(f"\n[SERVER RESPONSE]: {response}")
                    print(f"{self.client_name} - Enter message (or 'quit' to exit): ", end="", flush=True)
            except:
                break
    
    def start_client(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            self.client_socket.connect(('localhost', 12345))
            self.connected = True
            print(f"{self.client_name}: Connected to server")
            
            # Start thread to receive server responses
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            while self.connected:
                message = input(f"{self.client_name} - Enter message (or 'quit' to exit): ")
                
                if not self.connected:
                    break
                    
                self.client_socket.send(message.encode('utf-8'))
                
                if message.lower() == 'quit':
                    self.connected = False
                    break
                    
        except ConnectionRefusedError:
            print(f"{self.client_name}: Could not connect to server")
        except Exception as e:
            print(f"{self.client_name}: Error - {e}")
        finally:
            self.connected = False
            if self.client_socket:
                self.client_socket.close()
            print(f"{self.client_name}: Connection closed")

if __name__ == "__main__":
    client_name = sys.argv[1] if len(sys.argv) > 1 else "Client"
    client = ResponseClient(client_name)
    client.start_client()


# MULTI-CLIENT TESTER (step3_multi_test.py)
import socket
import threading
import time
import random

def test_client_with_responses(client_id, num_messages=5):
    """Test client that expects responses from server"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect(('localhost', 12345))
        print(f"Client {client_id}: Connected")
        
        # Receive welcome message
        welcome = client_socket.recv(1024).decode('utf-8')
        print(f"Client {client_id} received: {welcome}")
        
        # Send messages and receive responses
        for i in range(num_messages):
            message = f"Test message {i+1} from client {client_id}"
            client_socket.send(message.encode('utf-8'))
            
            # Receive response
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Client {client_id} received response: {response}")
            
            time.sleep(random.uniform(0.5, 2))
        
        # Send quit and receive goodbye
        client_socket.send("quit".encode('utf-8'))
        goodbye = client_socket.recv(1024).decode('utf-8')
        print(f"Client {client_id} received: {goodbye}")
        
    except Exception as e:
        print(f"Client {client_id} error: {e}")
    finally:
        client_socket.close()
        print(f"Client {client_id}: Disconnected")

def test_multiple_response_clients(num_clients=5):
    """Test multiple clients with server responses"""
    print(f"Testing {num_clients} clients with server responses...")
    
    threads = []
    for i in range(num_clients):
        thread = threading.Thread(target=test_client_with_responses, args=(i+1,))
        threads.append(thread)
        thread.start()
        time.sleep(0.2)  # Stagger connections
    
    for thread in threads:
        thread.join()
    
    print("All response client tests completed")

if __name__ == "__main__":
    test_multiple_response_clients()
