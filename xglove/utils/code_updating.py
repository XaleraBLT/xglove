import os
import subprocess

__all__ = ["update_code"]


def update_code(code_path: os.path):
    remote_path = "/home/xglove/main-script/main.py"
    remote_host = "192.168.4.1"
    user = "xglove"
    password = "xalera.space"
    service_name = "maindotpy"
    with open(code_path, "r", encoding="utf-8") as f:
        code = f.read()
    code = code.replace('"', '\\"').replace('$', '\\$')

    remote_cmd = f'echo "{code}" | sudo -S tee {remote_path} > /dev/null'

    res = subprocess.run([
        "sshpass", "-p", password,
        "ssh", f"{user}@{remote_host}", remote_cmd
    ], text=True)

    if res.returncode != 0:
        raise Exception("Ошибка при отправке файла:", res.stderr)

    res = subprocess.run([
        "sshpass", "-p", password,
        "ssh", f"{user}@{remote_host}",
        f"echo {password} | sudo -S systemctl restart {service_name}"
    ])

    if res.returncode != 0:
        raise Exception("Ошибка при перезагрузки systemd-задачи:", res.stderr)
