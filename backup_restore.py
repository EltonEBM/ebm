import paramiko
import os

def ssh_execute_command(host, username, key_file, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, key_filename=key_file)
    stdin, stdout, stderr = ssh.exec_command(command)
    print(stdout.read().decode())
    ssh.close()

def backup_db(3.87.138.109, key_file):
    backup_command = 'pg_dump -U postgres -d mydb -F c -f /tmp/mydb_backup.dump'
    ssh_execute_command(3.87.138.109, 'ubuntu', key_file, backup_command)

def transfer_backup(3.87.138.109, 34.229.252.228, key_file):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(3.87.138.109, username='ubuntu', key_filename=key_file)
    sftp = ssh.open_sftp()
    sftp.get('/tmp/mydb_backup.dump', '/tmp/mydb_backup.dump')
    sftp.close()
    ssh.close()

    ssh.connect(34.229.252.228, username='ubuntu', key_filename=key_file)
    sftp = ssh.open_sftp()
    sftp.put('/tmp/mydb_backup.dump', '/tmp/mydb_backup.dump')
    sftp.close()
    ssh.close()

def restore_db(34.229.252.228, key_file):
    restore_command = 'pg_restore -U postgres -d mydb -c /tmp/mydb_backup.dump'
    ssh_execute_command(34.229.252.228, 'ubuntu', key_file, restore_command)

if __name__ == "__main__":
    source_host = '3.87.138.109'
    dest_host = '34.229.252.228'
    key_file = '/Users/eltonmaharramov/Downloads/public-key.pem'

    backup_db(3.87.138.109, key_file)
    transfer_backup(3.87.138.109, 34.229.252.228, key_file)
    restore_db(34.229.252.228, key_file)
