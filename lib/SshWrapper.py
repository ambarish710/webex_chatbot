import os
import paramiko
import logging


class SshWrappper:
    """
        SSH Wrapper Class
    """
    def __init__(self):
        """
            Init Method
        """
        self.logger = logging.getLogger('chatbot_logger')


    def connect(self, hostname, username, password, port=2222, timeout=10):
        """
            Create SSH connection
            :param hostname: Hostname/IP
            :param username: Username
            :param password: Password
            :param port: Port
            :param timeout: SSH timeout value
            :return: SSH connection object
        """
        try:
            self.logger.info("Creating a SSH connection to {} cluster".format(hostname))
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=hostname, username=username, password=password, port=port, timeout=timeout)
            response = self.check_cluster_reachability(hostname)
            self.logger.info("Connected to - {} cluster".format(hostname))
            return ssh, response
        except Exception as e:
            self.logger.error("Cannot connect to {} cluster".format(hostname))
            self.logger.error("Error -- {}".format(e))
            response = self.check_cluster_reachability(hostname)
            return 0, response


    def check_cluster_reachability(self, hostname):
        """
            Check cluster reachability
            :param hostname: Hostname/IP of the cluster
            :return: pingstatus
        """
        self.logger.info("Checking cluster reachability...")
        response = os.system("ping -c 1 " + hostname + " | >/dev/null 2>&1")
        if response == 0:
            pingstatus = "Cluster is reachable"
        else:
            pingstatus = "Cluster is not reachable"
        self.logger.info("Ping Status: {}".format(pingstatus))
        return response
