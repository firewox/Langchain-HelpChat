# @Time  :2024/12/6 2:09
# @Author: yutian.li
# @Email : lyutian2020@qq.com
import subprocess
import frontend.configs.frontend_config as frontend_config
import os
import sys


host = frontend_config.WEBUI_SERVER["host"]
port = frontend_config.WEBUI_SERVER["port"]
current_directory = os.path.join(os.path.dirname(__file__), "")
p = subprocess.run([sys.executable, "-m", "streamlit", "run", os.path.join(current_directory, "mainPage.py"),
                    "--server.address", host,
                    "--server.port", str(port),
                    "--theme.base", "light",
                    "--theme.primaryColor", "#165dff",
                    "--theme.secondaryBackgroundColor", "#f5f5f5",
                    "--theme.textColor", "#000000",
                    ])