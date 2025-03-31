# import socket
# from niryo_robot_python_ros_wrapper.ros_wrapper import *
# import rospy
# import time
# import math
# import struct

# rospy.init_node('niryo_robot_arm_example_python_ros_wrapper')
# n = NiryoRosWrapper()

# # Create a socket object
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# # Bind to a port and start listening
# server_socket.bind(('0.0.0.0', 12347))  # '0.0.0.0' allows connections from any IP
# server_socket.listen(1)  # Listen for 1 connection

# print("Server is listening for incoming connections...")
# client_socket, client_address = server_socket.accept()
# print("Connection from:", client_address)

# try:
#     n.calibrate_auto()
#     print "Calibration finished !"
#     time.sleep(1)
#     n.set_arm_max_velocity(30)

#     while True:
#         # Receive the message (assuming we are receiving a 4-byte integer)
#         message = client_socket.recv(4)  # Expecting 4 bytes for the integer
#         # received_int = int.from_bytes(message, byteorder='big')
#         received_int = struct.unpack(">I", message)[0] 
#        # print(f"Received message: {received_int}")
#         # if not message:
#         #     break  # If no message is received, break the loop

#         if received_int == 0: # REST
#             print("N")
#             # DO NOTHING IG 
#         elif received_int == 1: # LEFT 
#            #  print(f"Received message: {received_int}")
#             current_joints = n.get_joints() 
#             current_joints[0] += -0.5
#             n.move_joints(*current_joints)
#         elif received_int == 2: # RIGHT
#             current_joints = n.get_joints() 
#             current_joints[0] += 0.5
#             n.move_joints(*current_joints)
#         elif received_int == 3: # PULL
#             current_joints = n.get_joints() 
#             current_joints[1] += -0.5  
#             current_joints[2] += 0.5
#             n.move_joints(*current_joints)
#         elif received_int == 4:
#             current_joints = n.get_joints() 
#             current_joints[1] += 0.5  
#             current_joints[2] += -0.5
#             n.move_joints(*current_joints)

#         # Convert the received bytes back to an integer

# except KeyboardInterrupt:
#     print("\nServer shutting down.")
# finally:
#     # Close the connection
#     client_socket.close()
#     server_socket.close()

import socket
from niryo_robot_python_ros_wrapper.ros_wrapper import *
import rospy
import time
import math
import struct

rospy.init_node('niryo_robot_arm_example_python_ros_wrapper')
n = NiryoRosWrapper()

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind to a port and start listening
server_socket.bind(('0.0.0.0', 12347))  # '0.0.0.0' allows connections from any IP
server_socket.listen(1)  # Listen for 1 connection

print("Server is listening for incoming connections...")
client_socket, client_address = server_socket.accept()
print("Connection from:", client_address)

try:
    n.calibrate_auto()
    print("Calibration finished !")
    time.sleep(1)
    n.set_arm_max_velocity(30)

    while True:
        # Receive the message (assuming we are receiving a 4-byte integer)
        message = client_socket.recv(4)  # Expecting 4 bytes for the integer
        received_int = struct.unpack(">I", message)[0]  # Convert the received bytes back to an integer

        if received_int == 0:  # REST
            print("N")
            # DO NOTHING IG 
        elif received_int == 1:  # LEFT
            current_joints = n.get_joints() 
            current_joints[0] += -0.5
            try:
                n.move_joints(*current_joints)
            except NiryoRosWrapperException as e:
                print("Error moving joints to the left")
        elif received_int == 2:  # RIGHT
            current_joints = n.get_joints() 
            current_joints[0] += 0.5
            try:
                n.move_joints(*current_joints)
            except NiryoRosWrapperException as e:
                print("Error moving joints to the right")
        elif received_int == 3:  # PULL
            current_joints = n.get_joints() 
            current_joints[1] += -0.5  
            current_joints[2] += 0.5
            try:
                n.move_joints(*current_joints)
            except NiryoRosWrapperException as e:
                print("Error moving joints to pull")
        elif received_int == 4:  # PUSH
            current_joints = n.get_joints() 
            current_joints[1] += 0.5  
            current_joints[2] += -0.5
            try:
                n.move_joints(*current_joints)
            except NiryoRosWrapperException as e:
                print("Error moving joints to push")

except KeyboardInterrupt:
    print("\nServer shutting down.")
finally:
    # Close the connection
    client_socket.close()
    server_socket.close()
