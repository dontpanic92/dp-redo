from dp_redo import *
import os, sys, re

source_tree = os.path.dirname(os.path.abspath(sys.argv[0]))

@do(".x")
def default_x(target_name, target_base_name, output_path):
    print("Compiling {}.y".format(target_base_name))
    os.system("cat {}.y > {}".format(os.path.join(source_tree, target_base_name), output_path))

@do("test2.o")
def test2(target_name, target_base_name, output_path):
    print("In test2 ")
    os.system("echo test2 > " + output_path)
    redo_ifchange("test.x")

@do("test.o")
def test(target_name, target_base_name, output_path):
    redo_ifchange(test2)
    source = os.path.join(source_tree, "test.c")
    os.system("gcc -M -MF test.c.dep -o {} {}".format(output_path, source))

    deps = open('test.c.dep', 'r').read().split(": ")[1].strip().split("\\\n")
    redo_ifchange(*deps)

if __name__ == "__main__":
    redo_ifchange(test)
