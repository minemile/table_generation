import random
from typing import List, Sequence, Tuple

from jinja2 import Template

import font_loader


class CSSProperty:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def get_random_value(self):
        return random.choice(self.values)

FONTS = {}
FONTS['DIR'] = '/Users/19592219/git/table_generation/data/fonts'
FONTS['FACES'] = font_loader.load_faces(FONTS['DIR'])

DEFAULT_PROPERTIES = {
    "font_face": FONTS['FACES'],

    "table_width": [str(i) + '%' for i in range(75, 101)],
    "table_height": [str(i) + '%' for i in range(75, 101)],

    "td_border_vertical_px": [str(i) + 'px' for i in range(3)],
    "td_border_horizontal_px": [str(i) + 'px' for i in range(3)],

    "td_border_color": ["black"],
    "td_text_align": ["left", "center", "right"],

    "tr_n_child": ["odd", "even", "none"],
    "tr_back_color": ["none"],

    "th_back_color": ["none"],
    "th_border_px": [str(i) + 'px' for i in range(5)],
    "th_border_color": ["black"]
}

DEFAULT_PROPERTIES = [CSSProperty(k, v) for k, v in DEFAULT_PROPERTIES.items()]


class CSS:
    def __init__(self, template, params):
        self.template = template
        self.params = params
        self.jinja_template = Template(template)
        self.css = self.populate_css()

    def populate_css(self):
        return self.jinja_template.render(**self.params)

    def save(self, path):
        with open(path, 'w') as f:
            f.write(str(self.css))


class CSSGenerator:
    def __init__(self, template, properties=None):
        if properties is None:
            properties = DEFAULT_PROPERTIES
        self.template = template
        self.properties = properties

    def generate(self):
        params = {}
        if len(self.properties) == 0:
            raise ValueError("Add css properties")
        for css_property in self.properties:
            property_value = css_property.get_random_value()
            params[css_property.name] = property_value
        return CSS(self.template, params)

    def add_property(self, css_property):
        self.properties.append(css_property)
