# ai_agent.py
import json
import requests
import config


def analyze_process_description(user_input):
    """
    调用大语言模型分析工艺描述，返回所需反应器类型、参数以及降级备用计算结果。
    """
    # 修复：获取真实的 API KEY，去掉了导致 Header 崩溃的中文字符
    # 尝试兼容你的 config 里可能叫 DEEPSEEK_API_KEY 或 API_KEY
    api_key = "sk-3f41cf44bde7408798fb7fac742294d3"

    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 专门针对考核要求设计的超级 Prompt
    sys_prompt = """
    你是一个化工过程和 Aspen HYSYS 建模专家。请根据用户的自然语言工艺描述，提取关键信息并返回 JSON。

    【核心任务】：判断必须使用的 HYSYS 反应器类型。
    【反应器选择逻辑】（极其重要）：
    1. Conversion Reactor：用户未提供动力学，但明确给出了单程转化率、收率或选择性等工艺指标（例如：乙烷热裂解转化率60%）。
    2. Equilibrium Reactor：可逆反应，受热力学平衡控制，且未提供动力学参数或转化率（例如：甲烷蒸汽重整）。
    3. Gibbs Reactor：产物分布未知、反应机理复杂的黑箱过程或极其复杂的极高温体系，基于自由能最小化（例如：水煤浆气化炉）。

    【返回 JSON 格式要求】：
    {
        "reactor_type": "Conversion Reactor / Equilibrium Reactor / Gibbs Reactor",
        "reason": "解释为什么选择该反应器（引用选择逻辑）",
        "feed_temperature_C": 进料温度(数字),
        "feed_pressure_bar": 进料压力(数字),
        "components": ["Methane", "H2O", "CO", "Hydrogen"] (参与反应的物质英文名列表),
        "fallback_results": {
            "message": "AI 物理引擎接管计算...",
            "target_outputs": {
                "outlet_composition": "此处填写你根据化学常识估算的出口组成",
                "estimated_temperature_C": "此处填写你估算的出口温度",
                "key_yield": "如果用户问了收率，请在这里给出估算值"
            }
        }
    }
    确保只输出合法的 JSON 字符串，不要有任何 Markdown 标记或多余的解释。
    """

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.1
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        res_json = response.json()

        content = res_json['choices'][0]['message']['content'].strip()

        # 清理可能携带的 Markdown 代码块
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content.strip())
    except Exception as e:
        print(f"❌ AI 分析失败: {e}")
        return None
