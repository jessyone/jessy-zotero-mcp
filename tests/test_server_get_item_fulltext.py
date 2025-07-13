import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from unittest.mock import patch, MagicMock
from zotero_mcp.server import _get_item_fulltext_impl

@pytest.fixture
def mock_ctx():
    class Ctx:
        def info(self, msg):
            pass
        def error(self, msg):
            pass
    return Ctx()

@patch('zotero_mcp.server.get_zotero_client')
@patch('zotero_mcp.server.get_attachment_details')
@patch('zotero_mcp.server.format_item_metadata')
def test_get_item_fulltext_indexed_fulltext(mock_format, mock_get_attachment, mock_get_client, mock_ctx):
    mock_zot = MagicMock()
    mock_item = {'key': 'ITEM123'}
    mock_attachment = MagicMock()
    mock_attachment.key = 'ATTACH123'
    mock_attachment.content_type = 'application/pdf'
    mock_format.return_value = '元数据内容'
    mock_get_attachment.return_value = mock_attachment
    mock_zot.item.return_value = mock_item
    mock_zot.fulltext_item.return_value = {'content': '全文内容'}
    mock_get_client.return_value = mock_zot

    result = _get_item_fulltext_impl('ITEM123', ctx=mock_ctx)
    assert '元数据内容' in result
    assert '全文内容' in result
    assert 'Full Text' in result

@patch('zotero_mcp.server.get_zotero_client')
@patch('zotero_mcp.server.get_attachment_details')
@patch('zotero_mcp.server.format_item_metadata')
@patch('zotero_mcp.server.convert_to_markdown')
def test_get_item_fulltext_download_and_convert(mock_convert, mock_format, mock_get_attachment, mock_get_client, mock_ctx):
    mock_zot = MagicMock()
    mock_item = {'key': 'ITEM123'}
    mock_attachment = MagicMock()
    mock_attachment.key = 'ATTACH123'
    mock_attachment.content_type = 'application/pdf'
    mock_attachment.filename = 'file.pdf'
    mock_format.return_value = '元数据内容'
    mock_get_attachment.return_value = mock_attachment
    mock_zot.item.return_value = mock_item
    mock_zot.fulltext_item.side_effect = Exception('no index')
    mock_get_client.return_value = mock_zot
    mock_convert.return_value = '转换后的全文'

    # mock dump 和 os.path.exists
    with patch('os.path.exists', return_value=True), \
         patch('tempfile.TemporaryDirectory') as mock_tmpdir:
        mock_tmp = MagicMock()
        mock_tmp.__enter__.return_value = '/tmpdir'
        mock_tmpdir.return_value = mock_tmp
        mock_zot.dump.return_value = None
        result = _get_item_fulltext_impl('ITEM123', ctx=mock_ctx)
        assert '元数据内容' in result
        assert '转换后的全文' in result
        assert 'Full Text' in result

@patch('zotero_mcp.server.get_zotero_client')
@patch('zotero_mcp.server.get_attachment_details')
@patch('zotero_mcp.server.format_item_metadata')
def test_get_item_fulltext_no_attachment(mock_format, mock_get_attachment, mock_get_client, mock_ctx):
    mock_zot = MagicMock()
    mock_item = {'key': 'ITEM123'}
    mock_format.return_value = '元数据内容'
    mock_get_attachment.return_value = None
    mock_zot.item.return_value = mock_item
    mock_get_client.return_value = mock_zot

    result = _get_item_fulltext_impl('ITEM123', ctx=mock_ctx)
    assert 'No suitable attachment' in result
    assert '元数据内容' in result

@patch('zotero_mcp.server.get_zotero_client')
@patch('zotero_mcp.server.format_item_metadata')
def test_get_item_fulltext_no_item(mock_format, mock_get_client, mock_ctx):
    mock_zot = MagicMock()
    mock_zot.item.return_value = None
    mock_get_client.return_value = mock_zot
    mock_format.return_value = '元数据内容'

    result = _get_item_fulltext_impl('NOTFOUND', ctx=mock_ctx)
    assert 'No item found' in result

@patch('zotero_mcp.server.get_zotero_client')
@patch('zotero_mcp.server.get_attachment_details')
@patch('zotero_mcp.server.format_item_metadata')
def test_get_item_fulltext_download_fail(mock_format, mock_get_attachment, mock_get_client, mock_ctx):
    mock_zot = MagicMock()
    mock_item = {'key': 'ITEM123'}
    mock_attachment = MagicMock()
    mock_attachment.key = 'ATTACH123'
    mock_attachment.content_type = 'application/pdf'
    mock_attachment.filename = 'file.pdf'
    mock_format.return_value = '元数据内容'
    mock_get_attachment.return_value = mock_attachment
    mock_zot.item.return_value = mock_item
    mock_zot.fulltext_item.side_effect = Exception('no index')
    mock_get_client.return_value = mock_zot

    # mock dump 和 os.path.exists
    with patch('os.path.exists', return_value=False), \
         patch('tempfile.TemporaryDirectory') as mock_tmpdir:
        mock_tmp = MagicMock()
        mock_tmp.__enter__.return_value = '/tmpdir'
        mock_tmpdir.return_value = mock_tmp
        mock_zot.dump.return_value = None
        result = _get_item_fulltext_impl('ITEM123', ctx=mock_ctx)
        assert 'File download failed' in result or 'Error accessing attachment' in result 