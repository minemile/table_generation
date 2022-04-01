import json
import os

from cv2 import cv2
from selenium import webdriver

from utils import parse_location


class Word:
    def __init__(self, word_tag):
        self.word = word_tag
        self.bbox = parse_location(word_tag.rect)
        self.text = word_tag.text

    def to_annotations(self, flat=False):
        if flat:
            return self.text, self.bbox
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

    def to_annotations(self, flat=False):
        words = []
        if flat:
            boxes = []
            for word in self.words:
                word, box = word.to_annotations(flat)
                words.append(word)
                boxes.append(box)
            return words, boxes
        words = [word.to_annotations(flat) for word in self.words]
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
            cv2.rectangle(im, (x_min, y_min), (x_max, y_max), (0, 255, 0), 1)
            for word in cell.words:
                x_min, y_min, x_max, y_max = word.bbox
                cv2.rectangle(im, (x_min, y_min), (x_max, y_max), (0, 0, 255), 1)

        for header_cells in self.headers:
            x_min, y_min, x_max, y_max = header_cells.bbox
            cv2.rectangle(im, (x_min, y_min), (x_max, y_max), (255, 0, 0), 1)
            for word in header_cells.words:
                x_min, y_min, x_max, y_max = word.bbox
                cv2.rectangle(im, (x_min, y_min), (x_max, y_max), (0, 0, 255), 1)
        return im

    def to_annotations(self, flat=False):
        if flat:
            output = {'labels': [], 'boxes': []}
            for cell in self.cells + self.headers:
                cell_words, cell_boxes = cell.to_annotations(flat)
                output['labels'].extend(cell_words)
                output['boxes'].extend(cell_boxes)
        else:
            output = {'cells': [cell.to_annotations(flat) for cell in self.cells + self.headers]}

        with open(os.path.join(self.file_root, "annotation.json"), "w") as f:
            json.dump(output, f, indent=None if flat else 4)





class TableParser:
    def __init__(self, options):
        self.chrome_options = options
        self.driver = webdriver.Chrome("./chromedriver", options=self.chrome_options)

    def send(self, cmd, params=None):
        if params is None:
            params = {}
        resource = "/session/%s/chromium/send_command_and_get_result" % self.driver.session_id
        url = self.driver.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': params})
        response = self.driver.command_executor._request('POST', url, body)
        # if response['status']: raise Exception(response.get('value'))
        return response.get('value')

    def parse_table(self, file_path):
        root = os.path.join(os.getcwd(), file_path)

        self.driver.get("file:///" + os.path.join(root, "table.html"))
        self.driver.maximize_window()

        table = self.driver.find_element_by_tag_name("table")
        table_screenshot_path = os.path.join(root, "table.png")
        table.screenshot(table_screenshot_path)
        self.send("Emulation.setDefaultBackgroundColorOverride",
             {'color': {'r': 0, 'g': 0, 'b': 0, 'a': 0}})
        table.screenshot(os.path.join(root, "table_transparent.png"))
        self.send("Emulation.setDefaultBackgroundColorOverride")
        table_image = cv2.imread(table_screenshot_path)
        im = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(table_screenshot_path, cv2.bitwise_not(im))

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
