from CodeReaderService import CodeReader
import os


def main():
    path = ".\\resources"
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.py' in file:
                files.append(os.path.join(r, file))

    for f in files:
        cs = CodeReader(f, path)

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
