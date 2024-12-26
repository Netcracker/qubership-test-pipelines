import paramiko
import logging

class SSH_Lib(object):

    def __init__(self, username='centos', path_to_key='ssh_key/shift_test_key.pem'):
        self.path_to_key = path_to_key
        self.username = username
        self.pkey = paramiko.RSAKey.from_private_key_file(self.path_to_key)
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        logging.basicConfig(level=logging.INFO)


    def connect_to_host(self, host_ip):
        self.connection.connect(hostname=host_ip, username=self.username, pkey=self.pkey)
        logging.info(f'... Connection to host {host_ip} is created ...')

    def close_connection(self):
        self.connection.close()
        logging.info('... Connection is closed! ...')

    def execute_command_on_host(self, command: str):
        """
        Connection to the host should be created before using this method.
        :param command: command that should be executed on external host
        :return: stdout, stderr of executed command
        """
        stdin, stdout, stderr = self.connection.exec_command(command)
        logging.info(f'Result of command: {command}, {stdout.read()}')
        return stdout, stderr

    def execute_commands_on_host(self, host_ip, commands: list):
        self.connect_to_host(host_ip)
        for command in commands:
            logging.info(f'Start execute command {command}')
            stdin, stdout, stderr = self.connection.exec_command(command)
            logging.info(f'Result of command: {command}, {stdout.read()}')
        self.close_connection()
