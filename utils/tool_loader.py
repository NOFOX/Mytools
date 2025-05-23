import os
import importlib.util
import sys
import gradio as gr

def load_tools(tools_dir_path):
    """
    从指定目录加载所有工具。支持从子目录加载工具。

    工具可以通过以下两种方式之一组织：
    1. 子目录中的 __init__.py 文件
    2. 与子目录同名的 .py 文件放在子目录中

    每个工具都应该定义以下变量/函数：
    - TOOL_NAME (str): 工具的显示名称。
    - TOOL_DESCRIPTION (str): 工具的简短描述。
    - gradio_interface (function): 一个返回 Gradio Interface 或 Blocks 对象的函数。

    参数:
        tools_dir_path (str): 存放工具脚本的目录路径。

    返回:
        list: 包含加载工具信息的字典列表。
              每个字典包含 'id', 'name', 'description', 和 'interface_fn'。
    """
    loaded_tools = []
    if not os.path.isdir(tools_dir_path):
        print(f"错误：工具目录 '{tools_dir_path}' 不存在或不是一个目录。")
        return loaded_tools

    # 遍历目录及其子目录
    for root, dirs, files in os.walk(tools_dir_path):
        # 跳过 __pycache__ 目录
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')

        # 如果是顶级目录，跳过处理（我们只想处理子目录中的工具）
        if root == tools_dir_path:
            continue

        # 获取当前目录相对于tools目录的路径
        rel_path = os.path.relpath(root, tools_dir_path)
        dir_name = os.path.basename(root)
        
        # 构建模块名
        module_path_parts = rel_path.split(os.sep)
        module_name = 'tools.' + '.'.join(module_path_parts)

        # 首先尝试加载 __init__.py
        if '__init__.py' in files:
            file_path = os.path.join(root, '__init__.py')
            tool_name_from_file = dir_name
        # 然后尝试加载与目录同名的 .py 文件
        elif f"{dir_name}.py" in files:
            file_path = os.path.join(root, f"{dir_name}.py")
            tool_name_from_file = dir_name
        else:
            continue  # 如果两种文件都不存在，跳过此目录

        try:
            # 确保工具目录在 Python 路径中
            if root not in sys.path:
                sys.path.insert(0, root)

            # 动态导入模块
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None:
                print(f"警告：无法为 '{file_path}' 创建模块规范。跳过此工具。")
                continue
            
            module = importlib.util.module_from_spec(spec)
            
            # 将模块添加到 sys.modules
            if module_name not in sys.modules:
                sys.modules[module_name] = module 
            
            spec.loader.exec_module(module)

            # 获取工具元数据
            tool_display_name = getattr(module, 'TOOL_NAME', tool_name_from_file.replace('_', ' ').title())
            tool_description = getattr(module, 'TOOL_DESCRIPTION', '无描述。')
            interface_function = getattr(module, 'gradio_interface', None)

            if callable(interface_function):
                # 使用目录名作为唯一ID
                tool_id = dir_name.lower().replace('_', '-')
                loaded_tools.append({
                    'id': tool_id,
                    'name': tool_display_name,
                    'description': tool_description,
                    'interface_fn': interface_function,
                    'module_name': module_name, # 方便调试
                    'directory': root  # 保存工具目录路径
                })
                print(f"成功加载工具: '{tool_display_name}' (ID: {tool_id}) 来自 {os.path.relpath(file_path, tools_dir_path)}")
            else:
                print(f"警告：工具 '{file_path}' 未定义可调用的 'gradio_interface' 函数。跳过此工具。")

        except ImportError as e:
            print(f"导入错误：加载工具 '{file_path}' 失败: {e}。请检查工具脚本及其依赖。")
        except AttributeError as e:
            print(f"属性错误：加载工具 '{file_path}' 失败: {e}。确保定义了必要的变量/函数。")
        except Exception as e:
            print(f"未知错误：加载工具 '{file_path}' 失败: {e}")
    
    return loaded_tools

