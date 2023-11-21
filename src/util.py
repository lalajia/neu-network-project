import os


def get_resource_dir():
    current_file_path = os.path.abspath(__file__)
    src_directory = os.path.dirname(current_file_path)
    return os.path.join(src_directory, '..', 'resources')


def get_server_dir():
    return os.path.join(get_resource_dir(), 'server')


def get_client_dir():
    return os.path.join(get_resource_dir(), 'client')


def fragment_data(data, udp_payload_size=508):
    fragments = []
    for i in range(0, len(data), udp_payload_size):
        fragments.append(data[i: i + udp_payload_size])
    return fragments
