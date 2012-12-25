import os


class Event(object):

    def __init__(self, filename, timestamp, line, current_host=None, file_config=None):
        self.data = {
            '@source': "file://{0}{1}".format(current_host, filename),
            '@source_host': current_host,
            '@source_path': filename,
            '@type': file_config.get('type', filename),
            '@tags': file_config.get('tags', filename),
            '@fields': file_config.get('fields', filename),
            '@timestamp': timestamp,
            '@message': line.strip(os.linesep),
        }

    def __str__(self):
        return self.data["@timestamp"] + "," + self.data["@source"] + "," + self.data["@message"]

    def __hash__(self):
        return hash(self.data)

    def overwrite(self, event):
        self.data = hash(event)

    def to_dict(self):
        return self.data

    def get(self, key):
        if key in self.data:
            return self.data[key]
        elif key in self.data["@fields"]:
            return self.data["@fields"][key]
        else:
            return False

    def set(self, key, value):
        if key in self.data:
            self.data[key] = value
        else:
            self.data["@fields"][key] = value

    def has(self, key):
        return (key in self.data or key in self.data["@fields"])

    def remove(self, field):
        if field in self.data:
            del self.data[field]
        else:
            del self.data["@fields"][field]

    def __eq__(self, other):
        if self.__class__ == other._class__:
            return hash(self) == hash(other)
        else:
            return False
