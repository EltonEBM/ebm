import paramiko
import os

def ssh_execute_command(host, username, key_file, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, key_filename=key_file)
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
    ssh.close()

def backup_db(source_host, key_file):
    backup_command = 'pg_dump -U postgres -d mydb -F c -f /tmp/mydb_backup.dump'
    ssh_execute_command(source_host, 'ubuntu', key_file, backup_command)

def transfer_backup(source_host, dest_host, key_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(source_host, username='ubuntu', key_filename=key_file)
    sftp = ssh.open_sftp()
    sftp.get('/tmp/mydb_backup.dump', '/tmp/mydb_backup.dump')
    sftp.close()
    ssh.close()

    ssh.connect(dest_host, username='ubuntu', key_filename=key_file)
    sftp = ssh.open_sftp()
    sftp.put('/tmp/mydb_backup.dump', '/tmp/mydb_backup.dump')
    sftp.close()
    ssh.close()

def restore_db(dest_host, key_file):
    restore_command = 'pg_restore -U postgres -d mydb -c /tmp/mydb_backup.dump'
    ssh_execute_command(dest_host, 'ubuntu', key_file, restore_command)

if __name__ == "__main__":
    source_host = 'source_ec2_ip'
    dest_host = 'destination_ec2_ip'
    key_file = '/path/to/private-key.pem'

    backup_db(source_host, key_file)
    transfer_backup(source_host, dest_host, key_file)
    restore_db(dest_host, key_file)
