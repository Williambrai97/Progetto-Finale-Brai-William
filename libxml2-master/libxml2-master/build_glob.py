#! /usr/bin/env python
###
#
#       build_glob.py : Build the global_functions.h and global_functions.c
#                       files which are required to implement the user
#                       interface to global variables now that thread specific
#                       data (TSD) is used to emulate global state.
#
#       See Copyright for the status of this software.
#       Gary.Pennington@sun.com
###
import os, string

class globvar:
    def __init__(self, type, name):
        self.type=type
        self.name=name

def striplinesep(line):
    while line and line[-1] in ('\r','\n'):
        line = line[:-1]
    return line

def writeline(file, line=None):
    if line:
        file.write(line)
    file.write("\n")

if __name__ == "__main__":
    globals={}
    global_data=open("global.data").readlines()
    global_code=open("globals.c").readlines()
    global_hdr=open("include/libxml/globals.h").readlines()
    global_functions_hdr=open("include/libxml/globals.h", "w+")
    global_functions_impl=open("globals.c", "w+")

    #
    # Rebuild the beginning of the file up to the
    # Automatically generated string
    # 
    for line in global_hdr:
        line = striplinesep(line)
        if line == " * Automatically generated by build_glob.py.":
	    break
	writeline(global_functions_hdr, line)

    writeline(global_functions_hdr, " * Automatically generated by build_glob.py.")
    writeline(global_functions_hdr, " * Do not modify the previous line.")
    writeline(global_functions_hdr, " */")
    writeline(global_functions_hdr)

    for line in global_code:
        line = striplinesep(line)
        if line == " * Automatically generated by build_glob.py.":
	    break
	writeline(global_functions_impl, line)

    writeline(global_functions_impl, " * Automatically generated by build_glob.py.")
    writeline(global_functions_impl, " * Do not modify the previous line.")
    writeline(global_functions_impl, " */")
    writeline(global_functions_impl)

    # Now process the data and write it to the appropriate output file
    for line in global_data:
        if line[0]=='#':
            continue
        line = striplinesep(line)
        fields = string.split(line, ",")
        # Update the header file
        writeline(global_functions_hdr)
        global_functions_hdr.write("XMLPUBFUN "+fields[0]+" * XMLCALL ")
        if fields[2]:
            global_functions_hdr.write("(*")
        global_functions_hdr.write("__"+fields[1]+"(void)")
        if fields[2]:
            global_functions_hdr.write(")"+fields[2])
        writeline(global_functions_hdr,";")
        writeline(global_functions_hdr, "#ifdef LIBXML_THREAD_ENABLED")
        writeline(global_functions_hdr,"#define "+fields[1]+" \\")
        writeline(global_functions_hdr,"(*(__"+fields[1]+"()))")
        writeline(global_functions_hdr,"#else")
        if fields[2]:
            writeline(global_functions_hdr,"XMLPUBVAR "+fields[0]+" "+fields[1]+fields[2]+";")
        else:
            writeline(global_functions_hdr,"XMLPUBVAR "+fields[0]+" "+fields[1]+";")
        writeline(global_functions_hdr,"#endif")
        # set/get for per-thread global defaults
        if fields[3]:
            writeline(global_functions_hdr,"XMLPUBFUN "+fields[0]+" XMLCALL "+fields[1][:3]+"ThrDef"+fields[1][3:]+"("+fields[0]+" v);")
        # Update the implementation file
        writeline(global_functions_impl)
#        writeline(global_functions_impl, "extern "+fields[0]+" "+fields[1]+";")
        writeline(global_functions_impl, "#undef\t"+fields[1])
        writeline(global_functions_impl, fields[0]+" *")
        if fields[2]:
            global_functions_impl.write("(*")
        global_functions_impl.write("__"+fields[1]+"(void)")
        if fields[2]:
            writeline(global_functions_impl, ")[]")
        writeline(global_functions_impl, " {")
        writeline(global_functions_impl, "    if (IS_MAIN_THREAD)")
        writeline(global_functions_impl, "\treturn (&"+fields[1]+");")
        writeline(global_functions_impl, "    else")
        writeline(global_functions_impl, "\treturn (&xmlGetGlobalState()->"+fields[1]+");")
        writeline(global_functions_impl, "}")
        # set/get for per-thread global defaults
        if fields[3]:
            writeline(global_functions_impl,fields[0]+" "+fields[1][:3]+"ThrDef"+fields[1][3:]+"("+fields[0]+" v) {")
            writeline(global_functions_impl,"    "+fields[0]+" ret;");
            writeline(global_functions_impl,"    xmlMutexLock(xmlThrDefMutex);")
            writeline(global_functions_impl,"    ret = "+fields[1][:3]+fields[1][3:]+"ThrDef;")
            writeline(global_functions_impl,"    "+fields[1][:3]+fields[1][3:]+"ThrDef = v;")
            writeline(global_functions_impl,"    xmlMutexUnlock(xmlThrDefMutex);")
            writeline(global_functions_impl,"    return ret;")
            writeline(global_functions_impl,"}")
    # Terminate the header file with appropriate boilerplate
    writeline(global_functions_hdr)
    writeline(global_functions_hdr, "#ifdef __cplusplus")
    writeline(global_functions_hdr, "}")
    writeline(global_functions_hdr, "#endif")
    writeline(global_functions_hdr)
    writeline(global_functions_hdr, "#endif /* __XML_GLOBALS_H */")
