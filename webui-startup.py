# @Time  :2024/12/6 2:09
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import subprocess
import backend.configs.model_config as local_file_config
import os
import sys

host = local_file_config.WEBUI_SERVER["host"]
port = local_file_config.WEBUI_SERVER["port"]
current_directory = os.path.join(os.path.dirname(__file__),"frontend")
print(current_directory)
p = subprocess.run([sys.executable, "-m", "streamlit", "run", os.path.join(current_directory, "mainPage.py"),
                    "--server.address", host,
                    "--server.port", str(port),
                    "--theme.base", "light",
                    "--theme.primaryColor", "#165dff",
                    "--theme.secondaryBackgroundColor", "#f5f5f5",
                    "--theme.textColor", "#000000",
                    ])