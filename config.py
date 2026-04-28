# config.py

# config.py

REMOTE_SERVER_HOST = "100.69.187.7"
REMOTE_SERVER_PORT = 22 # 刚才我们已经把服务起在 22 端口了

# 1. 修改用户名：如果你 RDP 是用 Administrator 进的，这里大概率也是它
REMOTE_SERVER_USER = "Administrator"


# 2. 修改密码：填入你连接远程桌面时使用的密码
REMOTE_SERVER_PASSWORD = "Procagent2026"

# 3. 找到真正的 HYSYS.exe 路径！
# 注意：C:\ProgramData...Start Menu 只是快捷方式。
# 你需要在远程电脑上打开 C:\Program Files\AspenTech\Aspen HYSYS\ 查看是不是在这里。
# 找到后修改成类似这样 (注意路径里的斜杠最好用反斜杠加 r，或者全用正斜杠)：
REMOTE_HYSYS_EXECUTABLE = r"C:\Program Files\AspenTech\Aspen HYSYS V15.0\AspenHysys.exe" # 请一定要在远程电脑上核实这个文件确实存在！

# 4. 修改临时目录为 Windows 格式
# 我们直接在远程电脑的 C 盘建个文件夹做临时目录，避免权限问题
REMOTE_TEMP_DIR = "C:/hysys_temp"
REMOTE_RESULT_FILE = f"{REMOTE_TEMP_DIR}/simulation_result.txt"

LOCAL_TEMP_DIR = r"C:\Users\朱豆豆\pythonProject1111\temp"

# 下面的保持不变...

# HYSYS 反应器选择逻辑参数 (根据实际情况调整)
REACTOR_SELECTION_LOGIC = {
    "kinase_param_available": ["conversion", "rate"], # 动力学参数可用telnet ec2-54-199-228-7.ap-northeast-1.compute.amazonaws.com 22的情况
    "conversion_provided": ["conversion", "yield", "selectivity"], # 提供转化率/收率/选择性的情况
    "gibbs_reactor_conditions": ["unknown_products", "complex_reactions", "high_temp"] # Gibbs Reactor 的触发条件
}

# HYSYS 组分信息 (示例, 需要根据实际情况补充)
COMPONENT_MAPPING = {
    "methane": "CH4",
    "hydrogen": "H2",
    "nitrogen": "N2",
    # ... 更多组分
}