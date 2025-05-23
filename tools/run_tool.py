import os
import sys
import subprocess
import importlib.util

def clear_screen():
    """清除终端屏幕"""
    os.system('cls' if os.name == 'nt' else 'clear')

def find_tools():
    """查找所有可用的工具"""
    tools = []
    
    # 遍历tools目录下的所有子目录
    for item in os.listdir('.'):
        if os.path.isdir(item) and not item.startswith('__'):
            # 检查是否有与目录同名的Python文件
            tool_file = os.path.join(item, f"{item}.py")
            if os.path.isfile(tool_file):
                # 尝试导入模块以获取元数据
                try:
                    spec = importlib.util.spec_from_file_location(item, tool_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 获取工具名称和描述
                    name = getattr(module, "TOOL_NAME", item)
                    description = getattr(module, "TOOL_DESCRIPTION", "无描述")
                    
                    tools.append({
                        "id": item,
                        "name": name,
                        "description": description,
                        "path": tool_file
                    })
                except Exception as e:
                    # 如果无法导入，使用默认值
                    tools.append({
                        "id": item,
                        "name": item,
                        "description": f"无法加载描述: {str(e)}",
                        "path": tool_file
                    })
    
    return tools

def install_requirements(tool_dir):
    """安装工具的依赖"""
    req_file = os.path.join(tool_dir, "requirements.txt")
    if os.path.isfile(req_file):
        print(f"正在安装依赖...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file])
        print(f"依赖安装完成！")
    else:
        print(f"未找到依赖文件: {req_file}")

def run_tool(tool_path):
    """运行指定的工具"""
    tool_dir = os.path.dirname(tool_path)
    
    # 安装依赖
    install_requirements(tool_dir)
    
    # 运行工具
    print(f"正在启动工具: {tool_path}")
    subprocess.run([sys.executable, tool_path])

def show_menu(tools):
    """显示工具选择菜单"""
    clear_screen()
    print("=" * 50)
    print("                工具启动器")
    print("=" * 50)
    print("\n可用工具列表:\n")
    
    for i, tool in enumerate(tools, 1):
        print(f"{i}. {tool['name']}")
        print(f"   {tool['description']}")
        print()
    
    print("0. 退出程序")
    print("\n" + "=" * 50)

def main():
    """主函数"""
    # 确保当前目录是tools目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # 查找所有工具
    tools = find_tools()
    
    if not tools:
        print("未找到任何工具！")
        return
    
    while True:
        show_menu(tools)
        
        try:
            choice = input("\n请选择要启动的工具 (输入编号): ")
            if choice == "0":
                print("感谢使用，再见！")
                break
            
            choice = int(choice)
            if 1 <= choice <= len(tools):
                selected_tool = tools[choice - 1]
                run_tool(selected_tool["path"])
            else:
                print(f"无效的选择，请输入0-{len(tools)}之间的数字")
                input("按Enter键继续...")
        except ValueError:
            print("请输入有效的数字")
            input("按Enter键继续...")
        except KeyboardInterrupt:
            print("\n程序已被用户中断")
            break
        except Exception as e:
            print(f"发生错误: {str(e)}")
            input("按Enter键继续...")

if __name__ == "__main__":
    main()