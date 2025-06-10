# markdown_utils.py
import re

def convert_markdown_to_html(markdown_text: str) -> tuple[str, str]:
    """
    Converts markdown text to HTML for email compatibility.
    
    Args:
        markdown_text: The markdown text to convert
        
    Returns:
        tuple: (html_content, plain_text_content)
    """
    # Store the original plain text for the email's text/plain part
    plain_text_content = markdown_text
    
    # Process the content line by line for better control
    lines = markdown_text.split('\n')
    html_lines = []
    
    i = 0
    in_list = False
    in_code_block = False
    code_block_content = []
    current_list_type = None
    
    while i < len(lines):
        line = lines[i]
        
        # Check for setext-style headers (underlined with === or ---)
        if i + 1 < len(lines) and lines[i+1] and (set(lines[i+1]) == {'='} or set(lines[i+1]) == {'-'}):
            if '=' in lines[i+1]:
                html_lines.append(f'<h1 style="margin: 16px 0;">{process_inline_formatting(line)}</h1>')
            else:
                html_lines.append(f'<h2 style="margin: 14px 0;">{process_inline_formatting(line)}</h2>')
            i += 2
            continue
            
        # Check for ATX-style headers (# Heading)
        header_match = re.match(r'^(#{1,6})\s*(.+)$', line)
        if header_match:
            level = len(header_match.group(1))
            content = header_match.group(2)
            margin = 16 - (level - 1) * 2
            style = f'margin: {margin}px 0;'
            html_lines.append(f'<h{level} style="{style}">{process_inline_formatting(content)}</h{level}>')
            i += 1
            continue
            
        # Check for code blocks
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_content = []
            else:
                in_code_block = False
                code_content = '\n'.join(code_block_content)
                html_lines.append(f'<pre style="background-color: #f6f8fa; border-radius: 3px; padding:  16px; overflow: auto;"><code>{code_content}</code></pre>')
            i += 1
            continue
            
        if in_code_block:
            code_block_content.append(line)
            i += 1
            continue
            
        # Check for horizontal rules
        if re.match(r'^(\*\*\*|---|___)$', line):
            html_lines.append('<hr style="margin: 20px 0; border: none; border-top: 1px solid #dddddd;">')
            i += 1
            continue
            
        # Check for unordered lists
        ul_match = re.match(r'^\s*[\*\-\+]\s+(.+)$', line)
        if ul_match:
            if not in_list or current_list_type != 'ul':
                if in_list:
                    html_lines.append('</ol>' if current_list_type == 'ol' else '</ul>')
                html_lines.append('<ul style="margin: 10px 0; padding-left: 25px;">')
                in_list = True
                current_list_type = 'ul'
            content = process_inline_formatting(ul_match.group(1))
            html_lines.append(f'<li style="margin: 5px 0;">{content}</li>')
            i += 1
            continue
            
        # Check for ordered lists
        ol_match = re.match(r'^\s*(\d+)[\.\)]\s+(.+)$', line)
        if ol_match:
            if not in_list or current_list_type != 'ol':
                if in_list:
                    html_lines.append('</ul>' if current_list_type == 'ul' else '</ol>')
                html_lines.append('<ol style="margin: 10px 0; padding-left: 25px;">')
                in_list = True
                current_list_type = 'ol'
            content = process_inline_formatting(ol_match.group(2))
            html_lines.append(f'<li style="margin: 5px 0;">{content}</li>')
            i += 1
            continue
            
        if in_list and not (ul_match or ol_match):
            html_lines.append('</ul>' if current_list_type == 'ul' else '</ol>')
            in_list = False
            
        # Process tables
        if '|' in line and i + 1 < len(lines) and '|' in lines[i+1] and '-' in lines[i+1]:
            header_cells = [cell.strip() for cell in line.strip().split('|') if cell.strip()]
            
            table_html = ['<table style="border-collapse: collapse; width: 100%; margin: 15px 0;">']
            table_html.append('<thead><tr>')
            for cell in header_cells:
                processed_cell = process_inline_formatting(cell)
                table_html.append(f'<th style="border: 1px solid #ddd; padding: 8px; text-align: left;">{processed_cell}</th>')
            table_html.append('</tr></thead>')
            
            table_html.append('<tbody>')
            j = i + 2
            while j < len(lines) and '|' in lines[j]:
                row_cells = [cell.strip() for cell in lines[j].strip().split('|') if cell.strip()]
                table_html.append('<tr>')
                for cell in row_cells:
                    processed_cell = process_inline_formatting(cell)
                    table_html.append(f'<td style="border: 1px solid #ddd; padding: 8px;">{processed_cell}</td>')
                table_html.append('</tr>')
                j += 1
            table_html.append('</tbody></table>')
            
            html_lines.append(''.join(table_html))
            i = j
            continue
            
        if line.strip():
            processed_line = process_inline_formatting(line)
            html_lines.append(f'<p style="margin: 10px 0;">{processed_line}</p>')
        i += 1
    
    if in_list:
        html_lines.append('</ul>' if current_list_type == 'ul' else '</ol>')
    
    html = '\n'.join(html_lines)
    
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Email</title>
</head>
<body style="font-family: Arial, 'Helvetica Neue', Helvetica, sans-serif; line-height: 1.6; color: #333333; padding: 20px;">
{html}
</body>
</html>'''

    return html, plain_text_content

def process_inline_formatting(text: str) -> str:
    """
    Process inline Markdown formatting within a block of text.
    Corrected version with no unnecessary escaping.
    """
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text, flags=re.DOTALL)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text, flags=re.DOTALL)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text, flags=re.DOTALL)
    
    text = re.sub(r'!\[(.*?)\]\((.*?)\)', r'<img src="\2" alt="\1" style="max-width: 100%; height: auto; margin: 10px 0;">', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" style="color: #007bff; text-decoration: underline;">\1</a>', text)
    text = re.sub(r'`(.*?)`', r'<code style="background-color: #f6f8fa; border-radius: 3px; padding: 0.2em 0.4em; font-family: monospace;">\1</code>', text, flags=re.DOTALL)
    
    return text
