# coding=utf8
class FilePipeline(object):

    def __init__(self, file_name):
        self.file_name = file_name

    def save(self, text):
        print(text)
        with open(self.file_name, 'w') as f:
            f.write(str(text))
