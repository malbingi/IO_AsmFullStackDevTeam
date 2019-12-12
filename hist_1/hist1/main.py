from packages.CodeReaderService import CodeReader, reload_counters
import os


def main():
    path = ".\\resources"
    files = []
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
        if len(cs.get_imports()) == 0:
            print("No imports\n\n")

        for im in cs.get_imports():
            print_str = "Import: " + im.get_source_name() + "\n"
            i = 1
            for f_r in im.files_ref:
                print_str += str(i) + ". " + f_r.reference_name\
                             + " calls: " + str(f_r.call_count) + '\n'
                i += 1
            print(print_str)


if __name__ == "__main__":
    main()
