import json
import re


class JsonManip(object):
    def __init__(self, json_data):
        self.data = json_data

    def extract(self, regex, group):
        match = re.search(regex, self.data)
        if match:
            self.data = match.group(group)

    def get_data(self):
        return json.loads(self.data)
