import gradio as gr

# 1. 工具名称
TOOL_NAME = "文本大小写转换"

# 2. 工具描述
TOOL_DESCRIPTION = "将输入的文本转换为全大写、全小写或首字母大写。"

# 3. Gradio 界面函数
def gradio_interface():
    """
    定义并返回文本大小写转换工具的 Gradio 用户界面。
    
    返回:
        gradio.Interface: Gradio 界面对象。
    """

    def convert_case(text, conversion_type):
        """
        根据所选类型转换文本的大小写。
        """
        if not text:
            return "请输入文本内容。"
        
        if conversion_type == "全大写 (UPPERCASE)":
            return text.upper()
        elif conversion_type == "全小写 (lowercase)":
            return text.lower()
        elif conversion_type == "首字母大写 (Capitalize)":
            return text.capitalize()
        # 未来可以扩展更多类型，例如 Title Case, Sentence case 等
        # elif conversion_type == "标题大写 (Title Case)":
        #     return text.title()
        else:
            return "无效的转换类型。"

    iface = gr.Interface(
        fn=convert_case,
        inputs=[
            gr.Textbox(label="输入文本", placeholder="在此处输入需要转换的文本...", lines=5),
            gr.Radio(
                choices=["全大写 (UPPERCASE)", "全小写 (lowercase)", "首字母大写 (Capitalize)"], 
                label="选择转换类型", 
                value="全大写 (UPPERCASE)" # 默认选项
            )
        ],
        outputs=[
            gr.Textbox(label="转换结果", lines=5)
        ],
        title=TOOL_NAME,
        description=TOOL_DESCRIPTION,
        article=(
            "### 使用说明:\n"
            "1. 在“输入文本”框中粘贴或输入你想要转换的文本。\n"
            "2. 从“选择转换类型”中选择一种转换方式。\n"
            "3. 点击“Submit”按钮，转换后的文本将显示在“转换结果”框中。"
        ),
        examples=[
            ["hello world", "全大写 (UPPERCASE)"],
            ["HELLO WORLD", "全小写 (lowercase)"],
            ["hELLO wORLD", "首字母大写 (Capitalize)"]
        ]
    )
    
    return iface

"""
工具开发提示:
- 确保 TOOL_NAME 和 TOOL_DESCRIPTION 清晰明了。
- `gradio_interface` 函数是核心，它定义了工具的交互方式。
- 在核心逻辑函数 (如 `convert_case`) 中处理各种输入情况和用户选择。
- 使用 Gradio 组件 (如 Textbox, Radio) 构建用户友好的界面。
- 提供 `examples` 可以帮助用户快速了解工具用法。
"""