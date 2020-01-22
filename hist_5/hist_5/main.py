import os

import graphviz

from packages.CodeReaderService import CodeReader, reload_counters


def main():
    path = "..\\..\\hist_1\\hist1\\resources"
    files = []
    dict_files_to_methods = {}
    dict_files_to_modules = {}
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
            dict_files_to_methods[m.name] = str(CodeReader.CodeReaders.get(m.file_index).filename)
            for k, v in m.call_reference.items():
                dict_files_to_methods[CodeReader.Methods[k].name] = str(
                    CodeReader.CodeReaders.get(m.file_index).filename)

        else:
            dict_files_to_methods[m.name] = str(CodeReader.CodeReaders.get(m.file_index).filename)

    del dict_files_to_methods['GLOBAL']

    for cs in code_readers:
        for im in cs.get_imports():
            dict_files_to_modules[im.get_source_name()] = str(cs.get_name())

    dot = graphviz.Digraph(comment='Relationships between methods and files(in Python files are modules)')
    for item in dict_files_to_methods:
        dot.node(item, color='blue')
        dot.node(dict_files_to_methods.get(item, ""), shape='square', color='red')
        dot.edge(item, dict_files_to_methods.get(item), color='blue', penwidth='5')

    for item in dict_files_to_modules:
        dot.node(item, color='red')
        dot.edge(item, dict_files_to_modules.get(item), color='yellow', penwidth='5')
    dot.render('test-output/round-table.gv', view=True)


if __name__ == "__main__":
    main()