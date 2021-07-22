from bs4 import BeautifulSoup
from bs4.builder import HTML

from yattag import Doc
from yattag import indent
import random


class WordGenerator():
    def __init__(self, words, n_max=5, p=0.5):
        self.words = words
        self.n_max = n_max
        self.p = p
    
    def get_string(self):
        string = []
        for _ in range(self.n_max):
            if random.random() < self.p:
                string.append(random.choice(self.words))
        return string

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
    def __init__(self, merge_rows_indxs, merge_cols_indxs):
        # Fill full rows or cols for now
        if merge_rows_indxs and merge_cols_indxs:
            raise ValueError("Only one mode available")
        self.merge_rows_indxs = merge_rows_indxs
        self.merge_cols_indxs = merge_cols_indxs


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
        return HTMLTable(intended)

    def generate_table(self, tag, line):
        with tag("table"):
            for row_indx in range(self.n_rows):

                with tag("tr"):
                    for col_indx in range(self.n_cols):
                        row_type = self.get_table_row_type(row_indx)



                        if row_indx in self.table_structure.merge_rows_indxs:
                            # Merge rows
                            with tag(row_type, colspan=self.n_cols):
                                words = self.word_generator.get_string()
                                for word in words:
                                    line("word", word)
                            break


                                
                        if row_indx == 0 and col_indx in self.table_structure.merge_cols_indxs:
                            # Merge columns
                            with tag(row_type, rowspan=self.n_rows):
                                words = self.word_generator.get_string()
                                for word in words:
                                    line("word", word)
                            continue
                        
                        if row_indx != 0 and col_indx in self.table_structure.merge_cols_indxs:
                            continue
                        
                        with tag(row_type):
                            words = self.word_generator.get_string()
                            for word in words:
                                line("word", word)
    
    def get_table_row_type(self, indx):
        if indx == 0 and self.add_header:
            return "th"
        else:
            return "td"