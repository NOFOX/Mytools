"""
Random Generator Tool - 随机数生成实用工具
支持随机数规则管理、随机数生成规则管理和随机数据生成
"""

import gradio as gr
import random
import string
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import os
import base64

# 工具元数据
TOOL_NAME = "随机数生成器"
TOOL_DESCRIPTION = "提供随机数规则管理、随机数生成规则管理和随机数据生成功能。支持自定义随机数列表、长度设置、去重选项和多种过滤形态。"

# 数据存储文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
RANDOM_RULES_FILE = os.path.join(DATA_DIR, "random_rules.json")
GENERATION_RULES_FILE = os.path.join(DATA_DIR, "generation_rules.json")
LOG_FILE = os.path.join(DATA_DIR, "generation_log.json")


@dataclass
class RandomRule:
    """随机数规则"""
    id: str
    name: str
    random_list: List[str]  # 随机数列表
    length: int  # 随机长度
    deduplicate: bool  # 是否去重
    filter_patterns: List[str]  # 过滤形态
    output_count: int  # 期望输出个数
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GenerationRule:
    """随机数生成规则"""
    id: str
    name: str
    left_rule_id: str  # 左侧随机数规则 ID
    right_rule_id: str  # 右侧随机数规则 ID
    generation_method: str  # 生成方式：拼接、合集、并集
    deduplicate: bool  # 是否去重
    output_count: int  # 期望输出个数
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GenerationLog:
    """生成日志"""
    id: str
    timestamp: str
    rule_type: str  # "random" 或 "generation"
    rule_name: str
    rule_details: Dict[str, Any]
    generated_data: List[str]
    count: int


def ensure_data_dir():
    """确保数据目录存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_json_file(filepath: str, default: Any = None) -> Any:
    """加载 JSON 文件"""
    ensure_data_dir()
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default if default is not None else []
    return default if default is not None else []


def save_json_file(filepath: str, data: Any):
    """保存 JSON 文件"""
    ensure_data_dir()
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_random_rules() -> List[Dict]:
    """加载随机数规则"""
    return load_json_file(RANDOM_RULES_FILE, [])


def save_random_rules(rules: List[Dict]):
    """保存随机数规则"""
    save_json_file(RANDOM_RULES_FILE, rules)


def load_generation_rules() -> List[Dict]:
    """加载随机数生成规则"""
    return load_json_file(GENERATION_RULES_FILE, [])


def save_generation_rules(rules: List[Dict]):
    """保存随机数生成规则"""
    save_json_file(GENERATION_RULES_FILE, rules)


def load_logs() -> List[Dict]:
    """加载日志"""
    return load_json_file(LOG_FILE, [])


def save_logs(logs: List[Dict]):
    """保存日志"""
    save_json_file(LOG_FILE, logs)


def generate_id(prefix: str = "") -> str:
    """生成唯一 ID"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}{timestamp}_{random_suffix}" if prefix else f"{timestamp}_{random_suffix}"


def check_pattern_match(data: str, pattern: str) -> bool:
    """检查数据是否匹配指定模式"""
    if len(data) < 3:
        return False
    
    # 全豹子：所有字符相同（至少 3 个）
    if pattern == "全豹子":
        return len(set(data)) == 1 and len(data) >= 3
    
    # 三豹子 AAA（前三个相同）
    if pattern == "三豹子AAA":
        return len(data) >= 3 and data[0] == data[1] == data[2]
    
    # 四豹子 AAAA（前四个相同）
    if pattern == "四豹子 AAAA":
        return len(data) >= 4 and data[0] == data[1] == data[2] == data[3]
    
    # 五豹子 AAAAA（前五个相同）
    if pattern == "五豹子 AAAAA":
        return len(data) >= 5 and all(data[i] == data[0] for i in range(5))
    
    # 六豹子 AAAAAA（前六个相同）
    if pattern == "六豹子 AAAAAA":
        return len(data) >= 6 and all(data[i] == data[0] for i in range(6))
    
    # 七豹子 AAAAAAA（前七个相同）
    if pattern == "七豹子 AAAAAAA":
        return len(data) >= 7 and all(data[i] == data[0] for i in range(7))
    
    # 三连 ABC（连续递增 3 个字符）
    if pattern == "三连 ABC":
        if len(data) < 3:
            return False
        for i in range(len(data) - 2):
            if (ord(data[i+1]) - ord(data[i]) == 1 and 
                ord(data[i+2]) - ord(data[i+1]) == 1):
                return True
        return False
    
    # ABAB 模式
    if pattern == "ABAB":
        if len(data) < 4:
            return False
        return data[0] == data[2] and data[1] == data[3] and data[0] != data[1]
    
    # ABCABC 模式
    if pattern == "ABCABC":
        if len(data) < 6:
            return False
        return data[:3] == data[3:6] and len(set(data[:3])) == 3
    
    # ABCD 模式（连续递增 4 个）
    if pattern == "ABCD":
        if len(data) < 4:
            return False
        for i in range(len(data) - 3):
            if (ord(data[i+1]) - ord(data[i]) == 1 and 
                ord(data[i+2]) - ord(data[i+1]) == 1 and 
                ord(data[i+3]) - ord(data[i+2]) == 1):
                return True
        return False
    
    # ABCDE 模式（连续递增 5 个）
    if pattern == "ABCDE":
        if len(data) < 5:
            return False
        for i in range(len(data) - 4):
            if all(ord(data[i+j+1]) - ord(data[i+j]) == 1 for j in range(4)):
                return True
        return False
    
    return False


