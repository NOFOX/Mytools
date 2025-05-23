import gradio as gr
import re

# 工具元数据
TOOL_NAME = "文本分析器"
TOOL_DESCRIPTION = "分析文本的字数、句子数和段落数，并提供基本的可读性统计。"

def count_words(text):
    """计算文本中的单词数量"""
    # 对于中英文混合文本，我们需要特殊处理
    # 1. 将中文字符视为单词
    # 2. 英文单词按空格分割
    
    # 移除所有标点符号
    text_no_punct = re.sub(r'[^\w\s]', '', text)
    
    # 分割英文单词
    words = text_no_punct.split()
    
    # 计算中文字符
    chinese_chars = sum(1 for char in text_no_punct if '\u4e00' <= char <= '\u9fff')
    
    # 总词数 = 英文单词 + 中文字符
    return len(words) + chinese_chars

def count_sentences(text):
    """计算文本中的句子数量"""
    # 使用正则表达式匹配句子结束标记
    sentences = re.split(r'[.!?。！？]+', text)
    # 过滤掉空句子
    sentences = [s for s in sentences if s.strip()]
    return len(sentences)

def count_paragraphs(text):
    """计算文本中的段落数量"""
    # 按照连续的换行符分割段落
    paragraphs = re.split(r'\n\s*\n', text)
    # 过滤掉空段落
    paragraphs = [p for p in paragraphs if p.strip()]
    return len(paragraphs)

def calculate_readability(text):
    """计算文本的可读性指标"""
    word_count = count_words(text)
    sentence_count = max(1, count_sentences(text))  # 避免除以零
    
    # 平均句子长度（词/句）
    avg_sentence_length = word_count / sentence_count
    
    # 简单的可读性评分（基于平均句子长度）
    if avg_sentence_length < 10:
        readability = "非常容易"
    elif avg_sentence_length < 15:
        readability = "容易"
    elif avg_sentence_length < 20:
        readability = "中等"
    elif avg_sentence_length < 25:
        readability = "困难"
    else:
        readability = "非常困难"
    
    return {
        "平均句子长度": f"{avg_sentence_length:.1f} 词/句",
        "可读性评级": readability
    }

def analyze_text(text):
    """分析文本并返回统计结果"""
    if not text.strip():
        return (
            0,
            0,
            0,
            "N/A",
            "N/A"
        )
    
    word_count = count_words(text)
    sentence_count = count_sentences(text)
    paragraph_count = count_paragraphs(text)
    readability_metrics = calculate_readability(text)
    
    return (
        word_count,
        sentence_count,
        paragraph_count,
        readability_metrics["平均句子长度"],
        readability_metrics["可读性评级"]
    )

def gradio_interface():
    """创建Gradio界面"""
    with gr.Blocks() as demo:
        gr.Markdown(f"# {TOOL_NAME}")
        gr.Markdown(TOOL_DESCRIPTION)
        
        with gr.Row():
            with gr.Column(scale=3):
                text_input = gr.Textbox(
                    label="输入文本",
                    placeholder="在此输入要分析的文本...",
                    lines=10
                )
            
            with gr.Column(scale=2):
                word_count = gr.Number(label="字数")
                sentence_count = gr.Number(label="句子数")
                paragraph_count = gr.Number(label="段落数")
                avg_sentence_length = gr.Textbox(label="平均句子长度")
                readability = gr.Textbox(label="可读性评级")
        
        analyze_btn = gr.Button("分析文本", variant="primary")
        analyze_btn.click(
            fn=analyze_text,
            inputs=[text_input],
            outputs=[word_count, sentence_count, paragraph_count, avg_sentence_length, readability]
        )
        
        # 添加示例
        gr.Examples(
            [
                ["这是一个简单的句子。这是第二个句子！这是第三个句子吗？是的。\n\n这是新的一段。这段包含了两个句子。"],
                ["The quick brown fox jumps over the lazy dog. This is a simple English sentence. How are you today?\n\nThis is a new paragraph. It contains multiple sentences. Isn't that interesting?"],
                ["这是一个中英文混合的例子。This is a mixed Chinese and English example.\n\n第二段落 Second paragraph.\n\n第三段落 Third paragraph."]
            ],
            inputs=[text_input]
        )
    
    return demo

# 用于测试
if __name__ == "__main__":
    demo = gradio_interface()
    demo.launch()