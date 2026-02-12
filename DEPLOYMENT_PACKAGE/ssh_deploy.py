#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CareFlow AI - SSH Deployment Script with Password Authentication
"""
import paramiko
import sys
import io

# Fix Windows encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Server credentials
HOST = "79.99.45.136"
PORT = 22
USERNAME = "root"
PASSWORD = "j2nzgPFUido5D"

def run_ssh_command(command):
    """Run a command on the remote server via SSH"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, PORT, USERNAME, PASSWORD, timeout=30)

        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        exit_code = stdout.channel.recv_exit_status()

        ssh.close()

        if exit_code != 0:
            return False, error, exit_code
        return True, output, exit_code
    except Exception as e:
        return False, str(e), -1

# Main deployment function
def deploy():
    print("=" * 50)
    print("CareFlow AI - Deployment")
    print("=" * 50)
    print()

    # Step 1: Test connection
    print("Step 1: Testing SSH connection...")
    success, output, code = run_ssh_command("whoami && pwd")
    if success:
        print(f"✓ Connected successfully as: {output.strip()}")
    else:
        print(f"✗ Connection failed: {output}")
        return

    # Step 2: Check OS
    print("\nStep 2: Checking server OS...")
    success, output, code = run_ssh_command("cat /etc/os-release | grep PRETTY_NAME")
    if success:
        print(f"✓ Server OS: {output.strip().split('=')[1]}")
    else:
        print("Could not detect OS version")

    # Step 3: Check if Docker is installed
    print("\nStep 3: Checking Docker installation...")
    success, output, code = run_ssh_command("docker --version")
    if success:
        print(f"✓ Docker: {output.strip()}")
    else:
        print("✗ Docker not found. Installing Docker...")
        # Install Docker
        install_cmd = """
        apt-get update -qq &&
        apt-get install -y docker.io docker-compose &&
        systemctl enable --now docker &&
        docker --version
        """
        success, output, code = run_ssh_command(install_cmd)
        if success:
            print(f"✓ Docker installed: {output.strip()}")
        else:
            print(f"✗ Docker installation failed: {output}")
            return

    # Step 4: Create deployment directory
    print("\nStep 4: Creating deployment directory...")
    success, output, code = run_ssh_command("mkdir -p /opt/careflow-ai-deploy && echo 'Directory ready'")
    if success:
        print("✓ Deployment directory created")
    else:
        print(f"✗ Failed to create directory: {output}")
        return

    # Step 5: Check for deployment files
    print("\nStep 5: Checking deployment files...")
    success, output, code = run_ssh_command("ls -la /opt/careflow-ai-deploy/")
    if success:
        print("Files in deployment directory:")
        print(output)
    else:
        print("No deployment files found yet")

    print("\n" + "=" * 50)
    print("Pre-deployment checks complete!")
    print("=" * 50)

if __name__ == "__main__":
    deploy()
