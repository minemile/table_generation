import json

from tqdm import tqdm

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from table_parser import TableParser
import os

import json

from table_generation import RandomTableGenerator
from html_generator import TemplateGenerator, WordGenerator, HTMLTableGeneratorByTemplate

from table_style import CSSGenerator


def send(driver, cmd, params=None):
    if params is None:
        params = {}
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd': cmd, 'params': params})
    response = driver.command_executor._request('POST', url, body)
    # if response['status']: raise Exception(response.get('value'))
    return response.get('value')


if __name__ == '__main__':
    OUT_COUNT = 50000
    NAME = 'random_table'
    with open("css/style_template.css") as f:
        css_template_str = f.read()

    with open("css/css_properties.json") as f:
        css_default_params = json.load(f)

    words = []
    with open("data/russian.txt", encoding='utf-8') as f:
        for line in f:
            words.append(line.strip())
    word_generator = WordGenerator(words, n_max=6, p=0.5)
    with open("html_templates/fin_table.html") as f:
        html_template_str = f.read()

    chrome_options = Options()
    chrome_options.add_argument("disable-extensions")
    chrome_options.add_argument("window-position=0,0")

    chrome_options.add_argument("headless")

    table_parser = TableParser(chrome_options)
    for i in tqdm(range(OUT_COUNT)):
        tg = TemplateGenerator()
        html_template_str = tg.generate()
        html_generator = HTMLTableGeneratorByTemplate(word_generator, html_template_str)
        css_generator = CSSGenerator(css_template_str)
        css = css_generator.generate()
        html_table = html_generator.generate()
        random_table_generator = RandomTableGenerator(html_generator, css_generator)
        full_table = random_table_generator.generate(name=NAME)
        full_table.save("output/", i)
        file_path = f"output/{NAME}/{i}/"
        parsed_table = table_parser.parse_table(file_path)
        parsed_table.to_annotations(flat=True)
