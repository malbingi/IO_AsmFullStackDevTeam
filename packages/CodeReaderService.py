import os
import re
import enum


class CallRefType(enum.Enum):
    DEFINITION = 0
    CLASS = 1
    MAIN = 2


class EndType(enum.Enum):
    Not_end = 1
    Next_def_block = 2
    Next_class_block = 3
    End_block = 4


def reload_counters():
    CodeReader.Method_counter = 0
    CodeReader.Class_counter = 0
    CodeReader.Code_counter = 0


class CodeReader:
    Method_counter = 0
    Class_counter = 0
    Code_counter = 0
    Methods = {}
    Classes = {}
    CodeReaders = {}

    def __init__(self, _file_path, source_folder="\\resources", auto_load=1, checking=False):
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
        self.is_in_class = -1
        self.is_in_def = 0
        self.actual_method_stack = []
        g = MethodInfo("def GLOBAL()", -1, self.index)
        if -1 not in CodeReader.Methods:
            CodeReader.Methods[-1] = g
        self.actual_method_stack.append(g)
        self.actual_class_stack = []
        self.actual_object_stack = []
        self.reader = {}

        if auto_load == 1:
            self.load_file_data(checking)

    def check_references(self):
        self.load_file_data(True)

    def load_file_data(self, checking):
        if not checking:
            with open(self.file_path, "r") as file:
                self.reader = file.readlines()
        self.actual_object_stack.append({})
        iterator = 0
        while len(self.reader) > iterator:
            line = self.reader[iterator].replace('\n', '')
            self.lines_counter += 1
            from_block = False
            if line.__contains__("class "):
                self.is_in_class += 1
                iterator = self.load_class(iterator, checking=checking)
                from_block = True
            elif line.__contains__("def "):
                self.is_in_def += 1
                iterator = self.load_method(iterator, checking=checking)
                from_block = True
            elif line.__contains__("import"):
                im = ImportInfo(line)
                if not checking:
                    self.imports.append(im)
                im.is_local = self.check_is_local(im)
            elif checking:
                self.check_if_using_any_method(line, CallRefType.MAIN)
                self.check_if_using_any_class(line, CallRefType.MAIN)
                self.check_refs(line)
            if not from_block:
                iterator += 1

        self.actual_object_stack.pop()

    def check_refs(self, line):
        for i in self.imports:
            for f_r in i.files_ref:
                if line.__contains__(f_r.reference_name+'(') or line.__contains__(f_r.reference_name+'.')\
                        or line.__contains__(f_r.reference_name+')'):
                    f_r.increase_counter()

    def load_method(self, index, is_class_method=False, checking=False):
        self.actual_method_stack.append(MethodInfo(self.reader[index],
                                                   CodeReader.Method_counter,
                                                   self.index, is_class_method))
        index += 1
        self.actual_object_stack.append({})
        if not checking:
            CodeReader.Methods[CodeReader.Method_counter] = self.actual_method_stack[self.is_in_def]
        CodeReader.Method_counter += 1
        if is_class_method is False:
            index = self.read_line_in_block(index, False, CallRefType.DEFINITION, checking)
        else:
            self.actual_class_stack[self.is_in_class].add_method(self.actual_method_stack[self.is_in_def])
            index = self.read_line_in_block(index, True, CallRefType.DEFINITION, checking)
        self.actual_object_stack.pop()
        self.actual_method_stack.pop()
        self.is_in_def -= 1
        return index

    def load_class(self, index, is_in_class=False, checking=False):
        if is_in_class is True:
            parent_index = self.actual_class_stack[self.is_in_class-1].index
        else:
            parent_index = -1
        self.actual_class_stack.append(ClassInfo(self.reader[index],
                                                 CodeReader.Class_counter,
                                                 self.index,
                                                 parent_index))
        index += 1
        if not checking:
            CodeReader.Classes[CodeReader.Class_counter] = self.actual_class_stack[self.is_in_class]
        CodeReader.Class_counter += 1
        self.actual_object_stack.append({})
        index = self.read_line_in_block(index, True, CallRefType.CLASS, checking)
        self.actual_object_stack.pop()
        self.actual_class_stack.pop()
        self.is_in_class -= 1
        return index

    def read_line_in_block(self, index, is_in_class=False, block_type=CallRefType.DEFINITION, checking=False):
        while index < len(self.reader):
            if checking:
                self.check_if_using_any_method(self.reader[index], block_type)
                self.check_if_using_any_class(self.reader[index], block_type)
                self.check_refs(self.reader[index])
            cond = self.check_is_end_of_block(index, block_type)
            if cond.end_type is EndType.End_block:
                index = cond.index
                break
            elif cond.end_type is EndType.Next_def_block\
                    and block_type is not CallRefType.MAIN:
                self.is_in_def += 1
                index = self.load_method(cond.index, is_in_class, checking) - 1
            elif cond.end_type is EndType.Next_class_block:
                self.is_in_class += 1
                index = self.load_class(cond.index, is_in_class, checking) - 1
            index += 1
        return index

    def check_is_next_block(self):
        print("s"+self.index)

    def check_if_using_self(self, line):
        s_pos = line.find("self")
        if s_pos > -1:
            for m in CodeReader.Classes[self.actual_class_stack[self.is_in_class].index].methods.values():
                if line.__contains__("self."+m.name+"(") or line.__contains__("self."+m.name+" ")\
                        or line.__contains__("self."+m.name+",") or line.__contains__("self."+m.name+")"):
                    m.increase_counter()
                    self.add_call_ref(m.index,
                                      CallRefType.CLASS,
                                      CodeReader.Classes[self.actual_class_stack[self.is_in_class].index].index)

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
        if block_type is CallRefType.DEFINITION:
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
            return ConditionEofBlock(EndType.Not_end, index+end_ln)

    def check_if_using_any_method(self, line, block_type=CallRefType.DEFINITION):
        for k, v in CodeReader.Methods.items():
            if v.is_class_method is False:
                if line.__contains__(v.name+'(') or line.__contains__(v.name+',') or line.__contains__(v.name+')'):
                    v.increase_counter()
                    if block_type is CallRefType.DEFINITION or block_type is CallRefType.CLASS:
                        if self.is_in_def > 0:
                            self.add_call_ref(k, CallRefType.DEFINITION)
                        else:
                            self.add_call_ref(k, CallRefType.DEFINITION)
                    else:
                        CodeReader.Methods[-1].add_call_ref(k, CallRefType.DEFINITION)

    def check_if_using_any_class(self, line, block_type=CallRefType.DEFINITION):
        stack_length = len(self.actual_object_stack)-1
        for k, v in CodeReader.Classes.items():
            c_pos = line.find(v.name)
            if c_pos > -1:
                name_length = len(v.name)
                if line[c_pos+name_length] is "(":
                    eq_pos = line.find("=")
                    d_pos = line.find(".", line.find(")"))
                    if d_pos == -1 and c_pos > eq_pos > -1:
                        obj = ObjectInfo(line[:eq_pos-len(line)].replace(" ", ''), k)
                        v.increase_init()
                        self.add_call_ref(v.methods[0].index, block_type)
                        self.actual_object_stack[stack_length][obj.name] = obj
                        return
                    elif d_pos > -1 and c_pos > eq_pos > -1:
                        v.increase_init()
                        for m in v.methods.values():
                            if line.find(m.name, d_pos) > -1:
                                m.increase_counter()
                                self.add_call_ref(m.index, CallRefType.DEFINITION, k)
                                return
        self.check_if_object_using_any_method(line, block_type)
        if self.is_in_class > -1:
            self.check_if_using_self(line)

    def check_if_object_using_any_method(self, line, block_type=CallRefType.DEFINITION):
        for s_ob in self.actual_object_stack:
            for k, v in s_ob.items():
                c_pos = line.find(k)
                if c_pos > -1:
                    name_length = len(v.name)
                    if line[c_pos + name_length] is ".":
                        for km, vm in CodeReader.Classes[v.class_index].methods.items():
                            if line.__contains__(v.name + '.' + vm.name):
                                vm.increase_counter()
                                if block_type is CallRefType.DEFINITION or block_type is CallRefType.CLASS:
                                    if self.is_in_def > -1:
                                        self.add_call_ref(km, CallRefType.DEFINITION, v.class_index)
                                    else:
                                        self.add_call_ref(km, CallRefType.DEFINITION, v.class_index)

    def add_call_ref(self, m_ind, block_type, c_ind=-1):
        if block_type is CallRefType.DEFINITION:
            CodeReader.Methods[self.actual_method_stack[self.is_in_def].index]\
                .add_call_ref(m_ind, c_ind, block_type)
        elif block_type is CallRefType.CLASS:
            CodeReader.Classes[self.actual_class_stack[self.is_in_class].index]\
                .add_call_ref(m_ind, c_ind, block_type)
        else:
            CodeReader.Methods[-1].add_call_ref(m_ind, c_ind, block_type)

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
    def __init__(self, line, index, f_index, class_method=False):
        self.is_class_method = class_method
        self.file_index = f_index
        self.index = index
        self.spaces = int(re.search(r'[^ ]', line).start())
        s_ind = line.find("def ", 0, line.__len__())
        self.name = line[s_ind+4:].split('(')[0]
        self.call_reference = {}
        self.call_count = 0
        self.objects = {}

    def increase_counter(self):
        self.call_count += 1

    def add_call_ref(self, index, class_index=-1, call_obj_type=CallRefType.DEFINITION):
        add_call_ref(self, index, class_index, call_obj_type)


