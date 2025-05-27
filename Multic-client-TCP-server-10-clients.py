
# SERVER CODE (step2_server.py)
import socket
import threading
import time

class MultiClientServer:
    def __init__(self, host='localhost', port=12345, max_clients=10):
        self.host = host
        self.port = port
        self.max_clients = max_clients
        self.active_clients = 0
        self.client_lock = threading.Lock()
        
    def handle_client(self, client_socket, address, client_id):
        """Handle individual client connection"""
        with self.client_lock:
            self.active_clients += 1
            current_clients = self.active_clients
        
        print(f"Client {client_id} ({address}) connected. Active clients: {current_clients}")
        
        try:
            while True:
                # Receive message from client
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                
                print(f"Client {client_id}: {message}")
                
                if message.lower() == 'quit':
                    break
                    
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
        # Create TCP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind to host and port
        server_socket.bind((self.host, self.port))
        
        # Listen with larger backlog to handle multiple simultaneous connections
        server_socket.listen(self.max_clients)
        print(f"Server listening on {self.host}:{self.port}")
        print(f"Maximum clients supported: {self.max_clients}")
        
        client_counter = 0
        
        try:
            while True:
                # Accept client connection
                client_socket, address = server_socket.accept()
                client_counter += 1
                
                # Check if we've reached max clients
                with self.client_lock:
                    if self.active_clients >= self.max_clients:
                        print(f"Maximum clients ({self.max_clients}) reached. Rejecting client {address}")
                        client_socket.send("Server full. Try again later.".encode('utf-8'))
                        client_socket.close()
                        continue
                
                # Handle client in a separate thread
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
    server = MultiClientServer()
    server.start_server()


# MULTI-CLIENT TESTER (step2_multi_client_test.py)
import socket
import threading
import time
import random

def create_client(client_id, delay=0):
    """Create a client that connects to the server"""
    time.sleep(delay)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect(('localhost', 12345))
        print(f"Client {client_id}: Connected successfully")
        
        # Send a few messages
        for i in range(3):
            message = f"Message {i+1} from Client {client_id}"
            client_socket.send(message.encode('utf-8'))
            time.sleep(random.uniform(1, 3))
        
        # Send quit message
        client_socket.send("quit".encode('utf-8'))
        
    except ConnectionRefusedError:
        print(f"Client {client_id}: Could not connect - server refused connection")
    except Exception as e:
        print(f"Client {client_id}: Error - {e}")
    finally:
        client_socket.close()
        print(f"Client {client_id}: Disconnected")

def test_multiple_clients(num_clients=12):
    """Test with multiple clients (more than server limit)"""
    print(f"Testing with {num_clients} clients...")
    
    threads = []
    for i in range(num_clients):
        # Stagger client connections slightly
        delay = i * 0.1
        thread = threading.Thread(target=create_client, args=(i+1, delay))
        threads.append(thread)
        thread.start()
    
    # Wait for all clients to finish
    for thread in threads:
        thread.join()
    
    print("All client tests completed")

if __name__ == "__main__":
    test_multiple_clients()


# INDIVIDUAL CLIENT CODE (step2_client.py)
import socket
import sys

def start_client(client_name="Client"):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect(('localhost', 12345))
        print(f"{client_name}: Connected to server")
        
        while True:
            message = input(f"{client_name} - Enter message (or 'quit' to exit): ")
            client_socket.send(message.encode('utf-8'))
            
            if message.lower() == 'quit':
                break
                
    except ConnectionRefusedError:
        print(f"{client_name}: Could not connect to server")
    except Exception as e:
        print(f"{client_name}: Error - {e}")
    finally:
        client_socket.close()
        print(f"{client_name}: Connection closed")

if __name__ == "__main__":
    client_name = sys.argv[1] if len(sys.argv) > 1 else "Client"
    start_client(client_name)
