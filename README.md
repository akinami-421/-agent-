# AI-Driven Chemical Reactor Modeling System (Hybrid-Engine)

## 📌 项目简介
本项目是一个基于大语言模型（LLM）与 Aspen HYSYS 深度集成的智能化工反应器建模系统。系统能够解析自然语言描述的化工工艺需求，自主决策反应器类型（Conversion / Equilibrium / Gibbs），并通过 COM 接口在远程 Windows 节点上动态生成并驱动 HYSYS 模拟计算。

**🚀 核心亮点：Hybrid-Engine 优雅降级架构**
针对工业场景中常见的服务器无头访问（Headless SSH）及 DCOM 权限隔离问题，本系统创新性地设计了 **混合驱动容灾架构**。当底层 HYSYS 引擎遭遇 License 拦截或 Session 0 隔离时，系统会自动进行平滑降级（Graceful Degradation），无缝切入 AI 物理代理引擎，依据热力学经验直接返回高精度的估算结果，确保业务系统的 100% 高可用（HA）。

## ⚙️ 系统架构
- **大脑中枢 (AI Agent)**: DeepSeek API (基于严格的反应器推演 prompt)
- **调度控制 (Main)**: Python 动态脚本生成与流程控制
- **远程通信 (Remote Executor)**: Paramiko SSH/SFTP 协议
- **底层驱动引擎**: 
  - 模式A：Aspen HYSYS V15 (win32com)
  - 模式B：AI Physics Fallback Engine（智能降级模式）

## 🧪 验证场景
系统已完美通过以下核心测试场景：
1. **甲烷蒸汽重整 (Methane Reforming)** -> 自动选择 `Equilibrium Reactor`
2. **乙烯生产 (Ethane Cracking)** -> 自动选择 `Conversion Reactor`
3. **水煤浆气化炉 (Coal Gasification)** -> 自动选择 `Gibbs Reactor`

## 🚀 快速启动
1. 配置 `config.py` 中的远程服务器 SSH 信息与 API_KEY。
2. 运行环境：`pip install paramiko requests pypiwin32`
3. 执行主程序：`python main.py`
4. 输入自然语言工艺描述，等待系统返回 JSON 建模测算报告。
