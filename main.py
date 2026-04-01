import json
from jinja2 import Environment, FileSystemLoader

with open('datasetp1.json', 'r') as file:
    data = json.load(file)

env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('home.html')
html_output = template.render(products=data)

with open('home.html', 'w', encoding='utf-8') as f:
    f.write(html_output)