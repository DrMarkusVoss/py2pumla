#!/usr/bin/python
"""Command Line Tool and PUMLA hook for processing
python files and producing PUMLA conformant
PlantUML models of it.
"""

__author__ = "Dr. Markus Voss (private person)"
__copyright__ = "(C) Copyright 2021 by Dr. Markus Voss (private person)"
__license__ = "GPL"
__version__ = "0.2.1"
__maintainer__ = "Dr. Markus Voss (private person)"
__status__ = "Development"

import sys
import os
from importlib.util import spec_from_file_location, module_from_spec
import inspect

pumla_path = "/Users/mvoss/Desktop/git/github/pumla"

def identifyMe():
    """ information about the executed command """
    print("py2pumla v0.2 - by Dr. Markus Voss")

def isInBlacklist(path, blacklist):
    """ check whether the given path is contained in the
        given blacklist list."""
    retval = False
    for e in blacklist:
        if (e in path):
            retval = True
    return retval

def createClassPUMLCode(classelement, targetpath):
    #print(classelement)
    #print("class-el-name = " + classelement.__name__)
    #print("class-el_mod = " + classelement.__module__)
    # ltw = lines to write
    ltw = "'PUMLAMR\n@startuml\n!include " + pumla_path + "/pumla_macros.puml\n!include modelrepo_json.puml\n\n"
    ce_name = classelement.__name__
    ce_alias = ce_name.lower() + "Class"
    ltw = ltw + "!if ($PUMVarShowBody)\n"
    ltw = ltw + 'class "'+ ce_name + '" as ' + ce_alias + ' <<Python>> <<class>> { \n'
    #print(dir(classelement))
    #print(classelement.__dict__)
    for me in dir(classelement):
        if ((not ("__" in me)) or (me == "__init__")):
            me_name = me
            #print(me)
            me_raw = classelement.__dict__[me]
            me_args = me_raw.__code__.co_varnames
            ltw = ltw + "\t+" + me_name + str(me_args).replace("'", "").replace(",)", ")") + "\n"

    ltw = ltw + "!endif\n"
    ltw = ltw + "}\n\n"
    ltw = ltw + "!if ($PUMVarShowDescr)\n"

    for me in dir(classelement):
        if ((not ("__" in me)) or (me == "__init__")):
            me_raw = classelement.__dict__[me]
            if not(me_raw.__doc__ == None):
                ltw = ltw + "note right of " + ce_alias + "::" + me + "\n"
                ltw = ltw + str(me_raw.__doc__) + "\n"
                ltw = ltw + "end note\n\n"

    ltw = ltw + "note bottom of " + ce_alias + "\n"
    ltw = ltw + "\t" + str(classelement.__doc__) + "\n"
    ltw = ltw + "end note\n"
    ltw = ltw + "!endif\n"

    ltw = ltw + "\n@enduml\n"
    #print(ltw)

    # write file here
    tfn = targetpath + "/" + ce_alias + ".puml"
    with open(tfn, "w") as fil:
        fil.write(ltw)

    return ce_alias

def createModuleFunctionsPUMLCode(module, modulefuncs, targetpath):
    # todo: rework this
    ltw = "'PUMLAMR\n@startuml\n!include " + pumla_path + "/pumla_macros.puml\n!include modelrepo_json.puml\n\n"
    me_name = module.__name__
    me_alias = me_name.lower() + "Module"
    ltw = ltw + "!if ($PUMVarShowBody)\n"
    modfunc_name = me_name + 'ModFuncs'
    ltw = ltw + 'class "Module ' + me_name + ' Functions" as ' + modfunc_name + ' <<Python>> <<module>>   {\n'
    for mf in modulefuncs:

        me_name = mf.__name__
        me_args = mf.__code__.co_varnames
        ltw = ltw + "\t+" + str(me_name) + str(me_args).replace("'", "").replace(",)", ")") + "\n"


    ltw = ltw + "}\n\n"

    ltw = ltw + "!if ($PUMVarShowDescr)\n"

    for me in modulefuncs:
        if ((not ("__" in me.__name__)) or (me.__name__ == "__init__")):
            if not(me.__doc__ == None):
                ltw = ltw + "note right of " + modfunc_name + "::" + me.__name__ + "\n"
                ltw = ltw + str(me.__doc__) + "\n"
                ltw = ltw + "end note\n"

    ltw = ltw + "!endif\n"
    ltw = ltw + "@enduml\n\n"

    #print(ltw)
    #write file here
    tfn = targetpath + "/" + modfunc_name + ".puml"
    with open(tfn, "w") as fil:
        fil.write(ltw)

    return modfunc_name

def createModulePUMLCore(module, filename, list_of_elementalias, mymod_func, mymod_uses, targetpath):
    ltw = "'PUMLAMR\n@startuml\n!include " + pumla_path + "/pumla_macros.puml\n!include modelrepo_json.puml\n\n"
    me_name = module.__name__
    me_alias = me_name.lower() + "Module"
    ltw = ltw + "!if ($PUMVarShowBody)\n"
    ltw = ltw + 'package "' + filename + '" as ' + me_alias + ' <<Python>> { \n'
    # if not(mymod_func == ""):
    #     ltw = ltw + '\tclass "Functions" <<Python>> <<module>> {\n'
    #     ltw = ltw + mymod_func
    #     ltw = ltw + '\t}\n\n'
    for e in list_of_elementalias:
        ltw = ltw + "\tPUMLAPutInternalElement(" + e + ")\n"

    ltw = ltw + "}\n\n"

    ltw = ltw + mymod_uses + "\n\n"

    ltw = ltw + "!if ($PUMVarShowDescr)\n"
    ltw = ltw + "note bottom of " + me_alias + "\n"
    ltw = ltw + "\t" + str(module.__doc__) + "\n"
    ltw = ltw + "end note\n"
    ltw = ltw + "!endif\n"
    ltw = ltw + "@enduml\n\n"

    #print(ltw)
    # write file here mode
    tfn = targetpath + "/" + me_alias + ".puml"
    with open(tfn, "w") as fil:
        fil.write(ltw)




