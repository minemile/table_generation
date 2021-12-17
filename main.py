import json

from tqdm import tqdm
from yattag import Doc
from yattag import indent

from IPython.core.display import display, HTML
from IPython.display import IFrame

from jinja2 import Template
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from table_parser import TableParser
import matplotlib.pyplot as plt
import os
import cv2

from bs4 import BeautifulSoup
import json
import random
import numpy as np

from table_generation import RandomTableGenerator
from table_style import CSSGenerator, CSSProperty
from html_generator import TemplateGenerator, WordGenerator, HTMLTableGeneratorByTemplate

from table_style import CSSGenerator, CSSProperty


def send(cmd, params={}):
    resource = "/session/%s/chromium/send_command_and_get_result" % driver.session_id
    url = driver.command_executor._url + resource
    body = json.dumps({'cmd': cmd, 'params': params})
    response = driver.command_executor._request('POST', url, body)
    # if response['status']: raise Exception(response.get('value'))
    return response.get('value')


if __name__ == '__main__':
    OUT_COUNT = 5
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
        chrome_options = Options()
        chrome_options.add_argument("disable-extensions")
        chrome_options.add_argument("window-position=0,0")

        chrome_options.add_argument("headless")

        table_parser = TableParser(chrome_options)
        file_path = f"output/{NAME}/{i}/"
        parsed_table = table_parser.parse_table(file_path)
        parsed_table.to_annotations(flat=True)

        root = os.path.join(os.getcwd(), file_path)
        # TRANSPARENCY
        options = webdriver.ChromeOptions()
        options.add_argument("disable-gpu")
        options.add_argument("disable-infobars")
        options.add_argument("headless")
        options.add_argument("--hide-scrollbars")

        driver = webdriver.Chrome("./chromedriver", chrome_options=options)
        driver.get("file:///" + os.path.join(root, "table.html"))

        # take screenshot with a transparent background
        send("Emulation.setDefaultBackgroundColorOverride",
             {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}})
        driver.get_screenshot_as_file(os.path.join(root, "table_transparent.png"))
        send("Emulation.setDefaultBackgroundColorOverride")
