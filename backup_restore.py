import os
import paramiko
import subprocess

# Variables for SSH and database
first_ec2_ip = os.getenv('FIRST_EC2_IP')
second_ec2_ip = os.getenv('SECOND_EC2_IP')
ssh_key_path = os.getenv('SSH_KEY_PATH')
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')
db_name = os.getenv('DB_NAME')

# Backup PostgreSQL on the first EC2 instance
def backup_database():
    print("Backing up the database...")
    backup_command = f"PGPASSWORD={postgres_password} pg_dump -U {postgres_user} -h localhost {db_name} > backup.sql"
    result = subprocess.run(backup_command, shell=True, capture_output=True)
    if result.returncode != 0:
        print(f"Backup failed: {result.stderr.decode()}")
        exit(1)
    print("Backup completed.")

# Transfer the backup to the second EC2 instance
def transfer_backup():
    print("Transferring backup to the second EC2 instance...")
    scp_command = f"scp -i {ssh_key_path} backup.sql ubuntu@{second_ec2_ip}:/home/ubuntu/"
    result = subprocess.run(scp_command, shell=True, capture_output=True)
    if result.returncode != 0:
        print(f"Transfer failed: {result.stderr.decode()}")
        exit(1)
    print("Backup transferred.")

# Restore the backup on the second EC2 instance
def restore_database():
    print("Restoring the backup on the second EC2 instance...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(second_ec2_ip, username="ubuntu", key_filename=ssh_key_path)
        restore_command = f"PGPASSWORD={postgres_password} psql -U {postgres_user} -d {db_name} -f /home/ubuntu/backup.sql"
        stdin, stdout, stderr = ssh.exec_command(restore_command)
        print(stdout.read().decode())
        print(stderr.read().decode())
        ssh.close()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    backup_database()
    transfer_backup()
    restore_database()
