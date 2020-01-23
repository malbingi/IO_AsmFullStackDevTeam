from radon.complexity import cc_visit
from radon.cli.tools import iter_filenames

def CodeAnalysis(filepatch = '.', methodname = ''):
    comp = 0
    for filename in iter_filenames([filepatch]):
        print(str(filename))
        with open(filename) as fobj:
            source = fobj.read()

        blocks = cc_visit(source)
        print("Searching for " + methodname + " in " + filepatch)
        for i in blocks:
            print(i.name + ' - ' + str(i.complexity) + ' - ' + methodname)
            if(i.name == methodname):
                comp = i.complexity
                print('FOUND')
                break

    return comp