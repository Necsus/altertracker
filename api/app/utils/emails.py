import os

def render_template_with_data(template_path, data):
    with open(template_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    for key, value in data.items():
        html_content = html_content.replace(f"[{key}]", value)
    return html_content