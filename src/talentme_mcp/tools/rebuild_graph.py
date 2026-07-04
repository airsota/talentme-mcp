import os
import re
import time
from mcp.server.fastmcp import FastMCP

MARKDOWN_TOKENS_RE = re.compile(
    r'(?P<frontmatter>^\s*---.*?---\s*$)'
    r'|(?P<codeblock>```.*?```)'
    r'|(?P<inlinecode>`[^`\n]+`)'
    r'|(?P<wikilink>\[\[.*?\]\])'
    r'|(?P<stdlink>\[.*?\]\(.*?\))'
    r'|(?P<header>^#+ .*?$)',
    flags=re.DOTALL | re.MULTILINE
)

def clean_legacy_moc(text: str) -> str:
    text = re.sub(r'\[\[(.*?)_MOC\]\]', r'[[\1]]', text, flags=re.IGNORECASE)
    text = re.sub(r'theory_link:\s*\[\[(.*?)_MOC\]\]', r'theory_link: [[\1]]', text, flags=re.IGNORECASE)
    return text

def extract_metadata(filepath: str):
    title = ""
    description = ""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    yaml_match = re.search(r'^---.*?title:\s*(.*?)\n.*?---', content, re.DOTALL | re.MULTILINE)
    if yaml_match:
        title = yaml_match.group(1).strip().strip('"').strip("'")
    else:
        h1_match = re.search(r'^#\s+(.*?)$', content, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
            
    title = re.sub(r'^\d+\.\s*', '', title)
    title = re.sub(r'[^\w\s\-\(\)]', '', title).strip()
            
    no_fm = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
    no_hd = re.sub(r'^#+ .*?\n', '', no_fm, flags=re.MULTILINE)
    
    lines = no_hd.split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('<') and not line.startswith('!') and not line.startswith('-') and not line.startswith('```') and not line.startswith('|'):
            description = line
            break
            
    if not description:
        description = "Core concept and implementation details."
    if len(description) > 200:
        description = description[:197] + "..."
        
    return title, description, content

def setup_rebuild_graph_tool(mcp: FastMCP, memory_path: str = None):
    @mcp.tool()
    def rebuild_wiki_graph(target_dir: str = None) -> str:
        """
        Rebuild the Knowledge Base graph. Cleans legacy formats, generates a global glossary.md,
        injects safe semantic wikilinks across all markdown files via AST parsing, and auto-appends 
        Cross-References.
        
        Args:
            target_dir: The directory to rebuild. If not provided, uses the default memory vault.
        """
        target = target_dir if target_dir else memory_path
        if not target or not os.path.isdir(target):
            return f"Error: Invalid or unconfigured target directory: {target}"
            
        start_time = time.time()
        term_to_info = {}
        file_to_path = {}
        
        excludes = ['_index.md', '_global_index.md', 'glossary.md', 'CHANGELOG.md', 'README.md', 'DEVLOG.md', 'master_index.md', 'top_10_ml_questions.md', 'system_design_cheat_sheet.md']
        
        # 1. Build Dictionary
        for dirpath, dirnames, filenames in os.walk(target):
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            if '_dev' in dirnames:
                dirnames.remove('_dev')
                
            for f in filenames:
                if f.endswith('.md') and f not in excludes:
                    filepath = os.path.join(dirpath, f)
                    file_base = f[:-3]
                    title, desc, content = extract_metadata(filepath)
                    
                    if len(title) > 3:
                        term_to_info[title.lower()] = {'file': file_base, 'desc': desc, 'original': title}
                    
                    filename_clean = file_base.replace('_', ' ')
                    if len(filename_clean) > 3 and filename_clean.lower() != title.lower():
                        term_to_info[filename_clean.lower()] = {'file': file_base, 'desc': desc, 'original': filename_clean}
                        
                    file_to_path[filepath] = content

        if not term_to_info:
            return "No markdown files found to build graph."

        # 2. Super Linking
        sorted_terms = sorted(list(term_to_info.keys()), key=len, reverse=True)
        escaped_terms = [re.escape(t) for t in sorted_terms]
        super_pattern = re.compile(r'\b(' + '|'.join(escaped_terms) + r')\b', flags=re.IGNORECASE)
        
        modified_files = 0
        total_links = 0
        
        for filepath, original_content in file_to_path.items():
            content = clean_legacy_moc(original_content)
            chunks = []
            last_end = 0
            file_matched_targets = set()
            
            def repl(match):
                term = match.group(1)
                lower_term = term.lower()
                if lower_term in term_to_info:
                    tgt = term_to_info[lower_term]['file']
                    file_matched_targets.add(tgt)
                    return f"[[{tgt}|{term}]]"
                return term
            
            for match in MARKDOWN_TOKENS_RE.finditer(content):
                start, end = match.span()
                plain_text = content[last_end:start]
                replaced_text = super_pattern.sub(repl, plain_text)
                chunks.append(replaced_text)
                chunks.append(match.group(0))
                last_end = end
                
                if match.group('wikilink'):
                    wl = match.group('wikilink')
                    inner = wl[2:-2]
                    tgt = inner.split('|')[0].strip()
                    file_matched_targets.add(tgt)
                
            tail = content[last_end:]
            replaced_tail = super_pattern.sub(repl, tail)
            chunks.append(replaced_tail)
            
            new_content = "".join(chunks)
            
            file_base = os.path.basename(filepath)[:-3]
            file_matched_targets.discard(file_base)
            
            if file_matched_targets and "## 🔗 Cross-References" not in new_content:
                new_content += "\n\n---\n\n## 🔗 Cross-References\n"
                new_content += "- ⬅️ **Prerequisites**: *(Auto-extracted from document)*\n"
                for tgt in sorted(list(file_matched_targets)):
                    new_content += f"  - [[{tgt}]]\n"
                new_content += "- ↔️ **Comparisons**: *(To be filled)*\n"
                new_content += "- ➡️ **Next Steps / Advanced**: *(To be filled)*\n"
                
            if new_content != original_content:
                modified_files += 1
                total_links += len(file_matched_targets)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                    
        # 3. Write Glossary
        glossary_lines = [
            "# Global Knowledge Glossary\n",
            "A master index of all core concepts in the knowledge base, formatted for rapid interview preparation and quick recall.\n"
        ]
        
        glossary_dict = {}
        for term, info in term_to_info.items():
            tgt = info['file']
            glossary_dict[tgt] = info
            
        sorted_targets = sorted(glossary_dict.keys(), key=lambda x: x.lower())
        
        current_letter = ""
        for tgt in sorted_targets:
            info = glossary_dict[tgt]
            first_char = tgt[0].upper()
            if not first_char.isalpha():
                first_char = "#"
                
            if first_char != current_letter:
                current_letter = first_char
                glossary_lines.append(f"## {current_letter}\n")
                
            display_term = tgt.replace('_', ' ')
            glossary_lines.append(f"- **{display_term}**")
            glossary_lines.append(f"  - **Q: What is it?** {info['desc']}")
            glossary_lines.append(f"  - **Link**: [[{tgt}]]\n")
            
        with open(os.path.join(target, "glossary.md"), 'w', encoding='utf-8') as f:
            f.write("\n".join(glossary_lines))
            
        duration = time.time() - start_time
        return f"""
[REBUILD WIKI GRAPH SUCCESS]
Processed Target Directory: {target}
Execution Time: {duration:.2f} seconds
Extracted Concepts: {len(term_to_info)}
Modified Files (Links/MOC/References updated): {modified_files}
Total Cross-References Mapped: {total_links}
Global Glossary Generated: glossary.md
"""
