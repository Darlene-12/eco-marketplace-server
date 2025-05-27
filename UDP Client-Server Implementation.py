
# UDP SERVER CODE (step4_udp_server.py)
import socket
import threading
import time
from datetime import datetime
from collections import defaultdict

class UDPServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.client_sessions = defaultdict(int)  # Track message count per client
        self.total_messages = 0
        self.lock = threading.Lock()
        
    def start_server(self):
        # Create UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((self.host, self.port))
        
        print(f"UDP Server listening on {self.host}:{self.port}")
        print("Ready to receive UDP packets from multiple clients...")
        
        try:
            while True:
                # Receive data and client address
                data, client_address = server_socket.recvfrom(1024)
                message = data.decode('utf-8')
                
                with self.lock:
                    self.client_sessions[client_address] += 1
                    self.total_messages += 1
                    session_count = self.client_sessions[client_address]
                    total_count = self.total_messages
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] From {client_address}: {message}")
                print(f"  Session messages: {session_count}, Total messages: {total_count}")
                
                # Send response back to client
                response = f"UDP Server received: '{message}' (Session #{session_count}, Total #{total_count}) at {timestamp}"
                server_socket.sendto(response.encode('utf-8'), client_address)
                
                # Handle quit message
                if message.lower() == 'quit':
                    goodbye = f"Goodbye {client_address}! Session ended."
                    server_socket.sendto(goodbye.encode('utf-8'), client_address)
                    with self.lock:
                        if client_address in self.client_sessions:
                            del self.client_sessions[client_address]
                    print(f"Client {client_address} session ended")
                
        except KeyboardInterrupt:
            print("\nUDP Server shutting down...")
        finally:
            server_socket.close()

if __name__ == "__main__":
    server = UDPServer()
    server.start_server()


# UDP CLIENT CODE (step4_udp_client.py)
import socket
import sys
import time

class UDPClient:
    def __init__(self, client_name="UDPClient"):
        self.client_name = client_name
        self.server_host = 'localhost'
        self.server_port = 12345
        
    def start_client(self):
        # Create UDP socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(5)  # 5 second timeout for receiving
        
        print(f"{self.client_name}: Starting UDP client")
        print(f"Connecting to UDP server at {self.server_host}:{self.server_port}")
        
        try:
            while True:
                message = input(f"{self.client_name} - Enter message (or 'quit' to exit): ")
                
                # Send message to server
                client_socket.sendto(message.encode('utf-8'), (self.server_host, self.server_port))
                
                try:
                    # Receive response from server
                    response, server_address = client_socket.recvfrom(1024)
                    print(f"[SERVER RESPONSE]: {response.decode('utf-8')}")
                except socket.timeout:
                    print("No response received from server (timeout)")
                
                if message.lower() == 'quit':
                    try:
                        # Try to receive goodbye message
                        goodbye, _ = client_socket.recvfrom(1024)
                        print(f"[SERVER]: {goodbye.decode('utf-8')}")
                    except socket.timeout:
                        pass
                    break
                    
        except Exception as e:
            print(f"{self.client_name}: Error - {e}")
        finally:
            client_socket.close()
            print(f"{self.client_name}: UDP connection closed")

if __name__ == "__main__":
    client_name = sys.argv[1] if len(sys.argv) > 1 else "UDPClient"
    client = UDPClient(client_name)
    client.start_client()


# UDP MULTI-CLIENT TESTER (step4_udp_multi_test.py)
import socket
import threading
import time
import random

