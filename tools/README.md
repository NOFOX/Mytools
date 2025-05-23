# Mytools 工具集

这是一个基于 Gradio 的工具集合，包含多个实用的小工具。

## 工具列表

### 1. Example Tool (示例工具)
位置：`example_tool/example_tool.py`
- 一个简单的示例工具，展示了基本的 Gradio 界面使用方法
- 支持基本的文本输入和输出功能

### 2. Case Converter (大小写转换器)
位置：`case_converter/case_converter.py`
- 提供文本大小写转换功能
- 支持将文本转换为大写、小写或首字母大写

### 3. Text Analyzer (文本分析器)
位置：`text_analyzer/text_analyzer.py`
- 分析文本的基本统计信息
- 功能包括：
  - 统计字数（支持中英文混合）
  - 统计句子数
  - 统计段落数
  - 计算平均句子长度
  - 评估文本可读性

## 安装和使用

每个工具都是独立的，可以单独安装和运行。

### 安装依赖
进入对应工具目录，安装依赖：
```bash
cd [工具目录]
pip install -r requirements.txt
```

### 运行工具
在对应工具目录中运行 Python 文件：
```bash
python [工具名].py
```

例如，要运行文本分析器：
```bash
cd text_analyzer
pip install -r requirements.txt
python text_analyzer.py
```

运行后，工具会在本地启动一个 Gradio 服务器，通常可以通过浏览器访问 http://localhost:7860 来使用工具界面。

## 开发说明

每个工具都遵循相同的目录结构：
```
工具名/
├── 工具名.py      # 主程序文件
└── requirements.txt # 依赖文件
```

如果要添加新工具，请遵循这个结构，并确保：
1. 创建独立的工具目录
2. 包含必要的 requirements.txt 文件
3. 在主程序文件中提供清晰的文档注释
4. 使用 Gradio 创建直观的用户界面