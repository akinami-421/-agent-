# nlp_processor.py

import spacy
from transformers import pipeline
import re

# 加载 spaCy 模型 (中文或英文，根据你的输入语言选择)
# python -m spacy download zh_core_web_sm  (如果中文)
# python -m spacy download en_core_web_sm  (如果英文)
try:
    nlp = spacy.load("en_core_web_sm") # 假设输入是英文，如果中文请换成 zh_core_web_sm
except OSError:
    print("Downloading en_core_web_sm model for spaCy...")
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# 可以选择使用 Hugging Face 的 pipeline 进行更高级的 NER 或关系抽取
# nlp_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english") # 示例NER模型

def parse_user_input(user_description: str) -> dict:
    """
    解析用户输入的自然语言描述，提取关键信息。
    这是核心的 NLP 部分，可能需要根据实际场景进行大量调整和优化。
    """
    doc = nlp(user_description)
    extracted_data = {
        "reactants": [],
        "products": [],
        "temperature": None,
        "pressure": None,
        "conversion": None,
        "yield": None,
        "selectivity": None,
        "kinetic_params_provided": False,
        "equilibrium_info_provided": False,
        "reactor_type_hint": None # 可以根据描述推测反应器类型
    }

    # -----------------------------------------------------------
    # 示例：使用 spaCy 的 NER 和规则匹配提取信息
    # -----------------------------------------------------------
    for ent in doc.ents:
        # 示例：提取反应物和产物 (需要更复杂的逻辑来区分)
        if ent.label_ == "PRODUCT": # 假设有PRODUCT标签，实际需要自定义NER
            extracted_data["products"].append(ent.text)
        elif ent.label_ == "CHEMICAL" or ent.label_ == "ORG": # 假设CHEMICAL/ORG可能代表反应物
            extracted_data["reactants"].append(ent.text)

        # 提取温度和压力 (需要更精确的正则)
        if "temperature" in ent.text.lower() or "temp" in ent.text.lower():
             match = re.search(r'(\d+(\.\d+)?)\s*(°?C|°F|K)', ent.text)
             if match:
                 extracted_data["temperature"] = f"{match.group(1)} {match.group(3)}"
        if "pressure" in ent.text.lower():
             match = re.search(r'(\d+(\.\d+)?)\s*(Pa|kPa|MPa|bar|atm)', ent.text)
             if match:
                 extracted_data["pressure"] = f"{match.group(1)} {match.group(3)}"

    # 提取转化率、收率、选择性 (需要更精确的正则)
    conv_match = re.search(r'conversion\s*[:=]?\s*(\d+(\.\d+)?)%', user_description, re.IGNORECASE)
    if conv_match:
        extracted_data["conversion"] = float(conv_match.group(1))
        extracted_data["kinetic_params_provided"] = True # 假设提供转化率就意味着有动力学相关信息

    yield_match = re.search(r'yield\s*[:=]?\s*(\d+(\.\d+)?)%', user_description, re.IGNORECASE)
    if yield_match:
        extracted_data["yield"] = float(yield_match.group(1))
        extracted_data["kinetic_params_provided"] = True

    select_match = re.search(r'selectivity\s*[:=]?\s*(\d+(\.\d+)?)%', user_description, re.IGNORECASE)
    if select_match:
        extracted_data["selectivity"] = float(select_match.group(1))
        extracted_data["kinetic_params_provided"] = True

    # 检查是否有动力学参数关键词
    if any(keyword in user_description.lower() for keyword in ["kinetics", "rate constant", "activation energy"]):
        extracted_data["kinetic_params_provided"] = True

    # 检查是否有平衡相关关键词
    if any(keyword in user_description.lower() for keyword in ["equilibrium", "reversible reaction", "ka", "gibbs free energy"]):
        extracted_data["equilibrium_info_provided"] = True

    # -----------------------------------------------------------
    # 示例：根据关键词提示反应器类型
    # -----------------------------------------------------------
    if "equilibrium" in user_description.lower() or "reversible" in user_description.lower():
         extracted_data["reactor_type_hint"] = "Equilibrium"
    elif "gibbs" in user_description.lower():
         extracted_data["reactor_type_hint"] = "Gibbs"
    elif extracted_data["kinetic_params_provided"] or extracted_data["conversion"] is not None:
         extracted_data["reactor_type_hint"] = "Conversion" # 默认 Conversion Reactor

    # -----------------------------------------------------------
    # TODO: 更多复杂的 NLP 逻辑，例如：
    # - 精确区分反应物和产物
    # - 处理摩尔比、流量等信息
    # - 处理单位转换
    # - 使用 Hugging Face models 进行更精准的 NER 或关系抽取
    # -----------------------------------------------------------

    print(f"Extracted Data: {extracted_data}")
    return extracted_data

# --- 示例用法 ---
if __name__ == "__main__":
    # 假设的用户输入 (需要根据实际场景来)
    example_description = """
    Simulate a reaction where methane and steam react to form hydrogen and carbon monoxide.
    The temperature is 800 C and pressure is 10 atm.
    The conversion of methane is 95%.
    This is a reversible reaction.
    """
    parsed_data = parse_user_input(example_description)
    # 在这里可以根据 parsed_data 来决定 Reactor 类型