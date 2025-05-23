import gradio as gr
import os
import sys

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# 工具脚本存放目录
TOOLS_DIR = os.path.join(BASE_DIR, "tools")
# 工具函数存放目录
UTILS_DIR = os.path.join(BASE_DIR, "utils")

# 将 utils 目录添加到 Python 模块搜索路径
if UTILS_DIR not in sys.path:
    sys.path.append(UTILS_DIR)

# 尝试导入工具加载器
try:
    import tool_loader
except ImportError:
    print("错误：无法导入 tool_loader.py。请确保 utils/tool_loader.py 文件存在且无误。")
    class MockToolLoader:
        def load_tools(self, path):
            print("警告：tool_loader 未成功加载，将使用空工具列表。")
            return []
    tool_loader = MockToolLoader()

# 全局变量，存储加载的工具信息
LOADED_TOOLS = []

def get_loaded_tools():
    """获取已加载的工具列表，如果尚未加载则进行加载。"""
    global LOADED_TOOLS
    if not LOADED_TOOLS:
        if not os.path.exists(TOOLS_DIR):
            os.makedirs(TOOLS_DIR)
            print(f"已创建工具目录: {TOOLS_DIR}")
        LOADED_TOOLS = tool_loader.load_tools(TOOLS_DIR)
        # 按工具名称排序
        LOADED_TOOLS.sort(key=lambda x: x.get('name', ''))
    return LOADED_TOOLS

def search_tools(query):
    """
    根据查询字符串模糊搜索工具。

    参数:
        query (str): 搜索关键词。

    返回:
        list: 匹配的工具列表。
    """
    tools = get_loaded_tools()
    if not query:
        return tools
    
    return [
        tool for tool in tools
        if query.lower() in tool.get('name', '').lower() or \
           query.lower() in tool.get('description', '').lower()
    ]

def create_tool_interface(tool_info):
    """创建工具的 Gradio 界面。"""
    if not tool_info or 'interface_fn' not in tool_info:
        return gr.Markdown("无法加载工具界面。")

    try:
        tool_interface = tool_info['interface_fn']()
        return tool_interface
    except Exception as e:
        error_message = f"加载工具 '{tool_info.get('name', '未知工具')}' 界面时出错: {e}"
        print(error_message)
        return gr.Markdown(error_message)

def create_main_interface():
    """创建主界面。"""
    tools = get_loaded_tools()
    
    # 创建一个 Blocks 应用
    with gr.Blocks(
        theme=gr.themes.Soft(),
        css="""
            /* 使用系统默认字体 */
            body, .gradio-container * { 
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
                             Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif !important; 
            }
            code, pre { 
                font-family: Consolas, Monaco, 'Courier New', monospace !important; 
            }
            /* 修复其他样式问题 */
            .gradio-container { max-width: 100% !important; }
            /* 工具列表样式 */
            .tool-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 16px;
                padding: 16px;
            }
            .tool-item {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 16px;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            .tool-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-color: #2196f3;
            }
            .tool-item h3 {
                margin: 0 0 8px 0;
                color: #1a73e8;
                font-size: 1.1em;
                font-weight: 600;
            }
            .tool-item p {
                margin: 0;
                color: #666;
                font-size: 0.9em;
                line-height: 1.4;
            }
            .search-container {
                max-width: 600px;
                margin: 0 auto 24px auto;
            }
            .welcome-text {
                text-align: center;
                max-width: 800px;
                margin: 0 auto 32px auto;
                padding: 0 16px;
            }
        """
    ) as demo:
        # 创建标签页组件
        tabs = gr.Tabs(selected=0)  # 默认选中首页
        
        with tabs:
            # 首页标签
            with gr.Tab("首页", id=0):
                with gr.Column(elem_classes=["welcome-text"]):
                    gr.Markdown("# MyTools 工具框架")
                    gr.Markdown("欢迎使用 MyTools 工具框架。使用搜索框查找工具或从下方列表选择。")
                
                # 搜索框
                with gr.Column(elem_classes=["search-container"]):
                    search_box = gr.Textbox(
                        label="搜索工具",
                        placeholder="输入工具名称或描述...",
                        show_label=True
                    )
                
                # 工具列表容器
                tool_list = gr.HTML()
                
                # 更新工具列表的函数
                def update_tool_list(query):
                    filtered_tools = search_tools(query)
                    tool_items = []
                    
                    for i, tool in enumerate(filtered_tools):
                        name = tool.get('name', '未知工具')
                        desc = tool.get('description', '')
                        tool_items.append(f"""
                            <div class="tool-item" data-tool-index="{i+1}" onclick="document.querySelector(`button[role='tab']:nth-child({i+2})`).click()">
                                <h3>{name}</h3>
                                <p>{desc}</p>
                            </div>
                        """)
                    
                    return f"""
                        <div class="tool-list">
                            {''.join(tool_items)}
                        </div>
                    """
                
                # 绑定搜索框事件
                search_box.change(
                    fn=update_tool_list,
                    inputs=[search_box],
                    outputs=[tool_list],
                    show_progress=False
                )
                
                # 初始显示所有工具
                tool_list.value = update_tool_list("")
            
            # 为每个工具创建标签页
            for i, tool in enumerate(tools):
                with gr.Tab(tool.get('name', '未知工具'), id=i+1):
                    create_tool_interface(tool)
    
    return demo

if __name__ == "__main__":
    # 确保 tools 和 utils 目录存在
    if not os.path.exists(TOOLS_DIR):
        os.makedirs(TOOLS_DIR)
        print(f"已创建工具目录: {TOOLS_DIR}")
    if not os.path.exists(UTILS_DIR):
        os.makedirs(UTILS_DIR)
        print(f"已创建 utils 目录: {UTILS_DIR}")
        print(f"请在 {UTILS_DIR} 目录下创建 tool_loader.py 文件。")
        print("tool_loader.py 应包含一个 load_tools(tools_dir_path) 函数，用于加载工具。")

    # 首次加载工具
    get_loaded_tools()
    
    # 创建并启动应用
    app_interface = create_main_interface()
    app_interface.launch(
        share=False,
        server_name="127.0.0.1",
        show_api=False,
        inbrowser=True,
    )