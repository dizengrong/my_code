import paramiko

class SSH:
    def __init__(self):
        self.connections = {}
        paramiko.util.log_to_file('ssh_log.log')

    def connect(self, ip, username, password = None, keyfile = None):
        if ip in self.connections:
            return True
        else:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password)
            self.connections[ip] = ssh
            return True
    def exec_command(self, ip, cmd):
        ssh =  self.connections[ip]
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd)
        return ssh_stdout.read()
        