import os
import networkx as nx
import matplotlib.pyplot as plt
import community
from packages.CodeReaderService import CodeReader, reload_counters


def main():
    path = "..\\hist_1\\hist_1\\resources"
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

    g = nx.Graph()
    for item in dict_files_to_methods:
        g.add_node(item)
        g.add_node(dict_files_to_methods.get(item, ""))
        g.add_edge(item, dict_files_to_methods.get(item))

    for item in dict_files_to_modules:
        g.add_node(item)
        g.add_edge(item, dict_files_to_modules.get(item))

    part = community.best_partition(g)
    values = [part.get(node) for node in g.nodes()]
    pos = nx.spring_layout(g)
    plt.figure(figsize=(10, 7))
    plt.axis('off')
    nx.draw_networkx_nodes(g, pos, node_size=100, node_color=list(values))
    nx.draw_networkx_edges(g, pos, alpha=0.3, arrows=True)
    plt.savefig("graph.png")  # save as png
    plt.show()


if __name__ == "__main__":
    main()