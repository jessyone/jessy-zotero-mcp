#!/usr/bin/env python3
"""
示例脚本：演示如何使用 zotero_create_note 功能

此脚本展示如何使用 MCP 协议调用 zotero_create_note 工具，
为 Zotero 中的条目创建一条笔记。
"""

import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量（如果有的话）
load_dotenv()

# 配置 Zotero API 凭据
# 如果没有从 .env 加载，您需要在这里设置这些值
ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID")
ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY")
ZOTERO_LIBRARY_TYPE = os.getenv("ZOTERO_LIBRARY_TYPE", "user")

# MCP 服务器配置
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

def call_create_note(item_key, note_title, note_text, tags=None):
    """
    调用 zotero_create_note 工具创建一条笔记
    
    Args:
        item_key: Zotero 条目的键
        note_title: 笔记标题
        note_text: 笔记内容
        tags: 可选的标签列表
    
    Returns:
        API 响应
    """
    # 构建请求主体
    request_body = {
        "tool": "zotero_create_note",
        "arguments": {
            "item_key": item_key,
            "note_title": note_title,
            "note_text": note_text
        }
    }
    
    # 如果提供了标签，则添加到参数中
    if tags:
        request_body["arguments"]["tags"] = tags
    
    # 发送请求到 MCP 服务器
    response = requests.post(
        f"{MCP_SERVER_URL}/tools",
        json=request_body,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    )
    
    return response.json()

def main():
    """主函数，演示如何使用 zotero_create_note"""
    # 检查必要的环境变量
    if not ZOTERO_LIBRARY_ID or not ZOTERO_API_KEY:
        print("错误: 请设置 ZOTERO_LIBRARY_ID 和 ZOTERO_API_KEY 环境变量")
        print("您可以在 .env 文件中设置这些变量，或者直接在脚本中设置")
        return
    
    # 在此处替换为您实际的 Zotero 条目键
    item_key = "YOUR_ZOTERO_ITEM_KEY"
    
    # 创建笔记
    note_title = "使用 MCP 创建的测试笔记"
    note_text = """这是一个测试笔记，使用 Model Context Protocol (MCP) 创建。

MCP 允许 LLM 与外部工具和数据源无缝连接，例如 Zotero 数据库。

此笔记演示了如何使用 zotero_create_note 工具为 Zotero 条目添加笔记。"""
    
    tags = ["MCP", "测试", "自动化"]
    
    print(f"正在为条目 {item_key} 创建笔记...")
    try:
        result = call_create_note(item_key, note_title, note_text, tags)
        print("API 响应:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if "result" in result:
            print("\n成功创建笔记！")
            print(result["result"])
    except Exception as e:
        print(f"错误: {e}")
        print("请确保 MCP 服务器正在运行，并且可以在 http://localhost:8000 访问")

if __name__ == "__main__":
    main() 