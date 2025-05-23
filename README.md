# Mytools 工具集合

这是一个基于 Python 和 Gradio 开发的实用工具集合，提供了多个独立的工具应用，可以帮助用户完成各种常见任务。

## 功能特点

- 📦 **模块化设计**：每个工具都是独立的，可以单独安装和使用
- 🎯 **简单易用**：所有工具都提供了直观的 Web 界面
- 🔧 **易于扩展**：标准化的目录结构，方便添加新工具
- 🚀 **一键启动**：统一的启动器，轻松选择和运行工具

## 目录结构

```
Mytools/
├── README.md           # 项目主文档
└── tools/             # 工具目录
    ├── README.md      # 工具集使用说明
    ├── run_tool.py    # 工具启动器
    ├── example_tool/  # 示例工具
    ├── case_converter/# 大小写转换工具
    └── text_analyzer/ # 文本分析工具
```

## 快速开始

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd Mytools
   ```

2. **运行工具启动器**
   ```bash
   cd tools
   python run_tool.py
   ```

3. **选择工具**
   - 在启动器菜单中输入工具对应的编号
   - 工具会自动安装所需依赖并启动

## 可用工具

1. **Example Tool (示例工具)**
   - 基本的 Gradio 界面示例
   - 演示了工具开发的基本结构

2. **Case Converter (大小写转换器)**
   - 文本大小写转换功能
   - 支持转换为大写、小写或首字母大写

3. **Text Analyzer (文本分析器)**
   - 文本统计和分析功能
   - 支持中英文混合文本
   - 提供字数、句子数、段落数统计
   - 计算文本可读性指标

## 系统要求

- Python 3.7 或更高版本
- pip 包管理器
- 网络连接（用于安装依赖）

## 开发指南

如果您想添加新工具，请遵循以下步骤：

1. 在 `tools` 目录下创建新的工具目录
   ```bash
   cd tools
   mkdir my_new_tool
   ```

2. 创建工具主文件和依赖文件
   ```
   my_new_tool/
   ├── my_new_tool.py      # 主程序文件
   └── requirements.txt     # 依赖文件
   ```

3. 在工具主文件中定义必要的元数据
   ```python
   TOOL_NAME = "工具名称"
   TOOL_DESCRIPTION = "工具描述"
   ```

4. 使用 Gradio 创建工具界面
   ```python
   def gradio_interface():
       # 创建 Gradio 界面
       pass

   if __name__ == "__main__":
       demo = gradio_interface()
       demo.launch()
   ```

## 贡献指南

欢迎贡献新的工具或改进现有工具！请确保：

1. 遵循项目的目录结构和编码规范
2. 为新工具提供完整的文档
3. 添加适当的错误处理和用户提示
4. 测试工具在不同环境下的运行情况

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送 Pull Request
- 发送邮件至 [your-email@example.com]

感谢使用 Mytools！