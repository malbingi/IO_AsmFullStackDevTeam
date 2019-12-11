import os
import re
import enum


class CallRefType(enum.Enum):
    DEFINITION = 0
    CLASS = 1


class EndType(enum.Enum):
    Not_end = 1
    Next_def_block = 2
    Next_class_block = 3
    End_block = 4


class CodeReader:
    Method_counter = 0
    Code_counter = 0
    Methods = {}
    CodeReaders = {}

    def __init__(self, _file_path, source_folder="\\resources", if_load_classes=0, auto_load=1):
        CodeReader.CodeReaders[CodeReader.Code_counter] = self
        self.index = CodeReader.Code_counter
        CodeReader.Code_counter += 1

        self.file_path = _file_path
        self.source_folder = source_folder
        self.filename = self.file_path.split('\\')[-1]
        self.lines_counter = 0
        self.imports = []
        self.files = []

        # = hist2
        self.if_load_classes = if_load_classes
        self.is_in_class = -1
        self.is_in_def = -1
        self.actual_method_stack = []
        self.actual_class_stack = []
        self.reader = {}
        if auto_load == 1:
            self.load_file_data()

    def load_file_data(self):
        with open(self.file_path, "r") as file:
            self.reader = file.readlines()
            iterator = 0
            while len(self.reader) > iterator:
                line = self.reader[iterator].replace('\n', '')
                self.lines_counter += 1
                if line.__contains__("class "):
                    # create class obj === Todo hist 3
                    self.is_in_class += 1
                    iterator = self.load_class(iterator)
                elif self.is_in_class < 0 and line.__contains__("def "):
                    self.is_in_def += 1
                    iterator = self.load_method(iterator)
                elif line.__contains__("import"):
                    im = ImportInfo(line)
                    self.imports.append(im)
                    im.is_local = self.check_is_local(im)
                else:
                    self.check_if_using_any_method(line)
                    self.check_refs(line)
                iterator += 1

    def check_refs(self, line):
        for i in self.imports:
            for f_r in i.files_ref:
                if line.__contains__(f_r.reference_name+'(') or line.__contains__(f_r.reference_name+'.')\
                        or line.__contains__(f_r.reference_name+')'):
                    f_r.increase_counter()

    def load_method(self, index):
        self.actual_method_stack.append(MethodInfo(self.reader[index], CodeReader.Method_counter, self.index))
        CodeReader.Methods[CodeReader.Method_counter] = self.actual_method_stack[self.is_in_def]
        CodeReader.Method_counter += 1
        index = self.read_line_in_block(index)
        self.actual_method_stack.pop()
        self.is_in_def -= 1
        return index

    def load_class(self, index):
        self.actual_class_stack.append(ClassInfo(self.reader[index], self.index))
        index = self.read_line_in_block(index, CallRefType.CLASS)
        self.actual_class_stack.pop()
        self.is_in_class -= 1
        return index

    def read_line_in_block(self, index, block_type=CallRefType.DEFINITION):
        index += 1
        while index < len(self.reader):
            self.check_if_using_any_method(self.reader[index])
            self.check_refs(self.reader[index])
            cond = self.check_is_end_of_block(index, block_type)
            if cond.end_type is EndType.End_block:
                break
            elif cond.end_type is EndType.Next_def_block\
                    and block_type is CallRefType.DEFINITION:
                self.is_in_def += 1
                index = self.load_method(cond.index)
            elif cond.end_type is EndType.Next_class_block:
                self.is_in_class += 1
                index = self.load_class(cond.index)
            index += 1
        return index

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

    def check_is_end_of_block(self, index, block_type=CallRefType.DEFINITION):
        if block_type == CallRefType.DEFINITION:
            act_obj = self.actual_method_stack[self.is_in_def]
        else:
            act_obj = self.actual_class_stack[self.is_in_class]
        iterator = index
        end_ln = 0
        new_block = 0
        end_block = 0
        while iterator < len(self.reader) and new_block == 0 and end_block == 0 and iterator-index <= end_ln:
            if self.reader[iterator].replace('\t', '').replace(' ', '') == '\n':
                end_ln += 1
            elif int(re.search(r'[^ ]', self.reader[iterator]).start()) <= act_obj.spaces:
                end_block = 1
                break
            elif self.reader[iterator].__contains__("def "):
                new_block = 1
                break
            elif self.reader[iterator].__contains__("class "):
                new_block = 2
                break
            iterator += 1

        if end_block == 1:
            return ConditionEofBlock(EndType.End_block, iterator)
        elif new_block == 1:
            return ConditionEofBlock(EndType.Next_def_block, iterator)
        elif new_block == 2:
            return ConditionEofBlock(EndType.Next_class_block, iterator)
        else:
            return ConditionEofBlock(EndType.Not_end, 0)

    def check_if_using_any_method(self, line):
        # ======= todo calls from class methods
        for k, v in CodeReader.Methods.items():
            if line.__contains__(v.name+'(') or line.__contains__(v.name+',') or line.__contains__(v.name+')'):
                v.increase_counter()
                if self.is_in_def >= 0:
                    self.actual_method_stack[self.is_in_def].add_call_ref(k)

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


class MethodInfo:
    def __init__(self, line, index, f_index):
        self.file_index = f_index
        self.index = index
        self.spaces = re.search(r'[^ ]', line).start()
        s_ind = line.find("def ", 0, line.__len__())
        self.name = line[s_ind+4:].split('(')[0]
        self.call_reference = {}
        self.call_count = 0

    def increase_counter(self):
        self.call_count += 1

    # call_obj_type ----> 0 - def, 1 - class
    def add_call_ref(self, index, call_obj_type=CallRefType.DEFINITION):
        if call_obj_type == CallRefType.DEFINITION:
            if index in self.call_reference:
                self.call_reference.get(index).increase_call_counter()
            else:
                self.call_reference[index] = CallRef(index)
        elif call_obj_type == CallRefType.CLASS:
            if index in self.call_reference:
                self.call_reference.get(index).increase_call_counter()
            else:
                self.call_reference[index] = CallRef(index, CallRefType.CLASS)


class CallRef:
    def __init__(self, index, type=CallRefType.DEFINITION):
        self.index = index
        self.type = type
        self.call_count = 1

    def increase_call_counter(self):
        self.call_count += 1


class ConditionEofBlock:
    def __init__(self, end_type, index):
        self.end_type = end_type
        self.index = index


class ClassInfo:
    def __init__(self, line, f_index):
        self.file_index = f_index
        self.spaces = re.search(r'[^ ]', line).start()
        s_ind = line.find("class ", 0, line.__len__())
        self.name = line[s_ind + 6:].split(':')[0]