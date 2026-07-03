from .get_user_memory_summary import setup_get_user_memory_summary
from .log_learning_progress import setup_log_learning_progress
from .create_wiki_page import setup_create_wiki_page
from .read_wiki_page import setup_read_wiki_page
from .list_local_wiki_pages import setup_list_local_wiki_pages

def setup_local_tools(mcp, memory_path: str):
    setup_get_user_memory_summary(mcp, memory_path)
    setup_log_learning_progress(mcp, memory_path)
    setup_create_wiki_page(mcp, memory_path)
    setup_read_wiki_page(mcp, memory_path)
    setup_list_local_wiki_pages(mcp, memory_path)
