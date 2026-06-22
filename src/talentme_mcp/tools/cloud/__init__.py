from .cloud_knowledge_query import setup_cloud_knowledge_query
from .read_cloud_document import setup_read_cloud_document

def setup_cloud_tools(mcp, api_url: str, license_key: str):
    setup_cloud_knowledge_query(mcp, api_url, license_key)
    setup_read_cloud_document(mcp, api_url, license_key)