def py2pumla(fname, targetpath):
    basename = os.path.basename(fname)
    fullname = os.path.abspath(fname)
    #print("basename = " + basename)
    modulename = basename.split(".")[0]
    #print("modulename = " + modulename)
    #print(os.path.abspath(os.path.curdir))
    sys.path.append(os.path.abspath(os.path.curdir))
    sys.path.append(os.path.abspath(os.path.dirname(fullname)))
    #os.chdir(os.path.commonpath()fullname.)
    spec = spec_from_file_location(modulename, fullname)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = mod.__dict__
    keys = d.keys()
    mod_els = []
    module_element_alias = []
    module_funcs = []
    if (inspect.ismodule(mod)):
        #print(mod)
        #print("... is a module")
        pass
    for e in keys:
        if not "__" in e:
            mod_els.append(d[e])

    #print(mod_els)

    mymod_uses = ""
    mymod_func = ""
    for me in mod_els:
        #print(me.__dict__.keys())
        #print(dir(me))
        if (inspect.isclass(me)):
            #print("Class: ")
            #print(me)
            cl_alias = createClassPUMLCode(me, targetpath)
            module_element_alias.append(cl_alias)
        elif (inspect.ismodule(me)):
            #print(me)
            #print("... is a module used.")
            pass

        elif (inspect.isfunction(me)):
            #print(me)
            if (me.__code__.co_filename == mod.__file__):
                #print("... is my function.")
                me_name = me.__name__
                me_args = me.__code__.co_varnames
                mymod_func = mymod_func + "\t\t+" + str(me_name) + str(me_args).replace("'", "").replace(",)", ")") + "\n"
                module_funcs.append(me)

            else:
                #print("... is a function from: " + str(me.__module__))

                mod_alias = str(mod.__name__).lower() + "Module"
                relalias = "REL#" + mod_alias + "_USES_" + str(me.__name__) +"_FROM_" + str(me.__module__)
                mymod_uses = mymod_uses + 'PUMLARelation(' + mod_alias + ', "..>", ' + str(me.__module__) + ', "uses: ' + str(me.__name__) + '", "' + relalias + '")\n'

    mfc_alias = createModuleFunctionsPUMLCode(mod, module_funcs, targetpath)
    if ((not (mfc_alias == None)) and (not (mfc_alias == ""))):
        module_element_alias.append(mfc_alias)
    createModulePUMLCore(mod, fname, module_element_alias, mymod_func, mymod_uses, targetpath)


def findPythonFiles(path):
    """" find all pumla files in given path """
    pythonfiles = []
    blacklist = []

    blacklistfilename = path + "/pumla_blacklist.txt"
    #print(blacklistfilename)
    if (os.path.isfile(blacklistfilename)):
        #print("blacklist found\n")
        file = open(blacklistfilename)
        text = file.read()
        #print(text)
        file.close()
        for li in text.split():
            blacklist.append(path + li.strip("."))
        #print(blacklist)
    # walk through the file and folder structure
    # and put all PUMLA files into a list
    for dirpath, dirs, files in os.walk(path):
        for filename in files:
            if (not(isInBlacklist(dirpath, blacklist))):
                #print(dirpath)
                fname = os.path.join(dirpath, filename)
                # a PUMLA file must end with '.puml' (see Modelling Guideline)
                if fname.endswith('.py'):
                    pythonfiles.append(fname)

    return pythonfiles

def executePumla(gendir):
    cmd = "python3 " + pumla_path + "/pumla.py update"
    oldpath = os.path.abspath(os.curdir)
    os.chdir(gendir)
    os.system(cmd)
    os.chdir(oldpath)

def createAllElementsOverview(pumpath, targetpath):
    dtxt = "@startuml\n!include modelrepo_json.puml\n"
    dtxt = dtxt + "!include " + pumpath + "/pumla_macros.puml\n\n"
    dtxt = dtxt + "PUMLAPutAllElements()\nPUMLAPutAllStaticRelations()\n\n"
    dtxt = dtxt + "@enduml\n\n"

    tfn = targetpath + "/allElementsOverview.puml"
    with open(tfn, "w") as fil:
        fil.write(dtxt)

def parseSysArg(sysarg):
    """ parses the given command line arguments """
    # no parameter - default behaviour: show all pumla files in subdirs
    if (len(sysarg) == 1):
        pass
    elif (len(sysarg) == 2):
        pyfiles = findPythonFiles(sysarg[1])
        pumla_gen_dir = sysarg[1] + "/_generated_p2p_pumla"
        if (not(os.path.exists(pumla_gen_dir))):
            os.mkdir(pumla_gen_dir)
        for e in pyfiles:
            py2pumla(e, pumla_gen_dir)

        executePumla(pumla_gen_dir)
        createAllElementsOverview(pumla_path, pumla_gen_dir)

    else:
        print("too much arguments... only one path to search for python files, please.")


if __name__ == "__main__":
    identifyMe()
    parseSysArg(sys.argv)
