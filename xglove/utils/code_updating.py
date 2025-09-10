import paramiko
import os

__all__ = ["update_code"]


def update_code(code_path: str):
    remote_path = "/home/xglove/main-script/main.py"
    remote_host = "192.168.4.1"
    user = "xglove"
    password = "xalera.space"
    service_name = "maindotpy"

    with open(code_path, "r", encoding="utf-8") as f:
        code = f.read()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_host, username=user, password=password)

    try:
        sftp = ssh.open_sftp()
        with sftp.file(remote_path, "w") as remote_file:
            remote_file.write(code)
        sftp.close()

        stdin, stdout, stderr = ssh.exec_command(
            f"echo {password} | sudo -S systemctl restart {service_name}"
        )
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            err = stderr.read().decode()
            raise Exception(f"Ошибка при перезагрузке systemd-задачи: {err}")

    finally:
        ssh.close()
