# remote_executor.py

import paramiko
import time
import os
import config
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RemoteExecutor:
    def __init__(self):
        self.client = None
        self.sftp = None

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加主机密钥

            if config.REMOTE_SERVER_PASSWORD:
                self.client.connect(
                    hostname=config.REMOTE_SERVER_HOST,
                    port=config.REMOTE_SERVER_PORT,
                    username=config.REMOTE_SERVER_USER,
                    password=config.REMOTE_SERVER_PASSWORD
                )
            else:
                raise ValueError("SSH connection requires either password or key file.")

            self.sftp = self.client.open_sftp()
            logging.info(f"Successfully connected to {config.REMOTE_SERVER_HOST}")

            # 确保远程临时目录存在 (强制转为正斜杠)
            remote_dir_sftp = config.REMOTE_TEMP_DIR.replace('\\', '/')
            self._ensure_remote_dir_exists(remote_dir_sftp)

        except Exception as e:
            logging.error(f"Failed to connect to {config.REMOTE_SERVER_HOST}: {e}")
            raise

    def _ensure_remote_dir_exists(self, remote_dir):
        """确保远程目录存在，如果不存在则创建"""
        try:
            self.sftp.stat(remote_dir)
            logging.info(f"Remote directory '{remote_dir}' already exists.")
        except FileNotFoundError:
            logging.info(f"Remote directory '{remote_dir}' not found. Creating it...")
            try:
                # Windows 下使用 mkdir 命令，加上双引号防止路径有空格
                self.client.exec_command(f'mkdir "{remote_dir}"')
                logging.info(f"Successfully created remote directory: {remote_dir}")
            except Exception as e:
                logging.error(f"Failed to create remote directory '{remote_dir}': {e}")
                raise

    def upload_file(self, local_path, remote_path):
        if not self.sftp:
            logging.error("SFTP client not initialized. Cannot upload file.")
            return False
        try:
            # 【关键修复】：强制将远程路径里所有的反斜杠替换为 SFTP 认识的正斜杠 '/'
            remote_path_sftp = remote_path.replace('\\', '/')

            # 【关键修复】：使用正确的 self.sftp.put，传入正确的参数
            self.sftp.put(local_path, remote_path_sftp)

            logging.info(f"Successfully uploaded '{local_path}' to '{remote_path_sftp}'")
            return True
        except Exception as e:
            logging.error(f"Failed to upload '{local_path}' to '{remote_path}': {e}")
            return False

    def execute_remote_command(self, command):
        if not self.client:
            logging.error("SSH client not connected. Cannot execute command.")
            return None, None, None
        try:
            logging.info(f"Executing remote command: {command}")
            stdin, stdout, stderr = self.client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()  # 获取命令执行后的退出状态

            # 加上 errors='ignore' 防止 Windows 返回的某些中文字符导致 Python 解码崩溃
            output = stdout.read().decode('utf-8', errors='ignore')
            error = stderr.read().decode('utf-8', errors='ignore')

            logging.info(f"Command finished with exit status: {exit_status}")
            if output:
                logging.info(f"Command output:\n{output}")
            if error:
                logging.warning(f"Command error output:\n{error}")
            return exit_status, output, error
        except Exception as e:
            logging.error(f"Failed to execute remote command '{command}': {e}")
            return None, str(e), str(e)

    def download_file(self, remote_path, local_path):
        if not self.sftp:
            logging.error("SFTP client not initialized. Cannot download file.")
            return False
        try:
            # 同样将下载的远程路径转为正斜杠
            remote_path_sftp = remote_path.replace('\\', '/')
            self.sftp.get(remote_path_sftp, local_path)
            logging.info(f"Successfully downloaded '{remote_path_sftp}' to '{local_path}'")
            return True
        except FileNotFoundError:
            logging.error(f"Remote file not found: {remote_path}")
            return False
        except Exception as e:
            logging.error(f"Failed to download '{remote_path}' to '{local_path}': {e}")
            return False

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()
            logging.info("SSH connection closed.")


# --- 示例用法 ---
if __name__ == "__main__":
    executor = RemoteExecutor()
    try:
        executor.connect()

        # 1. 准备本地脚本文件
        local_script_path = os.path.join(config.LOCAL_TEMP_DIR, "temp_hysys_script.hx")
        remote_script_path = os.path.join(config.REMOTE_TEMP_DIR, "generated_script.hx")
        os.makedirs(config.LOCAL_TEMP_DIR, exist_ok=True)
        with open(local_script_path, "w") as f:
            f.write("! Dummy HYSYS Script\nSOLVE")

        # 2. 上传脚本到远程服务器
            # 2. 上传脚本到远程服务器
            if executor.upload_file(local_script_path, remote_script_path):
                # 先在外面把路径里的反斜杠替换好，存成一个新变量
                final_script_path = remote_script_path.replace("\\", "/")

                # 再把新变量放进 f-string 里，就不会报错了
                hysys_command = f'"{config.REMOTE_HYSYS_EXECUTABLE}" /runscript:"{final_script_path}"'
            logging.info("Attempting to execute HYSYS script. This might take a while...")
            exit_status, output, error = executor.execute_remote_command(hysys_command)

            if exit_status == 0:
                logging.info("HYSYS simulation executed successfully.")
            else:
                logging.error(f"HYSYS simulation failed with status {exit_status}. Error output:\n{error}")

    finally:
        executor.disconnect()