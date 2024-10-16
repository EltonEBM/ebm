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
    
    # Connect to the source host to get the backup file
    ssh.connect(source_host, username='ubuntu', key_filename=key_file)
    sftp = ssh.open_sftp()
    sftp.get('/tmp/mydb_backup.dump', '/tmp/mydb_backup.dump')
    sftp.close()
    ssh.close()

    # Connect to the destination host to transfer the backup file
    ssh.connect(dest_host, username='ubuntu', key_filename=key_file)
    sftp = ssh.open_sftp()
    sftp.put('/tmp/mydb_backup.dump', '/tmp/mydb_backup.dump')
    sftp.close()
    ssh.close()

def restore_db(dest_host, key_file):
    restore_command = 'pg_restore -U postgres -d mydb -c /tmp/mydb_backup.dump'
    ssh_execute_command(dest_host, 'ubuntu', key_file, restore_command)

if __name__ == "__main__":
    source_host = '3.87.138.109'  # Source EC2 IP
    dest_host = '34.229.252.228'  # Destination EC2 IP
    key_file = 'public-pey.pem'  # Path to your private key

    backup_db(source_host, key_file)
    transfer_backup(source_host, dest_host, key_file)
    restore_db(dest_host, key_file)
