# dp-redo

A python variant of the [redo](http://cr.yp.to/redo.html) build system, with which You Can (Not) Redo.

## Example

Let's say we have a build process where we read `test.c` and generate `test.o`:

```python
import os, sys
source_tree = os.path.dirname(os.path.abspath(sys.argv[0]))

def test():
    source = os.path.join(source_tree, "test.c")

    # The simplest compiler 😁
    os.system("cat {} > {}".format(source, "test.o"))

if __name__ == "__main__":
    test()
```

`test` will be run every time no matter whether `test.c` gets an update or not, which wastes much time. Now let's add some magic:

```python
from dp_redo import *
import os, sys

source_tree = os.path.dirname(os.path.abspath(sys.argv[0]))

@do("test.o")
def test(target_name, target_base_name, output_path):
    redo_ifchange("test.c")
    source = os.path.join(source_tree, "test.c")
    os.system("cat {} > {}".format(source, output_path))

if __name__ == "__main__":
    redo_ifchange(test)
```

If you run it multiple times:

```
PS C:\Users\lishengq\source\repos\dp-redo\build> python ..\test2.py
Redoing target: test
PS C:\Users\lishengq\source\repos\dp-redo\build> python ..\test2.py
Skipping target test: it's up to date.
```

Fantastic, isn't it? If you changed `test.c`, modified the `test` method itself, or deleted `test.o`, `test` will be executed again:

```
PS C:\Users\lishengq\source\repos\dp-redo\build> python ..\test2.py
Redoing target: test. Reason: It's python code has changed
PS C:\Users\lishengq\source\repos\dp-redo\build> python ..\test2.py
Redoing target: test. Reason: The target file doesn't exist
PS C:\Users\lishengq\source\repos\dp-redo\build> python ..\test2.py
Redoing target: test. Reason: The test.c has been modified
PS C:\Users\lishengq\source\repos\dp-redo\build> 
```

A target method can also depend on another method, which is rather simple:

```python
from dp_redo import *
import os, sys

source_tree = os.path.dirname(os.path.abspath(sys.argv[0]))

@do("test2.o")
def test2(target_name, target_base_name, output_path):
    os.system("echo test2 > " + output_path)

@do("test.o")
def test(target_name, target_base_name, output_path):
    redo_ifchange(test2, "test.c")
    source = os.path.join(source_tree, "test.c")
    os.system("cat {} > {}".format(source, output_path))

if __name__ == "__main__":
    redo_ifchange(test)
```