from dp_redo import *
import os, sys

source_tree = os.path.dirname(os.path.abspath(sys.argv[0]))

@do("test2.o")
def test2(target_name, target_base_name, output_path):
    print("In test2")
    os.system("echo test2 > " + output_path)

@do("test.o")
def test(target_name, target_base_name, output_path):
    redo_ifchange(test2, "test.c")
    source = os.path.join(source_tree, "test.c")
    os.system("cat {} > {}".format(source, output_path))

if __name__ == "__main__":
    redo_ifchange(test)
