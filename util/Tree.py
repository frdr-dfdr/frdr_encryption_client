import os

from util.util import Util

class Tree:
    def __init__(self):
        self.dirCount = 0
        self.fileCount = 0
        self.totalSize = 0

    def readable(self, size, showDecimal=True):
        """ Convert bytes to human readable form"""
        for x in [' ', 'K', 'M', 'G', 'T', 'P']:
            if size < 10.0 and showDecimal:
                return "{:4.1f}{}".format(size, x)
            elif size < 1024.0:
                return "{:4.0f}{}".format(size, x)
            size /= 1024.0

    def register(self, absolute):
        fileSize = 0
        if os.path.isdir(absolute):
            self.dirCount += 1
        else:
            self.fileCount += 1
        try:
            fileSize = os.path.getsize(absolute)
            self.totalSize += fileSize
        except OSError:
            pass
        return fileSize

    def summary(self):
        return self.readable(self.dirCount, False) + " directories\n" + self.readable(self.fileCount, False) + " files\n" + self.readable(self.totalSize) + " total size\n"

    def walk(self, directory, f, prefix = ""):
        cache = Util.path_tree(directory)

        for index, item in enumerate(cache['contents']):

            if item['name'] == "." or item['name'] == "..":
                continue

            absolute = os.path.join(directory, item['name'])
            self.register(absolute)

            if index == len(cache['contents']) - 1:
                print(prefix + "└── [" + self.readable(item["size"]) + "] " + item['name'], file=f)
                if os.path.isdir(absolute):
                    self.walk(absolute, f, prefix + "    ")
                    
            else:
                print(prefix + "├── [" + self.readable(item["size"]) + "] " + item['name'], file=f)
                if os.path.isdir(absolute):
                    self.walk(absolute, f, prefix + "│   ")