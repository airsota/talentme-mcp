# `rebuild_wiki_graph` Tool

## Description
The `rebuild_wiki_graph` tool is a high-performance backend utility designed to automatically restructure and cross-link the TalentMe Knowledge Base graph. It runs a highly optimized Python AST parser to update references safely across thousands of Markdown files without breaking code blocks, YAML frontmatter, or existing links.

## Usage
Agents should invoke this tool whenever a major batch of new content (e.g., raw interview notes, new ML topics) has been imported into the vault, or when the user requests a "wiki rebuild", "link sync", or "graph update".

### Parameters
- `target_dir` (Optional, string): The absolute path to the directory to rebuild. If not provided, it defaults to the configured `memory_path` of the MCP Server.

## Internal Mechanisms
1. **O(1) Super Regex Engine**: Instead of looping through thousands of files and regex matching individually, it compiles all known titles in the vault into a single Regex State Machine (`re.compile(r'\b(term1|term2|...)\b')`).
2. **AST Markdown Tokenization**: Ignores `YAML frontmatter`, code blocks (` ``` `), and inline code (`` ` ``). It safely injects wikilinks only in plain text.
3. **MOC Cleanup**: Automatically translates legacy `[[Topic_MOC]]` links into modern `[[Topic]]` format.
4. **Auto Cross-References**: Injects `## 🔗 Cross-References` at the bottom of markdown files containing auto-extracted Prerequisites based on the wikilinks present in the file.
5. **Glossary Generation**: Aggregates all definitions into a master `glossary.md` in Q&A format for interview prep.

## Example Call
```json
{
  "name": "rebuild_wiki_graph",
  "arguments": {
    "target_dir": "/home/suiyaoc/TalentMe/cloud/memory/ML/latest"
  }
}
```