if __name__ == '__main__':
    # 用于测试 tool_loader.py
    # 假设 Mytools 是项目根目录，并且此脚本在 utils 子目录中
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tools_test_dir = os.path.join(project_root, "tools")

    # 确保测试时 tools 目录在 sys.path 中，以便模块导入
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 创建一个示例工具用于测试
    if not os.path.exists(tools_test_dir):
        os.makedirs(tools_test_dir)
    
    example_tool_content = """
import gradio as gr

TOOL_NAME = "示例测试工具"
TOOL_DESCRIPTION = "这是一个用于测试工具加载器的示例工具。"

def gradio_interface():
    def greet(name):
        return f"你好, {name}!"
    
    return gr.Interface(fn=greet, inputs="text", outputs="text", title=TOOL_NAME, description=TOOL_DESCRIPTION)

"""
    with open(os.path.join(tools_test_dir, "example_test_tool.py"), "w", encoding="utf-8") as f:
        f.write(example_tool_content)
    
    print(f"正在从 '{tools_test_dir}' 加载工具...")
    tools = load_tools(tools_test_dir)
    
    if tools:
        print("\n成功加载的工具:")
        for tool in tools:
            print(f"  - 名称: {tool['name']}")
            print(f"    描述: {tool['description']}")
            print(f"    ID: {tool['id']}")
            print(f"    模块: {tool['module_name']}")
            # 尝试调用接口函数 (仅用于测试，实际应用中由 main.py 处理)
            try:
                iface = tool['interface_fn']()
                if isinstance(iface, (gr.Interface, gr.Blocks)):
                    print(f"    接口函数调用成功，返回类型: {type(iface)}")
                else:
                    print(f"    警告: 接口函数未返回 Gradio Interface 或 Blocks 对象，返回类型: {type(iface)}")
            except Exception as e:
                print(f"    错误: 调用接口函数失败: {e}")
    else:
        print("没有加载任何工具。")

    # 清理示例工具
    # os.remove(os.path.join(tools_test_dir, "example_test_tool.py"))
    # if not os.listdir(tools_test_dir):
    #     os.rmdir(tools_test_dir)
    print("\n测试完成。如果需要，请手动清理 example_test_tool.py。")

"""
说明:
1.  `load_tools(tools_dir_path)` 函数:
    *   遍历 `tools_dir_path` 目录下的所有 `.py` 文件。
    *   动态导入每个 Python 文件作为一个模块。
    *   从模块中提取 `TOOL_NAME`, `TOOL_DESCRIPTION`, 和 `gradio_interface`。
    *   如果 `gradio_interface` 是一个可调用函数，则将工具信息（包括函数本身）添加到一个列表中。
    *   包含错误处理，以防工具脚本格式不正确或导入失败。
2.  `if __name__ == '__main__':` 部分:
    *   提供了一个简单的测试脚本，当直接运行 `tool_loader.py` 时执行。
    *   它会尝试在 `../tools` (相对于 `utils` 目录) 创建一个示例工具文件 `example_test_tool.py`。
    *   然后调用 `load_tools` 加载该目录下的工具，并打印加载结果。
    *   这有助于独立测试工具加载逻辑。

使用方法:
在 `main.py` 中，你可以像这样使用 `load_tools`:

```python
# main.py
import os
from utils import tool_loader # 假设 utils 是一个包或者在 sys.path 中

TOOLS_DIR = os.path.join(os.path.dirname(__file__), "tools")

def get_tools():
    if not os.path.exists(TOOLS_DIR):
        os.makedirs(TOOLS_DIR)
    return tool_loader.load_tools(TOOLS_DIR)

# ... 后续逻辑使用 get_tools() 获取工具列表 ...
```

确保 `utils` 目录和 `tools` 目录与 `main.py` 在同一级别，或者相应地调整路径。
如果 `utils` 不是一个包 (即没有 `__init__.py` 文件)，你可能需要调整 `main.py` 中的导入语句，或者将 `utils` 目录添加到 `sys.path`。
当前 `main.py` 的设计已经考虑了将 `utils` 加入 `sys.path`。
"""