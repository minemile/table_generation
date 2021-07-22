import os
import argparse

class Table:
    def __init__(self, name, html_table, css):
        self.name = name
        self.html = html_table
        self.css = css

    def save(self, path):
        full_path = os.path.join(path, self.name)
        if not os.path.exists(full_path):
            os.makedirs(full_path)

        html_table_path = os.path.join(full_path, "table.html")
        self.html.save(html_table_path)

        css_path = os.path.join(full_path, "style.css")
        self.css.save(css_path)


class RandomTableGenerator:
    def __init__(self, table_generator, css_generator):
        self.table_generator = table_generator
        self.css_generator = css_generator

    def generate(self, name):
        html_table = self.table_generator.generate()
        css = self.css_generator.generate()
        table = Table(name, html_table, css)
        return table
    