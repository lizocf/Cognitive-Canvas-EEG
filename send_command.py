import socket
import sys

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to Pi
server_ip = '10.10.10.10' 
client_socket.connect((server_ip, 12347))

try:
    while True:
        user_input = input("Enter an integer to send: ")
        if user_input.lower() == "exit":
            break

        try:
            number = int(user_input)
            message = number.to_bytes(4, byteorder='big')
            client_socket.send(message)
            print(f"Sent: {number}")
        except ValueError:
            print("Invalid input. Please enter an integer.")

except KeyboardInterrupt:
    print("\nShutdown signal received. Closing connection.")
finally:
    client_socket.close()
    sys.exit(0)
