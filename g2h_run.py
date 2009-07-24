#!/usr/bin/env python

import os.path,os,sys,ConfigParser
from Cheetah.Template import Template
import glimmer2html

# setup paths
template_dir = None
for p in ['template',os.path.join(os.environ['GLIMMER_PREFIX'],'share','glimmer2html')]:
    if os.path.exists(p):
        template_dir = p
        break
if template_dir == None:
    print 'Error, could not find template directory'
    sys.exit(1)

# loading initial configuration
config = ConfigParser.ConfigParser()
config.read(os.path.join(template_dir,'glimmer2html.cfg'))

config.read(sys.argv[1])
source = config.get('setup','source')
# setup output directory
outpath = sys.argv[2]
if os.path.exists(outpath):
    if not os.path.isdir(outpath):
        print 'Error, %s exists and is not a directory'%outpath
        sys.exit(1)
else:
    os.makedirs(outpath)
basename = os.path.join(outpath,config.get('setup','basename'))

index = glimmer2html.index(basename,config,'setup')
index.write()

for s in config.get('setup','sections').split():
    sectiontype = None
    if s in glimmer2html.handle_section:
        sectiontype = s
    else:
        try:
            t = config.get(s,'type')
        except:
            t = ''
        if t in glimmer2html.handle_section:
            sectiontype = t
    if sectiontype != None:
        tmpl = glimmer2html.handle_section[sectiontype](basename,config,s)
        tmpl.write()



