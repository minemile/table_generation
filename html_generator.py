from typing import Collection

import numpy as np
from bs4 import BeautifulSoup
from bs4.builder import HTML

from yattag import Doc
from yattag import indent
import random
from bs4 import BeautifulSoup

WRAP = '<html><head><link rel="stylesheet" href="style.css" /></head>' \
       '<body><table class="iksweb"><tbody>\n{table_body}</tbody></table></body></html>'

TH = '<th></th>'
TD = '<td{colspan}{rowspan}></td>'
TR = '<tr>{cells}</tr>\n'


class TemplateGenerator:
    def __init__(self, col_range=(2, 5), row_range=(2, 8), colspan=0.2, rowspan=0.1):
        self.col_range = col_range
        self.row_range = row_range
        self.colspan = colspan
        self.rowspan = rowspan

    def generate(self):
        cols = random.randint(*self.col_range)
        rows = random.randint(*self.row_range)
        if self.rowspan <= 0 and self.colspan <= 0:
            table_body = (TR.format(cells='<td></td>' * cols) + '\n') * rows
            return WRAP.format(table_body=table_body)
        grid = np.zeros((rows, cols))  # 1 if cell is reserved
        table_body = ''
        for row in range(rows):
            cells = ''
            for col in range(cols):
                if grid[row][col]:
                    continue
                colspan = 1
                rowspan = 1
                if col + 1 < cols and random.random() < self.colspan:
                    i = 1
                    while col + i < cols and not grid[row][col:col + i + 1].any():
                        i += 1
                    max_colspan = i
                    colspan = random.randint(1, max_colspan)
                    if colspan > 1:
                        grid[row, col:col + colspan] = 1
                        print(row, col, rowspan, colspan, '\n', grid)
                if row + 1 < rows and random.random() < self.rowspan:
                    i = 1
                    while row + i < rows and not grid[row:row + i + 1, col:col + colspan].any():
                        i += 1
                    max_rowspan = i
                    rowspan = random.randint(1, max_rowspan)
                    if rowspan > 1:
                        grid[row:row + rowspan, col:col + colspan] = 1
                        print(row, col, rowspan, colspan, '\n', grid)
                rowspan = f' rowspan="{rowspan}"' if rowspan > 1 else ''
                colspan = f' colspan="{colspan}"' if colspan > 1 else ''
                cells += TD.format(rowspan=rowspan, colspan=colspan)
                grid[row][col] = 1
            table_body += TR.format(cells=cells)
        return WRAP.format(table_body=table_body)


class WordGenerator:
    def __init__(self, words, gen_numbers=True, n_max=5, p=0.5):
        self.words = words
        self.n_max = n_max
        self.p = p
        self.gen_numbers = gen_numbers

    def get_string(self):
        string = []
        if self.gen_numbers and random.random() < self.p:
            string.append(self.generate_number())
        else:
            for _ in range(self.n_max):
                if random.random() < self.p:
                    string.append(self.generate_word())
        return string

    def generate_number(self):
        return f"{random.uniform(-100000, 100000):.{random.randint(0, 8)}f}"

    def generate_word(self):
        return random.choice(self.words)


class HTMLTable:
    def __init__(self, html):
        self.html = html

    def save(self, path):
        with open(path, 'w') as f:
            f.write(str(self.html))


class HTMLTableGeneratorByTemplate:
    def __init__(self, word_generator, template):
        self.word_generator = word_generator
        self.template = template

    def generate(self):
        html = BeautifulSoup(self.template, "html.parser")
        for td in html.find_all(["td", "th"]):
            words = self.word_generator.get_string()
            for word in words:
                new_tag = html.new_tag("word")
                new_tag.string = word + "\n"
                td.append(new_tag)
        return HTMLTable(html)


class TableStructure:
    def __init__(self, merge_rows_indexes, merge_cols_indexes):
        # Fill full rows or cols for now
        if merge_rows_indexes and merge_cols_indexes:
            raise ValueError("Only one mode available")
        self.merge_rows_indexes = merge_rows_indexes
        self.merge_cols_indexes = merge_cols_indexes


