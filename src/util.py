import os

# This function returns the absolute path to the "resources" directory. It's used to obtain the path to the directory containing shared resources for the project.
def get_resource_dir():
    current_file_path = os.path.abspath(__file__)
    src_directory = os.path.dirname(current_file_path)
    return os.path.join(src_directory, '..', 'resources')

# Returns the absolute path to the "server" directory within the "resources" directory.
def get_server_dir():
    return os.path.join(get_resource_dir(), 'server')

# Returns the absolute path to the "client" directory within the "resources" directory.
def get_client_dir():
    return os.path.join(get_resource_dir(), 'client')

# Used for breaking down large data into manageable chunks, especially when dealing with UDP packets which have payload size limitations. The default size is set to 1400 bytes.
def fragment_data(data, udp_payload_size=1400):
    fragments = []
    for i in range(0, len(data), udp_payload_size):
        fragments.append(data[i: i + udp_payload_size])
    return fragments

