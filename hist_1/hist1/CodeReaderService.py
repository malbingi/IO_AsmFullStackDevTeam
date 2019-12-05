import os


class CodeReader:
    def __init__(self, _file_path, source_folder="\\resources", auto_load=1):
        self.file_path = _file_path
        self.source_folder = source_folder
        self.filename = self.file_path.split('\\')[-1]
        self.lines_counter = 0
        self.imports = []
        self.files = []
        if auto_load == 1:
            self.load_file_data()

    def load_file_data(self):
        with open(self.file_path, "r") as file:
            for line in file:
                line = line.replace('\n', '')
                self.lines_counter += 1
                if line.__contains__("import"):
                    im = ImportInfo(line)
                    self.imports.append(im)
                    im.is_local = self.check_is_local(im)
                else:
                    self.check_refs(line)

    def check_refs(self, line):
        for i in self.imports:
            for f_r in i.files_ref:
                if line.__contains__(f_r.reference_name+'(') or line.__contains__(f_r.reference_name+'.')\
                        or line.__contains__(f_r.reference_name+')'):
                    f_r.increase_counter()

    def check_is_local(self, im_info):
        name = ""
        if im_info.name[0] == '.':
            name = im_info.name[1:]
        else:
            name = im_info.name
        if self.files.__len__() == 0:
            for r, d, f in os.walk(self.source_folder):
                for file in f:
                    if '.py' in file:
                        self.files.append(file)
        for file in self.files:
            if file == name+".py":
                return 1
        return 0

    def get_name(self):
        return self.filename

    def get_lines_counter(self):
        return self.lines_counter

    def get_imports(self):
        return self.imports


class ImportInfo:
    def __init__(self, line):
        self.name = ""
        self.files_ref = []
        self.is_local = 0
        if not line.index("import") > 0:
            self.name = line.split(' ')[1]
            self.files_ref.append(FileRefImport(self.name))
        else:
            names = line.split("import")
            if not line.__contains__("from"):
                if names[0].replace(' ', '') == "":
                    self.name = names[1].replace(' ', '')
                else:
                    self.name = names[0].split(' ')[1].replace(' ', '')
                
            else:
                self.name = names[0].replace("from", '').replace(' ', '')
            for r_n in names[1].split(','):
                self.files_ref.append(FileRefImport(r_n.replace(' ', '')))

    def get_source_name(self):
        if self.is_local == 1:
            return self.name.split('.')[-1] + ".py"
        else:
            return self.name + " - [lib]"



class FileRefImport:
    def __init__(self, reference_name):
        self.reference_name = reference_name
        self.call_count = 0

    def increase_counter(self):
        self.call_count += 1