class HTMLTableGenerator:
    def __init__(self, word_generator, n_rows, n_cols, add_header=True, table_structure=None):
        self.word_generator = word_generator
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.add_header = add_header
        self.table_structure = table_structure

    def generate(self):
        doc, tag, text, line = Doc().ttl()
        with tag('html'):
            with tag("head"):
                doc.stag("link", rel='stylesheet', href="style.css")
            with tag('body'):
                self.generate_table(tag, line)
        intended = indent(doc.getvalue())
        # html_table = HTMLTable(intended)

        # if self.add_header:
        # html_table = self.add_spans(html_table)
        # if self.add_header:
        return HTMLTable(intended)

    def generate_table(self, tag, line):
        with tag("table"):
            for row_index in range(self.n_rows):

                with tag("tr"):
                    for col_index in range(self.n_cols):
                        row_type = self.get_table_row_type(row_index)

                        if row_index in self.table_structure.merge_rows_indexes:
                            # Merge columns
                            with tag(row_type, colspan=self.n_cols):
                                words = self.word_generator.get_string()
                                for word in words:
                                    line("word", word)
                            break

                        if row_index == 0 and col_index in self.table_structure.merge_cols_indexes:
                            # Merge rows
                            with tag(row_type, rowspan=self.n_rows):
                                words = self.word_generator.get_string()
                                for word in words:
                                    line("word", word)
                            continue

                        if row_index != 0 and col_index in self.table_structure.merge_cols_indexes:
                            continue

                        with tag(row_type):
                            words = self.word_generator.get_string()
                            for word in words:
                                line("word", word)

    def get_table_row_type(self, index):
        if index == 0 and self.add_header:
            return "th"
        else:
            return "td"

    def add_spans(self, html_table, merge_cols=2, merge_rows=2):
        sp = BeautifulSoup(html_table.html, 'html.parser')
        rows = sp.find_all("tr")
        columns = rows.find_all("td")
        for i, tr in enumerate(sp.find_all("tr")):
            for j, td in enumerate(tr.find_all("td")):

                # merge columns 
                if i == 0 and j == merge_cols:
                    td['colspan'] = 2
                # if merge_cols >= 0 and i == 0 and j == len(tr.find_all("td")) - 1:
                # td.decompose()
                # if i == 0 and

                # merge rows
                if i == merge_rows and j == 0:
                    td['rowspan'] = 2
                if i == merge_rows + 1 and j == 0:
                    td.decompose()
        # html_table.html = str(sp)
        return sp


class SpanGenerator:
    # Header spans generator
    def __init__(self, col_indexes: dict, row_indexes: dict):
        self.col_indexes = col_indexes
        self.row_indexes = row_indexes

    def add_spans(self, table_html):
        table_html = table_html.html
        sp = BeautifulSoup(table_html, 'html.parser')
        if self.col_indexes is not None:
            self.add_columns_spans(sp)
        if self.row_indexes is not None:
            self.add_rows_spans(sp)
        if self.col_indexes and self.row_indexes:
            if 0 in self.col_indexes and 0 in self.row_indexes:
                raise ValueError("Column and row indexes starts at 0")
        return HTMLTable(str(sp.prettify()))

    def add_columns_spans(self, soup):
        to_delete = sum([span_length - 1 for span_length in self.col_indexes.values()])
        rows = soup.find_all("tr")
        columns = rows[0].find_all("td")
        for i, row in enumerate(rows):
            for j, col in enumerate(row.find_all("td")):
                if i == 0 and j in self.col_indexes:
                    span_length = self.col_indexes[j]
                    if (span_length + j - 1) >= len(columns):
                        raise ValueError(
                            f"Span length {span_length} for column {j} >= row length {len(columns)}")
                    col['colspan'] = span_length
                if i == 0 and j >= len(columns) - to_delete:
                    col.decompose()

    def add_rows_spans(self, soup):
        to_delete = sum([span_length - 1 for span_length in self.row_indexes.values()])
        rows = soup.find_all("tr")
        columns = rows[0].find_all("td")
        current_row = None
        for i, row in enumerate(rows):
            for j, col in enumerate(row.find_all("td")):
                if j == 0 and i in self.row_indexes:
                    current_row = i
                    span_length = self.row_indexes[i]
                    if (span_length + i - 1) >= len(rows):
                        raise ValueError(
                            f"Span length {span_length} for row {i} >= column length {len(rows)}")
                    col['rowspan'] = span_length
                if j == 0 and current_row is not None:
                    if current_row + 1 <= i <= current_row + self.row_indexes[current_row] - 1:
                        # print("Here delete i: {0}, j: {1}".format(i, j))
                        col.decompose()