def filter_by_patterns(data_list: List[str], patterns: List[str]) -> List[str]:
    """根据模式过滤数据"""
    if not patterns:
        return data_list
    
    filtered = []
    for item in data_list:
        for pattern in patterns:
            if check_pattern_match(item, pattern):
                filtered.append(item)
                break
    return filtered


def generate_random_data(rule: Dict, log_info: Optional[Dict] = None) -> Tuple[List[str], str]:
    """根据随机数规则生成随机数据"""
    random_list = rule.get('random_list', list(string.ascii_lowercase))
    length = int(rule.get('length', 6))
    deduplicate = rule.get('deduplicate', False)
    filter_patterns = rule.get('filter_patterns', [])
    output_count = int(rule.get('output_count', 10))
    
    if not random_list:
        random_list = list(string.ascii_lowercase)
    
    results = []
    attempts = 0
    max_attempts = output_count * 100  # 防止无限循环
    
    while len(results) < output_count and attempts < max_attempts:
        attempts += 1
        
        # 生成随机字符串
        if deduplicate and len(random_list) >= length:
            # 不去重地从列表中选取
            selected = random.choices(random_list, k=length)
        else:
            selected = random.choices(random_list, k=length)
        
        result = ''.join(selected)
        
        # 如果有过滤条件，检查是否匹配
        if filter_patterns:
            if not any(check_pattern_match(result, p) for p in filter_patterns):
                continue
        
        # 如果已存在且要求去重，跳过
        if deduplicate and result in results:
            continue
        
        results.append(result)
    
    # 如果启用了去重但结果不足，尝试再次去重
    if deduplicate:
        results = list(dict.fromkeys(results))
    
    # 生成日志信息
    log_details = {
        'rule_type': 'random',
        'rule_name': rule.get('name', '未命名规则'),
        'rule_details': rule,
        'generated_data': results,
        'count': len(results),
        'timestamp': datetime.now().isoformat()
    }
    
    return results, json.dumps(log_details, ensure_ascii=False, indent=2)


def generate_by_generation_rule(rule: Dict, random_rules: List[Dict]) -> Tuple[List[str], str]:
    """根据生成规则生成随机数据"""
    left_rule_id = rule.get('left_rule_id')
    right_rule_id = rule.get('right_rule_id')
    method = rule.get('generation_method', '拼接')
    deduplicate = rule.get('deduplicate', False)
    output_count = int(rule.get('output_count', 10))
    
    # 查找对应的随机数规则
    left_rule = None
    right_rule = None
    for r in random_rules:
        if r.get('id') == left_rule_id:
            left_rule = r
        if r.get('id') == right_rule_id:
            right_rule = r
    
    if not left_rule or not right_rule:
        return [], json.dumps({"error": "未找到对应的随机数规则"}, ensure_ascii=False, indent=2)
    
    # 生成左右两侧的数据
    left_data, _ = generate_random_data(left_rule)
    right_data, _ = generate_random_data(right_rule)
    
    results = []
    
    if method == '拼接':
        # 拼接：左 + 右
        for l in left_data:
            for r in right_data:
                results.append(l + r)
    elif method == '合集':
        # 合集：合并两个列表
        results = left_data + right_data
    elif method == '并集':
        # 并集：合并并去重
        results = list(set(left_data + right_data))
    
    # 处理去重
    if deduplicate:
        results = list(dict.fromkeys(results))
    
    # 限制输出数量
    if len(results) > output_count:
        results = random.sample(results, min(output_count, len(results)))
    
    # 生成日志信息
    log_details = {
        'rule_type': 'generation',
        'rule_name': rule.get('name', '未命名规则'),
        'rule_details': rule,
        'left_rule': left_rule,
        'right_rule': right_rule,
        'generation_method': method,
        'generated_data': results,
        'count': len(results),
        'timestamp': datetime.now().isoformat()
    }
    
    return results, json.dumps(log_details, ensure_ascii=False, indent=2)


