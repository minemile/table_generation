import os
import json
from urllib import parse

import cv2
from utils import parse_location, parse_locations, bbox_to_4_coords

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Word:
    def __init__(self, word_tag):
        self.word = word_tag
        self.bbox = parse_location(word_tag.rect)
        self.text = word_tag.text

    def to_annotations(self):
        return {"text": self.text, "bbox": self.bbox}


class Cell:
    def __init__(self, cell_type, cell):
        self.cell_type = cell_type
        self.cell = cell
        self.bbox = parse_location(cell.rect)
        self.words = self.parse_words()

    def parse_words(self):
        words = self.cell.find_elements_by_tag_name("word")
        words_locations = []
        for word in words:
            words_locations.append(Word(word))
        return words_locations

    def to_annotations(self):
        words = []
        for word in self.words:
            words.append(word.to_annotations())
        return {"bbox": self.bbox, "class": self.cell_type, "words": words}


class ParsedTable:
    def __init__(self, file_root, image, locations):
        self.image = image
        self.file_root = file_root
        self.locations = locations
        self.cells = locations["cells"]
        self.headers = locations["headers"]

    def draw_bboxes(self):
        im = self.image.copy()
        for cell in self.cells:
            x_min, y_min, x_max, y_max = cell.bbox
            cv2.rectangle(im, (x_min, y_min), (x_max, y_max), (0, 255, 0), 3)
            for word in cell.words:
                x_min, y_min, x_max, y_max = word.bbox
                cv2.rectangle(im, (x_min, y_min), (x_max, y_max), (0, 0, 255), 3)

        for header_cells in self.headers:
            x_min, y_min, x_max, y_max = header_cells.bbox
            cv2.rectangle(im, (x_min, y_min), (x_max, y_max), (255, 0, 0), 3)
            for word in header_cells.words:
                x_min, y_min, x_max, y_max = word.bbox
                cv2.rectangle(im, (x_min, y_min), (x_max, y_max), (0, 0, 255), 3)
        return im

    def to_annotations(self):
        cells = []
        for cell in self.cells + self.headers:
            cells.append(cell.to_annotations())

        output = {"cells": cells}
        with open(os.path.join(self.file_root, "annotation.json"), "w") as f:
            json.dump(output, f, indent=4)


class TableParser:
    def __init__(self, options):
        self.chrome_options = options
        self.driver = webdriver.Chrome("./chromedriver", options=self.chrome_options)

    def parse_table(self, file_path):
        root = os.path.join(os.getcwd(), file_path)

        self.driver.get("file:///" + os.path.join(root, "table.html"))
        self.driver.maximize_window()

        table = self.driver.find_element_by_tag_name("table")
        table_screenshot_path = os.path.join(root, "table.png")
        table.screenshot(table_screenshot_path)

        table_image = cv2.imread(table_screenshot_path)
        im = cv2.cvtColor(table_image, cv2.COLOR_BGR2RGB)

        cells_raw = self.driver.find_elements_by_tag_name("td")
        cells = []
        for cell in cells_raw:
            cells.append(Cell("td", cell))

        headers = []
        headers_raw = self.driver.find_elements_by_tag_name("th")
        for header in headers_raw:
            headers.append(Cell("th", header))

        locations = {
            "cells": cells,
            "headers": headers,
        }

        parsed_table = ParsedTable(root, im, locations)
        return parsed_table
