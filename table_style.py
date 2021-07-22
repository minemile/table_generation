import random
from jinja2 import Template


class CSSProperty:
    def __init__(self, name, values):
        self.name = name
        self.values = values

    def get_random_value(self):
        return random.choice(self.values)


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
    def __init__(self, template):
        self.template = template
        self.properties = []

    def generate(self):
        params = {}
        if len(self.properties) == 0:
            raise ValueError("Add css properties")
        for property in self.properties:
            property_value = property.get_random_value()
            params[property.name] = property_value
        return CSS(self.template, params)
    
    def add_property(self, property):
        self.properties.append(property)