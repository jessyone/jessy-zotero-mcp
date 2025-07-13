import sys
import os
# 修复括号问题 - 确保所有括号正确闭合
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import patch, MagicMock
from zotero_mcp import server

@pytest.fixture
def mock_ctx():
    class Ctx:
        def info(self, msg):
            pass
        def error(self, msg):
            pass
    return Ctx()

@patch('zotero_mcp.server.get_zotero_client')
def test_add_item_by_doi_success(mock_get_client, mock_ctx):
    # 模拟 pyzotero 行为
    mock_zot = MagicMock()
    mock_item = {
        'title': 'Test Paper',
        'creators': [{'creatorType': 'author', 'firstName': 'Alice', 'lastName': 'Smith'}],
        'date': '2022',
        'DOI': '10.1234/testdoi'
    }
    mock_zot.item_from_doi.return_value = mock_item
    mock_zot.create_items.return_value = {'success': {'ABC123': mock_item}}
    mock_get_client.return_value = mock_zot

    # 正确的调用方式：直接调用原始实现函数
    result = server.add_item_by_doi_impl("10.1234/testdoi", ctx=mock_ctx)
    assert '成功' in result or 'Success' in result
    assert 'Test Paper' in result
    assert 'ABC123' in result

@patch('zotero_mcp.server.get_zotero_client')
def test_add_item_by_doi_invalid(mock_get_client, mock_ctx):
    mock_zot = MagicMock()
    mock_zot.item_from_doi.side_effect = Exception('DOI not found')
    mock_get_client.return_value = mock_zot

    # 正确的调用方式
    result = server.add_item_by_doi_impl("invalid-doi", ctx=mock_ctx)
    assert '错误' in result or 'Error' in result
    assert 'invalid-doi' in result

@patch('zotero_mcp.server.get_zotero_client')
def test_add_item_by_doi_duplicate(mock_get_client, mock_ctx):
    mock_zot = MagicMock()
    mock_item = {
        'title': 'Test Paper',
        'creators': [{'creatorType': 'author', 'firstName': 'Alice', 'lastName': 'Smith'}],
        'date': '2022',
        'DOI': '10.1234/testdoi'
    }
    # 假设 create_items 返回空，表示未添加（已存在）
    mock_zot.item_from_doi.return_value = mock_item
    mock_zot.create_items.return_value = {'success': {}}
    mock_get_client.return_value = mock_zot

    # 正确的调用方式
    result = server.add_item_by_doi_impl("10.1234/testdoi", ctx=mock_ctx)
    assert '未添加' in result or '已存在' in result or 'No new item' in result

@patch('zotero_mcp.server.get_zotero_client')
def test_add_item_by_doi_network_error(mock_get_client, mock_ctx):
    mock_zot = MagicMock()
    mock_zot.item_from_doi.side_effect = Exception('Network error')
    mock_get_client.return_value = mock_zot

    # 正确的调用方式
    result = server.add_item_by_doi_impl("10.5555/network", ctx=mock_ctx)
    assert '错误' in result or 'Error' in result
    assert 'Network error' in result