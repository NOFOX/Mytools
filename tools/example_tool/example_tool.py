import gradio as gr

# 1. 工具名称 (必选)
# 将在工具列表和工具页面上显示
TOOL_NAME = "示例工具"

# 2. 工具描述 (可选，但推荐)
# 简要说明工具的功能
TOOL_DESCRIPTION = "这是一个简单的示例工具，演示了如何在 MyTools 框架中添加新工具。它接受一个名字并返回问候语。"

# 3. Gradio 界面函数 (必选)
# 这个函数必须返回一个 Gradio Interface 或 Gradio Blocks 对象。
# Gradio 会使用这个对象来构建工具的用户界面和处理逻辑。
def gradio_interface():
    """
    定义并返回此工具的 Gradio 用户界面。
    
    返回:
        gradio.Interface: Gradio 界面对象。
    """

    # 定义工具的核心逻辑函数
    def greet(name, intensity):
        """
        根据输入的名字和强度生成问候语。
        """
        if not name:
            return "请输入一个名字！", ""
        
        greeting = f"你好, {name}! " * intensity
        detailed_output = f"已向 '{name}' 发送强度为 {intensity} 的问候。"
        return greeting, detailed_output

    # 创建 Gradio Interface
    # inputs: 定义输入组件的类型和标签
    # outputs: 定义输出组件的类型和标签
    # title: 界面的标题 (可选, 通常 TOOL_NAME 已经足够)
    # description: 界面的描述 (可选, 通常 TOOL_DESCRIPTION 已经足够)
    # article: 可以在界面底部添加更详细的说明或示例 (可选)
    # examples: 提供一些示例输入，方便用户快速测试 (可选)
    
    iface = gr.Interface(
        fn=greet,  # 指定核心逻辑函数
        inputs=[
            gr.Textbox(label="你的名字", placeholder="例如：张三"),
            gr.Slider(minimum=1, maximum=5, step=1, value=1, label="问候强度")
        ],
        outputs=[
            gr.Textbox(label="问候语"),
            gr.Textbox(label="详细输出")
        ],
        title=TOOL_NAME, # 可以省略，若省略则 Tab 名称已足够
        description=TOOL_DESCRIPTION, # 可以省略，若省略则 Tab 描述已足够
        article=(
            "### 如何使用:\n"
            "1. 在“你的名字”文本框中输入一个名字。\n"
            "2. 调整“问候强度”滑块来改变问候语的重复次数。\n"
            "3. 点击“Submit”按钮查看结果。"
        ),
        examples=[
            ["小明", 2],
            ["AI助手", 3]
        ]
    )
    
    return iface

# --- 可选的附加元数据或辅助函数 ---
# 你可以在这里定义工具可能需要的其他常量或辅助函数，
# 但它们不会被框架直接调用，除非被 `gradio_interface` 函数内部使用。

# 例如：
# API_KEY = "YOUR_SECRET_API_KEY" # 不推荐硬编码密钥，应通过其他方式管理
# def _internal_helper_function(data):
#     return data * 2


# --- 工具脚本开发指南 ---
"""
新工具脚本开发应保持尽可能简单及简洁。

核心要求:
1.  **`TOOL_NAME` (字符串)**: 工具的友好名称。
2.  **`TOOL_DESCRIPTION` (字符串)**: 工具的简短描述。
3.  **`gradio_interface()` (函数)**: 返回一个 `gradio.Interface` 或 `gradio.Blocks` 实例。
    这个函数封装了工具的UI和逻辑。

最佳实践:
-   **单一职责**: `gradio_interface()` 函数应专注于创建和返回Gradio界面。
    核心的业务逻辑可以封装在其他辅助函数中，然后由Gradio界面调用。
-   **清晰的输入输出**: 在 `gr.Interface` 中明确定义输入 (`inputs`) 和输出 (`outputs`) 组件。
    使用有意义的标签 (`label`) 和占位符 (`placeholder`)。
-   **错误处理**: 在你的逻辑函数 (如示例中的 `greet`) 中加入适当的错误处理和用户提示。
-   **用户体验**: 利用 `title`, `description`, `article`, `examples` 等参数增强Gradio界面的用户友好性。
-   **模块化**: 如果工具逻辑复杂，可以将其拆分到多个函数或类中，保持 `gradio_interface` 的简洁性。
-   **依赖管理**: 如果工具需要额外的Python包，请确保将它们添加到项目的 `requirements.txt` 文件中。
-   **无副作用导入**: 工具脚本在被 `tool_loader` 导入时不应执行耗时操作或产生副作用 (例如，立即连接到数据库或启动进程)。
    所有这类操作都应在 `gradio_interface` 返回的界面被用户实际交互时触发。
"""