def format_download_content(data: List[str], rule_info: str = "") -> str:
    """格式化下载内容"""
    content = f"# 随机数生成结果\n"
    content += f"# 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    if rule_info:
        content += f"{rule_info}\n\n"
    content += "\n".join(data)
    return content


# ==================== Gradio 界面函数 ====================

def gradio_interface():
    """定义并返回此工具的 Gradio 用户界面"""
    
    with gr.Blocks(
        theme=gr.themes.Soft(),
        title=TOOL_NAME,
        css="""
        .log-area { font-family: monospace; font-size: 12px; }
        .result-area { font-family: monospace; font-size: 14px; }
        .rule-card { margin: 10px 0; }
        """
    ) as demo:
        gr.Markdown(f"# {TOOL_NAME}")
        gr.Markdown(TOOL_DESCRIPTION)
        
        with gr.Tabs():
            # ==================== 标签页 1: 随机数规则管理 ====================
            with gr.Tab("📋 随机数规则管理"):
                gr.Markdown("### 创建、修改、删除随机数规则")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 规则列表")
                        random_rules_list = gr.Dropdown(
                            label="选择规则",
                            choices=[],
                            interactive=True,
                            info="从下拉列表中选择要查看或编辑的规则"
                        )
                        refresh_rules_btn = gr.Button("🔄 刷新列表", variant="secondary")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("#### 规则详情")
                        rule_name_input = gr.Textbox(
                            label="规则名称",
                            placeholder="输入规则名称，例如：字母规则",
                            info="给规则起一个易于识别的名称"
                        )
                        
                        random_list_input = gr.Textbox(
                            label="随机数列表（必填）",
                            placeholder="a b c d e f g h i j k l m n o p q r s t u v w x y z",
                            value="a b c d e f g h i j k l m n o p q r s t u v w x y z",
                            lines=3,
                            info="支持中文字符串，用空格分隔。默认是 26 个小写字母"
                        )
                        
                        random_length_input = gr.Number(
                            label="随机长度（必填）",
                            value=6,
                            minimum=1,
                            maximum=100,
                            step=1,
                            info="每个随机数由多少个元素组成"
                        )
                        
                        deduplicate_checkbox = gr.Checkbox(
                            label="是否去重",
                            value=False,
                            info="生成的随机数是否去除重复项"
                        )
                        
                        filter_patterns_dropdown = gr.Dropdown(
                            label="过滤形态（可多选）",
                            choices=[
                                "全豹子",
                                "三豹子 AAA",
                                "四豹子 AAAA",
                                "五豹子 AAAAA",
                                "六豹子 AAAAAA",
                                "七豹子 AAAAAAA",
                                "三连 ABC",
                                "ABAB",
                                "ABCABC",
                                "ABCD",
                                "ABCDE"
                            ],
                            multiselect=True,
                            info="选择需要保留的随机数形态，不选则不过滤"
                        )
                        
                        output_count_input = gr.Number(
                            label="期望输出个数",
                            value=10,
                            minimum=1,
                            maximum=10000,
                            step=1,
                            info="期望生成多少个随机数"
                        )
                
                with gr.Row():
                    save_rule_btn = gr.Button("💾 保存规则", variant="primary")
                    update_rule_btn = gr.Button("✏️ 更新规则", variant="secondary")
                    delete_rule_btn = gr.Button("🗑️ 删除规则", variant="stop")
                    clear_form_btn = gr.Button("🧹 清空表单", variant="secondary")
                
                rule_message = gr.Textbox(
                    label="操作结果",
                    interactive=False,
                    visible=True
                )
                
                # 隐藏字段用于存储当前编辑的规则 ID
                current_rule_id = gr.Textbox(visible=False, value="")
            
            # ==================== 标签页 2: 随机数生成规则管理 ====================
            with gr.Tab("🔧 随机数生成规则管理"):
                gr.Markdown("### 创建、修改、删除随机数生成规则")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 规则列表")
                        gen_rules_list = gr.Dropdown(
                            label="选择规则",
                            choices=[],
                            interactive=True,
                            info="从下拉列表中选择要查看或编辑的规则"
                        )
                        refresh_gen_rules_btn = gr.Button("🔄 刷新列表", variant="secondary")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("#### 规则详情")
                        gen_rule_name_input = gr.Textbox(
                            label="规则名称",
                            placeholder="输入规则名称，例如：组合规则",
                            info="给规则起一个易于识别的名称"
                        )
                        
                        left_rule_dropdown = gr.Dropdown(
                            label="左侧随机数规则（必填）",
                            choices=[],
                            interactive=True,
                            info="选择左侧使用的随机数规则"
                        )
                        
                        generation_method_dropdown = gr.Dropdown(
                            label="生成方式（必填）",
                            choices=["拼接", "合集", "并集"],
                            value="拼接",
                            interactive=True,
                            info="选择左右规则的生成方式"
                        )
                        
                        right_rule_dropdown = gr.Dropdown(
                            label="右侧随机数规则（必填）",
                            choices=[],
                            interactive=True,
                            info="选择右侧使用的随机数规则"
                        )
                        
                        gen_deduplicate_checkbox = gr.Checkbox(
                            label="是否去重",
                            value=False,
                            info="生成的结果是否去除重复项"
                        )
                        
                        gen_output_count_input = gr.Number(
                            label="期望输出个数",
                            value=10,
                            minimum=1,
                            maximum=10000,
                            step=1,
                            info="期望生成多少个随机数"
                        )
                
                with gr.Row():
                    save_gen_rule_btn = gr.Button("💾 保存规则", variant="primary")
                    update_gen_rule_btn = gr.Button("✏️ 更新规则", variant="secondary")
                    delete_gen_rule_btn = gr.Button("🗑️ 删除规则", variant="stop")
                    clear_gen_form_btn = gr.Button("🧹 清空表单", variant="secondary")
                
                gen_rule_message = gr.Textbox(
                    label="操作结果",
                    interactive=False,
                    visible=True
                )
                
                # 隐藏字段用于存储当前编辑的规则 ID
                current_gen_rule_id = gr.Textbox(visible=False, value="")
            
            # ==================== 标签页 3: 随机数生成 ====================
            with gr.Tab("🎲 随机数生成"):
                gr.Markdown("### 选择规则生成随机数")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("#### 选择生成方式")
                        generation_mode = gr.Radio(
                            label="生成模式",
                            choices=[
                                ("使用随机数规则", "random"),
                                ("使用生成规则", "generation")
                            ],
                            value="random",
                            interactive=True
                        )
                        
                        select_random_rule = gr.Dropdown(
                            label="选择随机数规则",
                            choices=[],
                            interactive=True,
                            visible=True,
                            info="选择要使用的随机数规则"
                        )
                        
                        select_gen_rule = gr.Dropdown(
                            label="选择生成规则",
                            choices=[],
                            interactive=True,
                            visible=False,
                            info="选择要使用的生成规则"
                        )
                        
                        generate_btn = gr.Button("🚀 生成随机数", variant="primary", size="lg")
                    
                    with gr.Column(scale=2):
                        gr.Markdown("#### 生成结果")
                        result_display = gr.Textbox(
                            label="生成的随机数",
                            lines=10,
                            interactive=False,
                            elem_classes=["result-area"]
                        )
                        
                        with gr.Row():
                            copy_btn = gr.Button("📋 复制结果", variant="secondary")
                            download_btn = gr.Button("📥 下载结果", variant="secondary")
                        
                        copy_message = gr.Textbox(
                            label="",
                            visible=False,
                            interactive=False
                        )
                
                # 日志显示
                gr.Markdown("#### 📜 详细日志")
                log_display = gr.Textbox(
                    label="生成日志",
                    lines=15,
                    interactive=False,
                    elem_classes=["log-area"],
                    info="显示详细的生成规则和过程信息"
                )
            
            # ==================== 标签页 4: 日志查看 ====================
            with gr.Tab("📖 日志查看"):
                gr.Markdown("### 查看历史生成日志")
                
                with gr.Row():
                    refresh_log_btn = gr.Button("🔄 刷新日志", variant="secondary")
                    clear_log_btn = gr.Button("🗑️ 清空日志", variant="stop")
                    export_log_btn = gr.Button("📤 导出日志", variant="secondary")
                
                log_count_slider = gr.Slider(
                    minimum=1,
                    maximum=100,
                    value=20,
                    step=1,
                    label="显示最近 N 条日志"
                )
                
                log_history_display = gr.Textbox(
                    label="历史日志",
                    lines=20,
                    interactive=False,
                    elem_classes=["log-area"]
                )
                
                log_message = gr.Textbox(
                    label="操作结果",
                    interactive=False,
                    visible=True
                )
        
        # ==================== 事件处理函数 ====================
        
        def refresh_random_rules_list():
            """刷新随机数规则下拉列表"""
            rules = load_random_rules()
            choices = [(r.get('name', '未命名'), r.get('id')) for r in rules]
            return (
                gr.update(choices=choices),
                gr.update(choices=choices),
                gr.update(choices=choices),
                gr.update(choices=choices)
            )
        
        def refresh_generation_rules_list():
            """刷新生成规则下拉列表"""
            rules = load_generation_rules()
            choices = [(r.get('name', '未命名'), r.get('id')) for r in rules]
            return gr.update(choices=choices), gr.update(choices=choices)
        
        def load_random_rule_detail(rule_id):
            """加载随机数规则详情"""
            if not rule_id:
                return "", "", 6, False, [], 10, ""
            
            rules = load_random_rules()
            for rule in rules:
                if rule.get('id') == rule_id:
                    return (
                        rule.get('name', ''),
                        ' '.join(rule.get('random_list', [])),
                        rule.get('length', 6),
                        rule.get('deduplicate', False),
                        rule.get('filter_patterns', []),
                        rule.get('output_count', 10),
                        rule.get('id', '')
                    )
            return "", "", 6, False, [], 10, ""
        
        def load_generation_rule_detail(rule_id):
            """加载生成规则详情"""
            if not rule_id:
                return "", "", "拼接", "", False, 10, ""
            
            rules = load_generation_rules()
            for rule in rules:
                if rule.get('id') == rule_id:
                    return (
                        rule.get('name', ''),
                        rule.get('left_rule_id', ''),
                        rule.get('generation_method', '拼接'),
                        rule.get('right_rule_id', ''),
                        rule.get('deduplicate', False),
                        rule.get('output_count', 10),
                        rule.get('id', '')
                    )
            return "", "", "拼接", "", False, 10, ""
        
        def save_random_rule(name, random_list_str, length, deduplicate, filter_patterns, output_count):
            """保存随机数规则"""
            if not name:
                return "❌ 错误：规则名称不能为空"
            if not random_list_str.strip():
                return "❌ 错误：随机数列表不能为空"
            
            random_list = [x.strip() for x in random_list_str.split() if x.strip()]
            if not random_list:
                return "❌ 错误：随机数列表至少包含一个元素"
            
            rule_id = generate_id("RR_")
            rule = {
                'id': rule_id,
                'name': name,
                'random_list': random_list,
                'length': int(length),
                'deduplicate': deduplicate,
                'filter_patterns': filter_patterns if filter_patterns else [],
                'output_count': int(output_count),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            rules = load_random_rules()
            rules.append(rule)
            save_random_rules(rules)
            
            return f"✅ 成功保存规则：{name}（ID: {rule_id}）"
        
        def update_random_rule(rule_id, name, random_list_str, length, deduplicate, filter_patterns, output_count):
            """更新随机数规则"""
            if not rule_id:
                return "❌ 错误：请先选择一个规则进行更新"
            if not name:
                return "❌ 错误：规则名称不能为空"
            if not random_list_str.strip():
                return "❌ 错误：随机数列表不能为空"
            
            random_list = [x.strip() for x in random_list_str.split() if x.strip()]
            if not random_list:
                return "❌ 错误：随机数列表至少包含一个元素"
            
            rules = load_random_rules()
            found = False
            for rule in rules:
                if rule.get('id') == rule_id:
                    rule['name'] = name
                    rule['random_list'] = random_list
                    rule['length'] = int(length)
                    rule['deduplicate'] = deduplicate
                    rule['filter_patterns'] = filter_patterns if filter_patterns else []
                    rule['output_count'] = int(output_count)
                    rule['updated_at'] = datetime.now().isoformat()
                    found = True
                    break
            
            if not found:
                return "❌ 错误：未找到指定的规则"
            
            save_random_rules(rules)
            return f"✅ 成功更新规则：{name}"
        
        def delete_random_rule(rule_id):
            """删除随机数规则"""
            if not rule_id:
                return "❌ 错误：请先选择一个规则进行删除"
            
            rules = load_random_rules()
            new_rules = [r for r in rules if r.get('id') != rule_id]
            
            if len(new_rules) == len(rules):
                return "❌ 错误：未找到指定的规则"
            
            save_random_rules(new_rules)
            return f"✅ 成功删除规则（ID: {rule_id}）"
        
        def save_generation_rule(name, left_rule_id, method, right_rule_id, deduplicate, output_count):
            """保存生成规则"""
            if not name:
                return "❌ 错误：规则名称不能为空"
            if not left_rule_id:
                return "❌ 错误：请选择左侧随机数规则"
            if not right_rule_id:
                return "❌ 错误：请选择右侧随机数规则"
            if not method:
                return "❌ 错误：请选择生成方式"
            
            rule_id = generate_id("GR_")
            rule = {
                'id': rule_id,
                'name': name,
                'left_rule_id': left_rule_id,
                'right_rule_id': right_rule_id,
                'generation_method': method,
                'deduplicate': deduplicate,
                'output_count': int(output_count),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            rules = load_generation_rules()
            rules.append(rule)
            save_generation_rules(rules)
            
            return f"✅ 成功保存规则：{name}（ID: {rule_id}）"
        
        def update_generation_rule(rule_id, name, left_rule_id, method, right_rule_id, deduplicate, output_count):
            """更新生成规则"""
            if not rule_id:
                return "❌ 错误：请先选择一个规则进行更新"
            if not name:
                return "❌ 错误：规则名称不能为空"
            if not left_rule_id:
                return "❌ 错误：请选择左侧随机数规则"
            if not right_rule_id:
                return "❌ 错误：请选择右侧随机数规则"
            
            rules = load_generation_rules()
            found = False
            for rule in rules:
                if rule.get('id') == rule_id:
                    rule['name'] = name
                    rule['left_rule_id'] = left_rule_id
                    rule['right_rule_id'] = right_rule_id
                    rule['generation_method'] = method
                    rule['deduplicate'] = deduplicate
                    rule['output_count'] = int(output_count)
                    rule['updated_at'] = datetime.now().isoformat()
                    found = True
                    break
            
            if not found:
                return "❌ 错误：未找到指定的规则"
            
            save_generation_rules(rules)
            return f"✅ 成功更新规则：{name}"
        
        def delete_generation_rule(rule_id):
            """删除生成规则"""
            if not rule_id:
                return "❌ 错误：请先选择一个规则进行删除"
            
            rules = load_generation_rules()
            new_rules = [r for r in rules if r.get('id') != rule_id]
            
            if len(new_rules) == len(rules):
                return "❌ 错误：未找到指定的规则"
            
            save_generation_rules(new_rules)
            return f"✅ 成功删除规则（ID: {rule_id}）"
        
        def generate_random_numbers(mode, random_rule_id, gen_rule_id):
            """生成随机数"""
            if mode == "random":
                if not random_rule_id:
                    return "请先选择一个随机数规则", "", "[]"
                
                rules = load_random_rules()
                selected_rule = None
                for rule in rules:
                    if rule.get('id') == random_rule_id:
                        selected_rule = rule
                        break
                
                if not selected_rule:
                    return "未找到指定的规则", "", "[]"
                
                results, log_json = generate_random_data(selected_rule)
                
                if not results:
                    return "未能生成符合要求的随机数，请调整规则参数", "", log_json
                
                result_text = '\n'.join(results)
                return result_text, "", log_json
            
            else:  # generation mode
                if not gen_rule_id:
                    return "请先选择一个生成规则", "", "[]"
                
                gen_rules = load_generation_rules()
                random_rules = load_random_rules()
                selected_rule = None
                
                for rule in gen_rules:
                    if rule.get('id') == gen_rule_id:
                        selected_rule = rule
                        break
                
                if not selected_rule:
                    return "未找到指定的规则", "", "[]"
                
                results, log_json = generate_by_generation_rule(selected_rule, random_rules)
                
                if not results:
                    return "未能生成符合要求的随机数，请调整规则参数", "", log_json
                
                result_text = '\n'.join(results)
                return result_text, "", log_json
        
        def copy_results(result_text):
            """复制结果（返回提示信息）"""
            if not result_text:
                return "没有可复制的内容"
            return f"已复制 {len(result_text.splitlines())} 行结果到剪贴板"
        
        def download_results(result_text, log_json):
            """下载结果"""
            if not result_text:
                return None
            
            content = f"# 随机数生成结果\n"
            content += f"# 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            
            # 添加规则信息
            try:
                log_data = json.loads(log_json)
                content += f"# 规则名称：{log_data.get('rule_name', '未知')}\n"
                content += f"# 规则类型：{'生成规则' if log_data.get('rule_type') == 'generation' else '随机数规则'}\n\n"
            except:
                pass
            
            content += result_text
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"random_result_{timestamp}.txt"
            
            return (content, filename)
        
        def refresh_logs(limit=20):
            """刷新日志显示"""
            logs = load_logs()
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            logs = logs[:int(limit)]
            
            if not logs:
                return "暂无日志记录"
            
            log_text = ""
            for log in logs:
                log_text += f"{'='*60}\n"
                log_text += f"时间：{log.get('timestamp', '未知')}\n"
                log_text += f"类型：{'生成规则' if log.get('rule_type') == 'generation' else '随机数规则'}\n"
                log_text += f"规则名称：{log.get('rule_name', '未知')}\n"
                log_text += f"生成数量：{log.get('count', 0)}\n"
                log_text += f"部分数据：{', '.join(log.get('generated_data', [])[:5])}...\n"
                log_text += f"{'='*60}\n\n"
            
            return log_text
        
        def clear_logs():
            """清空日志"""
            save_logs([])
            return "✅ 日志已清空"
        
        def export_logs():
            """导出日志"""
            logs = load_logs()
            if not logs:
                return None
            
            content = json.dumps(logs, ensure_ascii=False, indent=2)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"generation_logs_{timestamp}.json"
            
            return (content, filename)
        
        def add_log_entry(log_json):
            """添加日志条目"""
            try:
                log_data = json.loads(log_json)
                logs = load_logs()
                logs.append(log_data)
                save_logs(logs)
            except:
                pass
            return log_json
        
        def toggle_generation_mode(mode):
            """切换生成模式"""
            return (
                gr.update(visible=(mode == "random")),
                gr.update(visible=(mode == "generation"))
            )
        
        # ==================== 绑定事件 ====================
        
        # 随机数规则管理事件
        refresh_rules_btn.click(
            fn=refresh_random_rules_list,
            outputs=[random_rules_list, select_random_rule, left_rule_dropdown, right_rule_dropdown]
        )
        
        random_rules_list.change(
            fn=load_random_rule_detail,
            inputs=[random_rules_list],
            outputs=[rule_name_input, random_list_input, random_length_input, 
                    deduplicate_checkbox, filter_patterns_dropdown, output_count_input, current_rule_id]
        )
        
        save_rule_btn.click(
            fn=save_random_rule,
            inputs=[rule_name_input, random_list_input, random_length_input, 
                    deduplicate_checkbox, filter_patterns_dropdown, output_count_input],
            outputs=[rule_message]
        ).then(
            fn=refresh_random_rules_list,
            outputs=[random_rules_list, select_random_rule, left_rule_dropdown, right_rule_dropdown]
        ).then(
            fn=lambda: "",
            outputs=[current_rule_id]
        )
        
        update_rule_btn.click(
            fn=update_random_rule,
            inputs=[current_rule_id, rule_name_input, random_list_input, random_length_input,
                    deduplicate_checkbox, filter_patterns_dropdown, output_count_input],
            outputs=[rule_message]
        ).then(
            fn=refresh_random_rules_list,
            outputs=[random_rules_list, select_random_rule, left_rule_dropdown, right_rule_dropdown]
        )
        
        delete_rule_btn.click(
            fn=delete_random_rule,
            inputs=[current_rule_id],
            outputs=[rule_message]
        ).then(
            fn=refresh_random_rules_list,
            outputs=[random_rules_list, select_random_rule, left_rule_dropdown, right_rule_dropdown]
        ).then(
            fn=lambda: ("", "", 6, False, [], 10, ""),
            outputs=[rule_name_input, random_list_input, random_length_input,
                    deduplicate_checkbox, filter_patterns_dropdown, output_count_input, current_rule_id]
        )
        
        clear_form_btn.click(
            fn=lambda: ("", "a b c d e f g h i j k l m n o p q r s t u v w x y z", 6, False, [], 10, ""),
            outputs=[rule_name_input, random_list_input, random_length_input,
                    deduplicate_checkbox, filter_patterns_dropdown, output_count_input, current_rule_id]
        ).then(
            fn=lambda: "",
            outputs=[rule_message]
        )
        
        # 生成规则管理事件
        refresh_gen_rules_btn.click(
            fn=refresh_generation_rules_list,
            outputs=[gen_rules_list, select_gen_rule]
        )
        
        gen_rules_list.change(
            fn=load_generation_rule_detail,
            inputs=[gen_rules_list],
            outputs=[gen_rule_name_input, left_rule_dropdown, generation_method_dropdown,
                    right_rule_dropdown, gen_deduplicate_checkbox, gen_output_count_input, current_gen_rule_id]
        )
        
        save_gen_rule_btn.click(
            fn=save_generation_rule,
            inputs=[gen_rule_name_input, left_rule_dropdown, generation_method_dropdown,
                    right_rule_dropdown, gen_deduplicate_checkbox, gen_output_count_input],
            outputs=[gen_rule_message]
        ).then(
            fn=refresh_generation_rules_list,
            outputs=[gen_rules_list, select_gen_rule]
        ).then(
            fn=lambda: "",
            outputs=[current_gen_rule_id]
        )
        
        update_gen_rule_btn.click(
            fn=update_generation_rule,
            inputs=[current_gen_rule_id, gen_rule_name_input, left_rule_dropdown, generation_method_dropdown,
                    right_rule_dropdown, gen_deduplicate_checkbox, gen_output_count_input],
            outputs=[gen_rule_message]
        ).then(
            fn=refresh_generation_rules_list,
            outputs=[gen_rules_list, select_gen_rule]
        )
        
        delete_gen_rule_btn.click(
            fn=delete_generation_rule,
            inputs=[current_gen_rule_id],
            outputs=[gen_rule_message]
        ).then(
            fn=refresh_generation_rules_list,
            outputs=[gen_rules_list, select_gen_rule]
        ).then(
            fn=lambda: ("", "", "拼接", "", False, 10, ""),
            outputs=[gen_rule_name_input, left_rule_dropdown, generation_method_dropdown,
                    right_rule_dropdown, gen_deduplicate_checkbox, gen_output_count_input, current_gen_rule_id]
        )
        
        clear_gen_form_btn.click(
            fn=lambda: ("", "", "拼接", "", False, 10, ""),
            outputs=[gen_rule_name_input, left_rule_dropdown, generation_method_dropdown,
                    right_rule_dropdown, gen_deduplicate_checkbox, gen_output_count_input, current_gen_rule_id]
        ).then(
            fn=lambda: "",
            outputs=[gen_rule_message]
        )
        
        # 随机数生成事件
        generation_mode.change(
            fn=toggle_generation_mode,
            inputs=[generation_mode],
            outputs=[select_random_rule, select_gen_rule]
        )
        
        generate_btn.click(
            fn=generate_random_numbers,
            inputs=[generation_mode, select_random_rule, select_gen_rule],
            outputs=[result_display, copy_message, log_display]
        ).then(
            fn=add_log_entry,
            inputs=[log_display],
            outputs=[]
        )
        
        copy_btn.click(
            fn=copy_results,
            inputs=[result_display],
            outputs=[copy_message]
        )
        
        download_btn.click(
            fn=download_results,
            inputs=[result_display, log_display],
            outputs=[download_btn]
        )
        
        # 日志事件
        refresh_log_btn.click(
            fn=refresh_logs,
            inputs=[log_count_slider],
            outputs=[log_history_display]
        )
        
        clear_log_btn.click(
            fn=clear_logs,
            outputs=[log_message]
        ).then(
            fn=refresh_logs,
            inputs=[log_count_slider],
            outputs=[log_history_display]
        )
        
        export_log_btn.click(
            fn=export_logs,
            outputs=[export_log_btn]
        )
        
        # 初始化加载
        demo.load(
            fn=refresh_random_rules_list,
            outputs=[random_rules_list, select_random_rule, left_rule_dropdown, right_rule_dropdown]
        ).then(
            fn=refresh_generation_rules_list,
            outputs=[gen_rules_list, select_gen_rule]
        ).then(
            fn=refresh_logs,
            inputs=[log_count_slider],
            outputs=[log_history_display]
        )
    
    return demo
