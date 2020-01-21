import os

import graphviz

from packages.CodeReaderService import CodeReader, reload_counters


def main():
    path = "..\\..\\hist_1\\hist1\\resources"
    files = []
    dict = {}
    dict_with_relationships = {}
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
            print_str = "Name: " + str(m.index) + ' - ' + m.name + "\n[file, called] - [" \
                        + str(CodeReader.CodeReaders.get(m.file_index).filename) + ', ' + str(m.call_count) + "]\n"
            elements = []
            dict_with_relationships[m.name] = str(CodeReader.CodeReaders.get(m.file_index).filename)
            for k, v in m.call_reference.items():
                print_str += "\tMethod: " + str(k) + " - " + str(CodeReader.Methods[k].name) + " was called - " + str(
                    v.call_count) + "\n"
                elements.append([CodeReader.Methods[k].name, v.call_count])
                dict_with_relationships[CodeReader.Methods[k].name] = str(
                    CodeReader.CodeReaders.get(m.file_index).filename)
            dict[m.name] = elements
            print(print_str)
        else:
            dict_with_relationships[m.name] = str(CodeReader.CodeReaders.get(m.file_index).filename)

    del dict_with_relationships['GLOBAL']
    print(dict_with_relationships)

    dot = graphviz.Digraph(comment='Relationships between methods and files(in Python files are modules)')
    for item in dict_with_relationships:
        dot.node(item, color='blue')
        dot.node(dict_with_relationships.get(item, ""), shape='square', color='red')
        dot.edge(item, dict_with_relationships.get(item), color='blue')
    dot.render('test-output/round-table.gv', view=True)


if __name__ == "__main__":
    main()
