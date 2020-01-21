import os

import graphviz

from packages.CodeReaderService import CodeReader, get_method_from_class_key, reload_counters


def main():
    path = "..\\..\\hist_1\\hist1\\resources"
    files = []
    dict = {}
    method_ref_dict = {}
    for r, d, f in os.walk(path):
        for file in f:
            if '.py' in file:
                files.append(os.path.join(r, file))

    code_readers = []
    for f in files:
        code_readers.append(CodeReader(f, path))

    reload_counters()
    for cs in code_readers:
        cs.check_references()

    for m in CodeReader.Methods.values():
        if not m.is_class_method:
            print_str = print_method(m)
            print(print_str)

    print("======================= Classes=================\n")
    for c in CodeReader.Classes.values():
        print_str = "Name: " + str(c.index) + ' - ' + c.name + "  ============================"\
                    + "\n[file, init] - [" \
                    + CodeReader.CodeReaders.get(c.file_index).filename\
                    + ", " + str(c.init_count) + "]\n"\
                    + "GLOBAL CALLS:\n"

        for k, v in c.call_reference.items():
            if type(k) is not int:
                key = get_method_from_class_key(k)
            else:
                key = k
            if key > -1:
                print_str += "\tMethod: " + str(key) + " - " + str(CodeReader.Methods[key].name)
            else:
                print_str += "\tMethod: GLOBAL"
            print_str += " was called - " + str(v.call_count) + "\n"

        print_str += "\nLOCAL METHODS:\n"

        class_content = []
        for m in c.methods.values():
            class_content.append([m.name, m.call_count])
            references = []
            for k in m.call_reference.keys():

                if type(k) is not int:
                    if k.find("-") > -1:
                        k = get_method_from_class_key(k)
                references.append([CodeReader.Methods[k].name, CodeReader.Methods[k].call_count])

            method_ref_dict[m.name] = references
            print_str += print_method(m)
        print(print_str)

        dict[c.name] = class_content

    dot = graphviz.Digraph(comment='References graph')
    for item in dict:
        dot.node(item, item)
        for child in dict[item]:
            dot.edge(item, child[0], str(child[1]))

    for item_ in method_ref_dict:
        dot.node(item_, item_)
        for child_ in method_ref_dict[item_]:
            dot.edge(item_, child_[0], str(child_[1]))
    dot.render('test-output/round-table.gv', view=True)


def print_method(m):
    print_str = "\tName: " + str(m.index) + ' - ' + m.name + "\n\t[file, called] - [" \
                + str(CodeReader.CodeReaders.get(m.file_index).filename) + ', ' + str(m.call_count) + "]\n"
    for k, v in m.call_reference.items():
        if type(k) is not int:
            if k.find("-") > -1:
                k = get_method_from_class_key(k)
        print_str += "\t\tMethod: " + str(k) + " - " + str(CodeReader.Methods[k].name) + " was called - " + str(
            v.call_count) + "\n"
    return print_str


if __name__ == "__main__":
    main()