def udp_test_client(client_id, num_messages=5, delay_range=(0.1, 1.0)):
    """Test UDP client that sends multiple messages"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(3)
    
    server_address = ('localhost', 12345)
    
    try:
        print(f"UDP Client {client_id}: Starting test")
        
        # Send multiple messages
        for i in range(num_messages):
            message = f"UDP message {i+1} from client {client_id}"
            client_socket.sendto(message.encode('utf-8'), server_address)
            
            try:
                # Receive response
                response, _ = client_socket.recvfrom(1024)
                print(f"UDP Client {client_id}: Received - {response.decode('utf-8')}")
            except socket.timeout:
                print(f"UDP Client {client_id}: No response for message {i+1}")
            
            # Random delay between messages
            time.sleep(random.uniform(*delay_range))
        
        # Send quit message
        client_socket.sendto("quit".encode('utf-8'), server_address)
        
        try:
            goodbye, _ = client_socket.recvfrom(1024)
            print(f"UDP Client {client_id}: {goodbye.decode('utf-8')}")
        except socket.timeout:
            print(f"UDP Client {client_id}: No goodbye message received")
            
    except Exception as e:
        print(f"UDP Client {client_id}: Error - {e}")
    finally:
        client_socket.close()
        print(f"UDP Client {client_id}: Test completed")

def simultaneous_udp_test(num_clients=10):
    """Test multiple UDP clients connecting simultaneously"""
    print(f"Testing {num_clients} simultaneous UDP clients...")
    
    threads = []
    
    # Create all clients at nearly the same time
    for i in range(num_clients):
        thread = threading.Thread(target=udp_test_client, args=(i+1, 3))
        threads.append(thread)
    
    # Start all threads simultaneously
    start_time = time.time()
    for thread in threads:
        thread.start()
    
    # Wait for all to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    print(f"All UDP clients completed in {end_time - start_time:.2f} seconds")

def staggered_udp_test(num_clients=10):
    """Test UDP clients with staggered start times"""
    print(f"Testing {num_clients} staggered UDP clients...")
    
    threads = []
    
    for i in range(num_clients):
        thread = threading.Thread(target=udp_test_client, args=(i+1, 3))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # 100ms delay between starts
    
    for thread in threads:
        thread.join()
    
    print("Staggered UDP client test completed")

if __name__ == "__main__":
    print("Choose test type:")
    print("1. Simultaneous UDP clients")
    print("2. Staggered UDP clients")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        simultaneous_udp_test()
    elif choice == "2":
        staggered_udp_test()
    else:
        print("Invalid choice. Running simultaneous test by default.")
        simultaneous_udp_test()


# UDP vs TCP COMPARISON TEST (step4_comparison_test.py)
import socket
import threading
import time

def tcp_client_test(client_id, messages=3):
    """TCP client for comparison"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('localhost', 12346))  # Different port for TCP
        
        start_time = time.time()
        for i in range(messages):
            message = f"TCP message {i+1} from client {client_id}"
            sock.send(message.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8')
            
        sock.send("quit".encode('utf-8'))
        end_time = time.time()
        
        print(f"TCP Client {client_id}: Completed in {end_time - start_time:.3f}s")
        sock.close()
        
    except Exception as e:
        print(f"TCP Client {client_id}: Error - {e}")

def udp_client_test(client_id, messages=3):
    """UDP client for comparison"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)
        
        start_time = time.time()
        for i in range(messages):
            message = f"UDP message {i+1} from client {client_id}"
            sock.sendto(message.encode('utf-8'), ('localhost', 12345))
            try:
                response, _ = sock.recvfrom(1024)
            except socket.timeout:
                pass
                
        sock.sendto("quit".encode('utf-8'), ('localhost', 12345))
        end_time = time.time()
        
        print(f"UDP Client {client_id}: Completed in {end_time - start_time:.3f}s")
        sock.close()
        
    except Exception as e:
        print(f"UDP Client {client_id}: Error - {e}")

def compare_tcp_udp(num_clients=5):
    """Compare TCP vs UDP performance with multiple clients"""
    print("Comparing TCP vs UDP with multiple clients...")
    print("Note: Make sure both TCP and UDP servers are running!")
    
    # Test UDP clients
    print(f"\nTesting {num_clients} UDP clients...")
    udp_threads = []
    udp_start = time.time()
    
    for i in range(num_clients):
        thread = threading.Thread(target=udp_client_test, args=(i+1,))
        udp_threads.append(thread)
        thread.start()
    
    for thread in udp_threads:
        thread.join()
    
    udp_total = time.time() - udp_start
    print(f"UDP total time: {udp_total:.3f}s")
    
    time.sleep(1)  # Brief pause
    
    # Test TCP clients
    print(f"\nTesting {num_clients} TCP clients...")
    tcp_threads = []
    tcp_start = time.time()
    
    for i in range(num_clients):
        thread = threading.Thread(target=tcp_client_test, args=(i+1,))
        tcp_threads.append(thread)
        thread.start()
    
    for thread in tcp_threads:
        thread.join()
    
    tcp_total = time.time() - tcp_start
    print(f"TCP total time: {tcp_total:.3f}s")
    
    print(f"\nComparison Results:")
    print(f"UDP: {udp_total:.3f}s")
    print(f"TCP: {tcp_total:.3f}s")
    print(f"Difference: {abs(tcp_total - udp_total):.3f}s")

if __name__ == "__main__":
    compare_tcp_udp()
