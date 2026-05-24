import os
import re
import json
from pathlib import Path


class MarkdownTools:
    """Tools for Markdown processing, conversion, and manipulation"""
    
    def __init__(self):
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.image_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
        self.code_block_pattern = re.compile(r'```(\w*)\n(.*?)```', re.DOTALL)
        self.bold_pattern = re.compile(r'\*\*([^*]+)\*\*|__([^_]+)__')
        self.italic_pattern = re.compile(r'\*([^*]+)\*|_([^_]+)_')
        self.list_pattern = re.compile(r'^[\s]*[-*+]\s+(.+)$', re.MULTILINE)
        self.numbered_list_pattern = re.compile(r'^[\s]*\d+\.\s+(.+)$', re.MULTILINE)
    
    def read_markdown(self, file_path):
        """Reads a Markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_markdown(self, file_path, content):
        """Writes content to a Markdown file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    def extract_headings(self, markdown_text):
        """Extracts all headings with their levels"""
        headings = []
        for match in self.heading_pattern.finditer(markdown_text):
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append({
                'level': level,
                'title': title,
                'anchor': self._create_anchor(title)
            })
        return headings
    
    def _create_anchor(self, title):
        """Creates a URL anchor from a heading title"""
        anchor = title.lower()
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[\s_]+', '-', anchor)
        return anchor.strip('-')
    
    def extract_links(self, markdown_text):
        """Extracts all links from Markdown"""
        links = []
        for match in self.link_pattern.finditer(markdown_text):
            links.append({
                'text': match.group(1),
                'url': match.group(2)
            })
        return links
    
    def extract_images(self, markdown_text):
        """Extracts all images from Markdown"""
        images = []
        for match in self.image_pattern.finditer(markdown_text):
            images.append({
                'alt': match.group(1),
                'url': match.group(2)
            })
        return images
    
    def extract_code_blocks(self, markdown_text):
        """Extracts all code blocks with their languages"""
        code_blocks = []
        for match in self.code_block_pattern.finditer(markdown_text):
            code_blocks.append({
                'language': match.group(1) or 'text',
                'code': match.group(2).strip()
            })
        return code_blocks
    
    def extract_bold_text(self, markdown_text):
        """Extracts all bold text"""
        bold_texts = []
        for match in self.bold_pattern.finditer(markdown_text):
            bold_texts.append(match.group(1) or match.group(2))
        return bold_texts
    
    def extract_italic_text(self, markdown_text):
        """Extracts all italic text"""
        italic_texts = []
        for match in self.italic_pattern.finditer(markdown_text):
            italic_texts.append(match.group(1) or match.group(2))
        return italic_texts
    
    def extract_lists(self, markdown_text):
        """Extracts all list items"""
        unordered = [match.group(1) for match in self.list_pattern.finditer(markdown_text)]
        ordered = [match.group(1) for match in self.numbered_list_pattern.finditer(markdown_text)]
        return {
            'unordered': unordered,
            'ordered': ordered
        }
    
    def table_of_contents(self, markdown_text):
        """Generates a table of contents from headings"""
        headings = self.extract_headings(markdown_text)
        toc_lines = []
        for heading in headings:
            indent = '  ' * (heading['level'] - 1)
            toc_lines.append(f"{indent}- [{heading['title']}](#{heading['anchor']})")
        return '\n'.join(toc_lines)
    
    def markdown_to_html(self, markdown_text):
        """Converts Markdown to HTML"""
        import markdown
        return markdown.markdown(markdown_text, extensions=['tables', 'fenced_code', 'toc'])
    
    def markdown_to_plain_text(self, markdown_text):
        """Converts Markdown to plain text"""
        text = markdown_text
        text = self.code_block_pattern.sub(r'\2', text)
        text = self.link_pattern.sub(r'\1', text)
        text = self.image_pattern.sub(r'\1', text)
        text = self.bold_pattern.sub(r'\1\2', text)
        text = self.italic_pattern.sub(r'\1\2', text)
        text = self.heading_pattern.sub(r'\2', text)
        text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()
    
    def markdown_to_json(self, markdown_text):
        """Converts Markdown structure to JSON"""
        return {
            'headings': self.extract_headings(markdown_text),
            'links': self.extract_links(markdown_text),
            'images': self.extract_images(markdown_text),
            'code_blocks': self.extract_code_blocks(markdown_text),
            'lists': self.extract_lists(markdown_text),
            'word_count': len(markdown_text.split()),
            'char_count': len(markdown_text),
            'line_count': len(markdown_text.split('\n'))
        }
    
    def add_heading(self, markdown_text, heading, level=1):
        """Adds a heading to the beginning of Markdown"""
        prefix = '#' * level
        return f"{prefix} {heading}\n\n{markdown_text}"
    
    def add_table_of_contents(self, markdown_text):
        """Adds table of contents after first heading"""
        toc = self.table_of_contents(markdown_text)
        toc_section = f"## Table of Contents\n\n{toc}\n\n"
        first_heading = self.heading_pattern.search(markdown_text)
        if first_heading:
            end_pos = first_heading.end()
            return markdown_text[:end_pos] + '\n\n' + toc_section + markdown_text[end_pos:]
        return toc_section + markdown_text
    
    def create_table(self, headers, rows):
        """Creates a Markdown table"""
        header_row = '| ' + ' | '.join(headers) + ' |'
        separator = '| ' + ' | '.join(['---'] * len(headers)) + ' |'
        data_rows = ['| ' + ' | '.join(row) + ' |' for row in rows]
        return '\n'.join([header_row, separator] + data_rows)
    
    def parse_table(self, markdown_text):
        """Parses a Markdown table into structured data"""
        table_pattern = re.compile(r'\|(.+)\|\n\|[-:\s|]+\|\n((?:\|.+\|\n?)+)', re.MULTILINE)
        tables = []
        for match in table_pattern.finditer(markdown_text):
            headers = [h.strip() for h in match.group(1).split('|') if h.strip()]
            rows = []
            for row_text in match.group(2).strip().split('\n'):
                cells = [c.strip() for c in row_text.split('|')[1:-1]]
                rows.append(cells)
            tables.append({'headers': headers, 'rows': rows})
        return tables
    
    def wrap_code_block(self, code, language=''):
        """Wraps code in a Markdown code block"""
        return f"```{language}\n{code}\n```"
    
    def create_link(self, text, url):
        """Creates a Markdown link"""
        return f"[{text}]({url})"
    
    def create_image(self, alt_text, url):
        """Creates a Markdown image"""
        return f"![{alt_text}]({url})"
    
    def create_bold(self, text):
        """Creates bold text"""
        return f"**{text}**"
    
    def create_italic(self, text):
        """Creates italic text"""
        return f"*{text}*"
    
    def create_blockquote(self, text):
        """Creates a blockquote"""
        lines = text.split('\n')
        return '\n'.join(f"> {line}" for line in lines)
    
    def create_task_list(self, tasks):
        """Creates a task list"""
        return '\n'.join(f"- [ ] {task}" for task in tasks)
    
    def count_words(self, markdown_text):
        """Counts words in Markdown excluding syntax"""
        plain = self.markdown_to_plain_text(markdown_text)
        return len(plain.split())
    
    def reading_time(self, markdown_text, words_per_minute=200):
        """Estimates reading time for Markdown content"""
        word_count = self.count_words(markdown_text)
        minutes = word_count / words_per_minute
        return {
            'word_count': word_count,
            'minutes': round(minutes, 1),
            'formatted': f"{int(minutes)} min read" if minutes >= 1 else "< 1 min read"
        }
    
    def validate_links(self, markdown_text, check_external=False):
        """Validates links in Markdown"""
        links = self.extract_links(markdown_text)
        results = []
        for link in links:
            url = link['url']
            if url.startswith('#'):
                anchor = url[1:]
                headings = self.extract_headings(markdown_text)
                valid = any(h['anchor'] == anchor for h in headings)
                results.append({
                    'text': link['text'],
                    'url': url,
                    'valid': valid,
                    'type': 'anchor'
                })
            elif url.startswith('http'):
                results.append({
                    'text': link['text'],
                    'url': url,
                    'valid': True,
                    'type': 'external',
                    'checked': check_external
                })
            else:
                valid = os.path.exists(url)
                results.append({
                    'text': link['text'],
                    'url': url,
                    'valid': valid,
                    'type': 'file'
                })
        return results
    
    def split_sections(self, markdown_text):
        """Splits Markdown into sections by headings"""
        sections = []
        current_heading = {'level': 0, 'title': 'Introduction'}
        current_content = []
        for line in markdown_text.split('\n'):
            heading_match = self.heading_pattern.match(line)
            if heading_match:
                if current_content:
                    sections.append({
                        'heading': current_heading,
                        'content': '\n'.join(current_content)
                    })
                current_heading = {
                    'level': len(heading_match.group(1)),
                    'title': heading_match.group(2).strip()
                }
                current_content = []
            else:
                current_content.append(line)
        if current_content:
            sections.append({
                'heading': current_heading,
                'content': '\n'.join(current_content)
            })
        return sections
    
    def merge_markdown_files(self, file_paths, output_path):
        """Merges multiple Markdown files"""
        combined = []
        for path in file_paths:
            content = self.read_markdown(path)
            combined.append(content)
            combined.append('\n---\n')
        self.write_markdown(output_path, '\n'.join(combined))
        return True