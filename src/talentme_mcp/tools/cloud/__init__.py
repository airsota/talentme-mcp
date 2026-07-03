from .read_cloud_document import setup_read_cloud_document

def setup_cloud_tools(mcp, api_url: str, license_key: str, email: str = None):
    setup_read_cloud_document(mcp, api_url, license_key, email)
