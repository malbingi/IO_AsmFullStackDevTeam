from packages.CodeReaderService import CodeReader, reload_counters
import os
import graphviz

def main():
    path = "..\\..\\hist_1\\hist1\\resources"
    files = []
    dict = {}

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
            for k, v in m.call_reference.items():
                print_str += "\tMethod: " + str(k) + " - " + str(CodeReader.Methods[k].name) + " was called - " + str(v.call_count) + "\n"
                elements.append([CodeReader.Methods[k].name, v.call_count])
            dict[m.name] = elements
            print(print_str)

    dot = graphviz.Digraph(comment='References graph')
    for item in dict:
        dot.node(item, item)
        for child in dict[item]:
            dot.edge(item, child[0], str(child[1]))
    dot.render('test-output/round-table.gv', view=True)


if __name__ == "__main__":
    main()
