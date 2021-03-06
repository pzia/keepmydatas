import sys, os
import zipfile
from lxml import etree

def get_epub_info(fname, forceMime = False):
    ns = {
        'n':'urn:oasis:names:tc:opendocument:xmlns:container',
        'pkg':'http://www.idpf.org/2007/opf',
        'dc':'http://purl.org/dc/elements/1.1/'
    }

    # prepare to read from the .epub file
    zip = zipfile.ZipFile(fname)
    
    mime = zip.read('mimetype')
    
    if mime != "application/epub+zip\n" and not forceMime:
        print mime
        return None
    

    # find the contents metafile
    txt = zip.read('META-INF/container.xml')
    tree = etree.fromstring(txt)
    cfname = tree.xpath('n:rootfiles/n:rootfile/@full-path',namespaces=ns)[0]

    # grab the metadata block from the contents metafile
    cf = zip.read(cfname)
    tree = etree.fromstring(cf)
    px = tree.xpath('/pkg:package/pkg:metadata',namespaces=ns)
    p = px[0]

    # repackage the data
    res = {}
    for s in ['title','language','creator','date','identifier']:
        r = p.xpath('dc:%s/text()'%(s),namespaces=ns)
        if len(r) > 0 :
            v = r[0]
        else :  
            v = ""
        res[s] = v

    return res

for fnam in sys.argv[1:]:
    r = get_epub_info(fnam)
    print(r)
    #os.rename(fnam, "%s - %s.pub" % (r['title'], r['creator']))
