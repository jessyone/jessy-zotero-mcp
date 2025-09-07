# Zotero MCP - Create Note 功能指南

这个文档提供了关于如何使用 Zotero MCP 中的 `zotero_create_note` 功能的详细指南。此功能允许您通过 Model Context Protocol (MCP) 为 Zotero 条目创建笔记。

## 功能概述

`zotero_create_note` 是一个强大的工具，它允许您以编程方式为任何 Zotero 条目添加笔记。这对于以下场景特别有用：

- 在阅读文献后通过 AI 助手自动生成笔记摘要
- 批量为多个条目添加标准化的研究笔记
- 与其他工作流工具集成，例如从知识管理系统自动同步笔记到 Zotero

## 前提条件

在使用此功能之前，请确保：

1. Zotero MCP 服务器已正确安装并运行
2. 您具有有效的 Zotero API 凭据（对于远程 API）或本地 Zotero 实例
3. 您已配置环境变量或配置文件

## 配置

在 `.env` 文件或环境变量中设置以下值：

```
ZOTERO_LIBRARY_ID=your_library_id
ZOTERO_API_KEY=your_api_key
ZOTERO_LIBRARY_TYPE=user  # 或者 group
```

对于本地 Zotero 实例，设置：

```
ZOTERO_LOCAL=true
```

## 参数说明

`zotero_create_note` 工具接受以下参数：

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| item_key | 字符串 | 是 | Zotero 条目的唯一标识符 |
| note_title | 字符串 | 是 | 笔记的标题 |
| note_text | 字符串 | 是 | 笔记的内容（可以包含简单的 HTML 格式） |
| tags | 字符串列表 | 否 | 要应用于笔记的标签列表 |

## 使用方法

### 通过 Python 客户端

下面是一个简单的 Python 示例，展示如何调用 `zotero_create_note` 工具：

```python
import requests
import os

# MCP 服务器 URL
MCP_SERVER_URL = "http://localhost:8000"  # 修改为您的服务器 URL

# 构建请求
payload = {
    "tool": "zotero_create_note",
    "arguments": {
        "item_key": "ABC123",  # 替换为实际的 Zotero 条目键
        "note_title": "我的研究笔记",
        "note_text": "<p>这是一个<b>格式化</b>的笔记。</p><p>它包含多个段落。</p>",
        "tags": ["重要", "研究", "AI"]
    }
}

# 发送请求
response = requests.post(
    f"{MCP_SERVER_URL}/tools",
    json=payload,
    headers={"Content-Type": "application/json"}
)

# 处理响应
result = response.json()
print(result)
```

### 通过 curl 命令行

您也可以使用 curl 来调用此功能：

```bash
curl -X POST http://localhost:8000/tools \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "zotero_create_note",
    "arguments": {
      "item_key": "ABC123",
      "note_title": "命令行创建的笔记",
      "note_text": "这是通过命令行创建的简单笔记。\n\n它也支持多段落。",
      "tags": ["命令行", "自动化"]
    }
  }'
```

## 笔记内容格式化

`note_text` 参数支持两种格式：

1. **纯文本格式**：系统会自动将换行符 (`\n\n`) 转换为 HTML 段落，将单个换行符 (`\n`) 转换为 `<br/>` 标签。

2. **HTML 格式**：您可以直接提供 HTML 格式的内容，例如：
   ```html
   <p>第一段文本 <b>粗体</b> 和 <i>斜体</i>.</p>
   <p>第二段文本，包含 <a href="https://example.com">链接</a>.</p>
   <ul>
     <li>列表项 1</li>
     <li>列表项 2</li>
   </ul>
   ```

## 响应格式

成功的响应将返回：

```json
{
  "result": "Successfully created note for \"文献标题\"\n\nNote key: DEF456"
}
```

其中 `DEF456` 是新创建的笔记的键，可用于后续操作。

## 错误处理

常见的错误情况包括：

1. 条目不存在：
   ```json
   {
     "result": "Error: No item found with key: INVALID_KEY"
   }
   ```

2. API 权限问题：
   ```json
   {
     "result": "Error creating note: Invalid API key"
   }
   ```

## 高级用例

### 1. 创建带有丰富格式的研究笔记

```python
note_text = """
<h1>文献笔记</h1>
<p><strong>关键发现：</strong> ...</p>
<h2>方法论总结</h2>
<p>本研究采用了以下方法：</p>
<ol>
  <li>数据收集：通过问卷调查获取...</li>
  <li>数据分析：使用SPSS进行因子分析...</li>
</ol>
<h2>批评性思考</h2>
<p>该研究的局限性包括：</p>
<ul>
  <li>样本量较小</li>
  <li>未考虑文化差异因素</li>
</ul>
"""
```

### 2. 从其他工作流程中批量创建笔记

```python
import json

# 假设我们有一个包含多个文献笔记的 JSON 文件
with open('my_notes.json', 'r') as f:
    notes_data = json.load(f)

for note in notes_data:
    payload = {
        "tool": "zotero_create_note",
        "arguments": {
            "item_key": note["zotero_key"],
            "note_title": note["title"],
            "note_text": note["content"],
            "tags": note.get("tags", [])
        }
    }
    
    # 发送请求...
```

## 最佳实践

1. **验证条目存在性**：在创建笔记之前，使用 `zotero_get_item_metadata` 工具检查条目是否存在。

2. **注意笔记大小**：过大的笔记可能导致性能问题。将长文本拆分为多个笔记。

3. **合理使用标签**：标签可以帮助组织和检索笔记，但不要过度使用。

4. **错误处理**：始终包含适当的错误处理机制，以应对网络问题或 API 限制。

## 故障排除

1. **找不到条目**：确保使用正确的条目键，并且该条目在您有权访问的库中。

2. **权限问题**：确保 API 密钥具有正确的权限（读写权限）。

3. **HTML 格式问题**：如果笔记格式不正确，检查 HTML 是否有效。Zotero 支持有限的 HTML 子集。

4. **服务器连接问题**：确保 MCP 服务器正在运行，并且您可以访问它。

## 后续开发计划

未来的功能增强可能包括：

1. 支持文件附件上传到笔记
2. 改进的富文本格式支持
3. 笔记模板功能

## 参考资料

- [Zotero API 文档](https://www.zotero.org/support/dev/web_api/v3/basics)
- [Model Context Protocol (MCP) 规范](https://github.com/vpa1977/mcp)
- [Zotero 笔记语法](https://www.zotero.org/support/notes) 