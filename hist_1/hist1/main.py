from packages.CodeReaderService import CodeReader, reload_counters
import os
import graphviz


def main():
    path = ".\\resources"
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

        print("========= File: " + cs.get_name() + " ================")
        elements = []
        if len(cs.get_imports()) == 0:
            print("No imports\n\n")

        for im in cs.get_imports():
            print_str = "Import: " + im.get_source_name() + "\n"
            i = 1
            total = 0
            for f_r in im.files_ref:
                print_str += str(i) + ". " + f_r.reference_name \
                             + " calls: " + str(f_r.call_count) + '\n'
                total += f_r.call_count
                i += 1
            if im.is_local:
                elements.append([im.get_source_name(), total])
            print(print_str)

        dict[cs.get_name()] = elements

    dot = graphviz.Digraph(comment='References graph')
    for item in dict:
        dot.node(item, item)
        for child in dict[item]:
            dot.edge(item, child[0], str(child[1]))
    dot.render('test-output/round-table.gv', view=True)


if __name__ == "__main__":
    main()
