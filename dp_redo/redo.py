from .logging import get_logger
from .version import __version__
import inspect, hashlib, atexit, os, sys, json, shutil

logger = get_logger()

# All targets functions keyed by names
targets = {}
json_info = {}

REDO_DATA_DIR_NAME = ".redo"
REDO_DATA_FILE_NAME = "info.json"
source_tree = os.path.dirname(os.path.abspath(sys.argv[0]))
build_tree = os.getcwd()
redo_data_dir = os.path.join(build_tree, REDO_DATA_DIR_NAME)
redo_data_path = os.path.join(redo_data_dir, REDO_DATA_FILE_NAME)

class Target():
    def __init__(self, func, output_name, last_info):
        self.name = func.__name__
        self.__func = func
        self.__output_name = output_name
        self.__output_path = os.path.join(build_tree, output_name)
        self.__info = last_info
        self.digest = self.__digest(func)
        self.__updated_target_deps = []
        self.__updated_source_deps = []

        if "target_deps" not in self.__info:
            self.__info["target_deps"] = {}

        if "source_deps" not in self.__info:
            self.__info["source_deps"] = {}
    
    def add_target_dep(self, dep):
        self.__updated_target_deps.append(dep)

    def add_source_dep(self, dep):
        dep = os.path.join(source_tree, dep.strip())
        if not os.path.exists(dep):
            logger.error("Cannot find source file: %s", dep)
            exit(1)

        self.__updated_source_deps.append(dep)

    def redo_ifchange(self):
        need_redo = False
        redo_reason = ""
        if "digest" not in self.__info or self.__info["digest"] != self.digest:
            need_redo = True
            self.__info["digest"] = self.digest
            redo_reason = "It's python code has changed"

        if need_redo == False:
            if not os.path.exists(self.__output_path):
                need_redo = True
                redo_reason = "The target file doesn't exist"

        if need_redo == False:
            for dep in self.__info["source_deps"]:
                dep_path = os.path.join(source_tree, dep)
                if not os.path.exists(dep_path) or \
                    abs(self.__info["source_deps"][dep] - os.path.getmtime(dep_path)) > 0.001:
                        need_redo = True
                        redo_reason = "The {} has been modified".format(dep)
                        break
        
        if need_redo == False:
            for dep in self.__info["target_deps"]:
                if dep not in targets:
                    need_redo = True
                    break

                if not os.path.exists(targets[dep].__output_path) or \
                    abs(self.__info["target_deps"][dep] - os.path.getmtime(targets[dep].__output_path)) > 0.001:
                    need_redo = True
                    redo_reason = "{} has been modified".format(dep)
                    break

                need_redo = targets[dep].redo_ifchange() or need_redo
        
        redoing_tmp_name = self.__output_path + "---redoing"
        if need_redo:
            logger.info("Redoing target: %s. Reason: %s", self.name, redo_reason)
            self.__func(self.__output_name, os.path.basename(self.__output_name), redoing_tmp_name)
            
            self.__info["source_deps"] = {}
            for source_dep in self.__updated_source_deps:
                self.__info["source_deps"][source_dep] = os.path.getmtime(os.path.join(source_tree, source_dep))
            
            self.__info["target_deps"] = {}
            for target_dep in self.__updated_target_deps:
                self.__info["target_deps"][target_dep.name] = os.path.getmtime(target_dep.__output_path)

            if os.path.exists(redoing_tmp_name):
                shutil.move(redoing_tmp_name, self.__output_path)
            else:
                logger.warning("%s didn't generate any target file.", self.name)
        else:
            logger.info("Skipping target %s: it's up to date.", self.name)

    def __digest(self, func):
        md5 = hashlib.md5()
        for v in dir(func.__code__):
            if not v.startswith("co_") or v == "co_firstlineno":
                continue
            md5.update(str(func.__code__.__getattribute__(v)).encode(encoding="utf-8"))
        return md5.hexdigest()


def do(output_name):
    def register(func):
        if func.__name__ in targets:
            logger.error("Duplicate targets found: %s", output_name)
            exit(1)

        if func.__code__.co_argcount != 3:
            logger.error("Target method must receive 3 arguments")
            exit(1)
        
        if func.__name__ not in json_info:
            json_info[func.__name__] = {}

        targets[func.__name__] = Target(func, output_name, json_info[func.__name__])
        return func
    return register

def redo_ifchange(*deps):
    caller = inspect.stack()[1].function
    for dep in deps:
        if isinstance(dep, str):
            source_dep(caller, dep)
        else:
            target_dep(caller, dep)

def source_dep(caller, dep_name):
    if caller != "<module>":
        targets[caller].add_source_dep(dep_name)

def target_dep(caller, dep):
    if dep.__name__ not in targets:
        logger.error("redo_ifchange must be applied to a target. Invalid function: %s", dep.__name__)
        exit(1)

    if caller != "<module>":
        targets[caller].add_target_dep(targets[dep.__name__])

    targets[dep.__name__].redo_ifchange()

def flush_info():
    if not os.path.exists(redo_data_dir):
        os.mkdir(redo_data_dir)

    with open(redo_data_path, mode='w', encoding='utf-8') as json_file:
        json.dump(json_info, json_file)

def load_info():
    global json_info
    if os.path.exists(redo_data_path):
        with open(redo_data_path, encoding='utf-8') as json_file:
            try:
                json_info = json.load(json_file)
            except Exception as e:
                logger.warning("info.json is corrupted - ignoring it.")

load_info()
atexit.register(flush_info)
    #if caller not in targets:
    #    targets[caller] = Target(func, None)
    
    #if dep not in targets:
    #    targets[dep.__name__] = Target()

    #caller.add_dep_target(target)
