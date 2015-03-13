#!/usr/bin/python                                                                                                                                                     
import magic
import sys
m = magic.open(magic.MIME_TYPE)
m.load()
for f in sys.argv[1:]:
    try : 
        print(f,  m.file(f))
    except :
        print("Except with %s" % f)
