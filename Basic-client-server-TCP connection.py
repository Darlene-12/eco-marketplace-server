

# SERVER CODE (step1_server.py)
import socket
import threading

def handle_client(client_socket, address):
    """Handle individual client connection"""
    print(f"Connection established with {address}")
    
    try:
        while True:
            # Receive message from client
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            
            print(f"Received from {address}: {message}")
            
            # For Step 1, we just receive messages
            if message.lower() == 'quit':
                break
                
    except ConnectionResetError:
        print(f"Client {address} disconnected unexpectedly")
    finally:
        client_socket.close()
        print(f"Connection with {address} closed")

def start_server():
    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to localhost and port 12345
    host = 'localhost'
    port = 12345
    server_socket.bind((host, port))
    
    # Listen for connections (backlog of 5)
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")
    
    try:
        while True:
            # Accept client connection
            client_socket, address = server_socket.accept()
            
            # Handle client in a separate thread
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()


# CLIENT CODE (step1_client.py)
import socket

def start_client():
    # Create TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect to server
    host = 'localhost'
    port = 12345
    
    try:
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")
        
        while True:
            # Get message from user
            message = input("Enter message (or 'quit' to exit): ")
            
            # Send message to server
            client_socket.send(message.encode('utf-8'))
            
            if message.lower() == 'quit':
                break
                
    except ConnectionRefusedError:
        print("Could not connect to server. Make sure server is running.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Connection closed")

if __name__ == "__main__":
    start_client()