def create_method_class_key(c_index, m_index):
    return str(c_index)+"-"+str(m_index)


def get_class_from_class_key(key):
    if key[0] is "-":
        return -1
    return int(key.split("-")[0])


def get_method_from_class_key(key):
    tab = key.split("-")
    return int(tab[len(tab)-1])


class CallRef:
    def __init__(self, index, class_index=-1):
        self.class_index = class_index
        self.index = index
        if class_index > -1:
            self.type = CallRefType.CLASS
        else:
            self.type = CallRefType.DEFINITION
        self.call_count = 1

    def increase_call_counter(self):
        self.call_count += 1


class ConditionEofBlock:
    def __init__(self, end_type, index):
        self.end_type = end_type
        self.index = index


class ClassInfo:
    def __init__(self, line, index, f_index, parent_class=-1):
        self.parent_class = parent_class
        self.file_index = f_index
        self.index = index
        self.spaces = re.search(r'[^ ]', line).start()
        s_ind = line.find("class ", 0, line.__len__())
        self.name = line[s_ind + 6:].split(':')[0].split("(")[0]
        self.methods = {}
        self.methods_counter = 0
        self.objects = {}
        self.call_reference = {}
        self.init_count = 0

    def add_method(self, method):
        self.methods[self.methods_counter] = method
        self.methods_counter += 1

    def add_call_ref(self, index, class_index=-1, call_obj_type=CallRefType.CLASS):
        add_call_ref(self, index, class_index, call_obj_type)

    def increase_init(self):
        self.init_count += 1
        if self.methods[0].name == "__init__":
            self.methods[0].increase_counter()


class ObjectInfo:
    def __init__(self, name, class_index=-1):
        self.name = name
        self.class_index = class_index


# call_obj_type ----> 0 - def, 1 - class
def add_call_ref(obj, index, class_index=-1, call_obj_type=CallRefType.DEFINITION):
    if call_obj_type is CallRefType.DEFINITION:
        if index in obj.call_reference:
            obj.call_reference.get(index).increase_call_counter()
        else:
            obj.call_reference[index] = CallRef(index)
    elif call_obj_type is CallRefType.CLASS:
        if index in obj.call_reference:
            obj.call_reference.get(create_method_class_key(class_index, index)).increase_call_counter()
        else:
            obj.call_reference[create_method_class_key(class_index, index)] = CallRef(index, class_index)
    return obj
