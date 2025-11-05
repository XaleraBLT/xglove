from pathlib import Path
import paramiko
import os

__all__ = ["update_calib"]


def update_calib(calib_path: str):
    remote_path = Path(__file__).parent / "data" / "calib_raw.json"
    remote_host = "192.168.4.1"
    user = "xglove"
    password = "xalera.space"
    service_name = "maindotpy"

    with open(calib_path, "r", encoding="utf-8") as f:
        calib_data = f.read()

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(remote_host, username=user, password=password)

    try:
        sftp = ssh.open_sftp()
        with sftp.file(str(remote_path), "w") as remote_file:
            remote_file.write(calib_data)
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
