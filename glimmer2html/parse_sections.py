__all__ = ['index','snapshots','profiles','rsl','handle_section']

import os.path,os
from Cheetah.Template import Template
import plotcommand

class section(object):
    """Base class for a section"""

    def __init__(self,basename,config,sctn,):

        self.template_dir = None
        for p in ['template',os.path.join(os.environ['GLIMMER_PREFIX'],'share','glimmer2html')]:
            if os.path.exists(p):
                self.template_dir = p
                break
        if self.template_dir == None:
            raise RuntimeError,'Error, could not find template directory'
        self.template = Template(file=os.path.join(self.template_dir,self.template_name))
        self.config = config
        self.sctn = sctn

        # set title
        self.title = self.get_option(sctn,'title')
        self.basename = basename

        #source
        self.source = self.config.get('setup','source')

        # plot width
        w = self.get_option([sctn,'setup'],'plotwidth')
        if w!=None:
            self.plotwidth = '--width=%s'%w
        else:
            self.plotwidth = ''

        # setup template
        self.template.run = self.config.get('setup','title')
        self.template.title = self.title
        # setup navigation bar
        nav = []
        sections = self.config.get('setup','sections').split()
        for i in range(0,len(sections)):
            s = sections[i]
            nav.append({'name':s,'link':os.path.basename(self.outname(s))})
        self.template.nav = nav

    def outname(self,sctn):
        """Return output filename given section title"""
        return '%s_%s.html'%(self.basename,sctn)    

    def get_option(self,sctn,optionname):
        """Look up optionname in section, if not there look in default"""

        if type(sctn) == list:
            sections = sctn
        else:
            sections = [sctn]
        sections.append(self.section_type)
        for i in range(0,len(sections)):
            if self.config.has_option(sections[i],optionname):
                return self.config.get(sections[i],optionname)

    def write(self):
        """Write HTML results"""

        outfile = open(self.outname(self.sctn),'w')
        outfile.write(str(self.template))
        outfile.close()

class index(section):
    """Class for generating index page."""

    def __init__(self,basename,config,sctn,):

        self.section_type = 'index'
        self.template_name = 'index.tmpl'
        section.__init__(self,basename,config,sctn)

        self.template.description = self.config.get('setup','description')

    def write(self):
        """Write HTML results"""

        outfile = open(os.path.join(os.path.dirname(self.basename),'index.html'),'w')
        outfile.write(str(self.template))
        outfile.close()
            
class snapshots(section):
    """Class for displaying snapshots."""

    def __init__(self,basename,config,sctn):

        self.section_type = 'snapshots'
        self.template_name = 'snapshots.tmpl'

        section.__init__(self,basename,config,sctn)

        # setting up variables            
        self.variables = self.get_option(sctn,'variables').split()

        self.setup_layout()
        self.setup_plots()
        self.create_html()        

    def setup_layout(self):
        """setup layout of plots"""

        # check if we should animate plot
        anim = self.get_option(self.sctn,'animate')
        if anim != None:
            self.animate = anim.lower() in ['t','true','1']
        else:
            self.animate = False
        self.anim_range=[]
        t = self.get_option(self.sctn,'anim_start')
        if t!=None:
            self.anim_range.append(int(t))
        else:
            self.anim_range.append(0)
        t = self.get_option(self.sctn,'anim_end')
        if t!=None:
            self.anim_range.append(int(t))
        else:
            self.anim_range.append(5)
                
        self.times = self.get_option(self.sctn,'times')
        if self.times == "None":
            self.times = [None]
        else:
            self.times = self.times.split()
            
        if len(self.variables)>1:
            self.numdata = len(self.variables)
        else:
            self.numdata = len(self.times)
        try:
            self.numcol = int(self.get_option(self.sctn,'ncol'))
        except:
            self.numcol = self.numdata
        if len(self.variables)>1:
            self.numrow = len(self.times)
        else:
            self.numrow = 1
        
    def setup_plots(self):
        """setup plotting commands"""

        depends = self.get_option(self.sctn,'depends')
        if depends == None:
            depends = ''
        
        self.plots = {}
        for v in self.variables:
            plot = plotcommand.plot('%s_%s'%(self.basename,v),[self.source],depends.split())
            com = '%s -v%s'%(self.get_option(self.sctn,'plotcommand'),v)
            extra = self.get_option(self.sctn,v)
            if extra != None:
                com = '%s %s'%(com,extra)
            plot.plot_command = '%s %s'%(com,self.plotwidth)
            plot.convert_options = self.get_option(self.sctn,'convertargs')
            plot.thumb_size = int(self.get_option(self.sctn,'thumb_size'))

            # setup animation
            if self.animate:
                fps = self.get_option(self.sctn,'anim_fps')
                if fps != None:
                    plot.avi_fps = int(fps)
                asize = self.get_option(self.sctn,'anim_size')
                if asize != None:
                    plot.avi_size = int(asize)
            
            self.plots[v] = plot

    def create_html(self):
        """create HTML page."""
        rows = []
        if len(self.variables) > 1:
            for t in self.times:
                col = []
                for v in self.variables:
                    s = {}
                    s['ps']   = os.path.basename(self.plots[v].plotps(time=t))
                    s['png']  = os.path.basename(self.plots[v].plotpng(time=t))
                    s['thumb']= os.path.basename(self.plots[v].plotthumb(time=t))
                    s['title']= '%s, %ska'%(v,t)
                    if len(rows)==0:
                        if self.animate:
                            s['anim'] = os.path.basename(self.plots[v].anim(time=self.anim_range))
                    col.append(s)
                rows.append(col)
        else:
            col = []
            v = self.variables[0]
            for t in self.times:
                s = {}
                s['ps']   = os.path.basename(self.plots[v].plotps(time=t))
                s['png']  = os.path.basename(self.plots[v].plotpng(time=t))
                s['thumb']= os.path.basename(self.plots[v].plotthumb(time=t))
                s['title']= '%s, %ska'%(v,t)
                if len(col)==0:
                    if self.animate:
                        s['anim'] = os.path.basename(self.plots[v].anim(time=self.anim_range))
                col.append(s)
            rows.append(col)


        self.template.data  = rows
        self.template.times = self.times
        self.template.numrow = self.numrow
        self.template.numcol = self.numcol
        self.template.numdata = self.numdata

class profiles(snapshots):
    """Class for displaying profiles."""

    def __init__(self,basename,config,sctn):

        self.section_type = 'profiles'
        self.template_name = 'snapshots.tmpl'

        section.__init__(self,basename,config,sctn)

        # should be plot profile locations
        locs = self.get_option(self.sctn,'plotlocation')
        if locs != None:
            self.plotlocation = locs.lower() in ['t','true','1']
        else:
            self.plotlocation = False


        # setting up variables
        profiles = self.get_option(sctn,'profiles').split()
        if self.plotlocation:
            self.variables = ['locations']
        else:
            self.variables = []
        self.variables = self.variables+profiles

        self.setup_layout()
        self.setup_plots()
        self.create_html()        

    def setup_plots(self):
        """setup plotting commands"""

        self.plots = {}
        basic_plot = self.get_option(self.sctn,'plotcommand')
        # check whether we should plot profile locations
        first_prof = 0
        if self.plotlocation:
            first_prof = 1
            # get names of profiles
            profstring = ''
            for p in self.variables[first_prof:]:
                profile = self.get_option(self.sctn,'%s_prof'%p)
                if profile==None:
                    print 'Warning, no profile definition for profile %s'%v
                    continue
                profstring = '%s -p%s'%(profstring,profile)
            plot = plotcommand.plot('%s_ploc'%(self.basename),[self.source])
            plot.plot_command = '%s %s %s'%(self.get_option(self.sctn,'plotloc_command'),self.plotwidth,profstring)
            
            plot.convert_options = self.get_option(self.sctn,'plotloc_convert')
            plot.thumb_size = int(self.get_option(self.sctn,'thumb_size'))
            self.plots['locations'] = plot
            
        for v in self.variables[first_prof:]:
            profile = self.get_option(self.sctn,'%s_prof'%v)
            if profile==None:
                print 'Warning, no profile definition for profile %s'%v
                continue
            prof_extra = self.get_option(self.sctn,'%s_extra'%v)
            if prof_extra==None:
                prof_extra = ''
            plot = plotcommand.plot('%s_%s'%(self.basename,v),[self.source],[profile])
            plot.plot_command = '%s -p%s %s'%(basic_plot,profile,prof_extra)
            plot.convert_options = self.get_option(self.sctn,'convertargs')
            plot.thumb_size = int(self.get_option(self.sctn,'thumb_size'))
            # setup animation
            if self.animate:
                fps = self.get_option(self.sctn,'anim_fps')
                if fps != None:
                    plot.avi_fps = int(fps)
                asize = self.get_option(self.sctn,'anim_size')
                if asize != None:
                    plot.avi_size = int(asize)

            self.plots[v] = plot
        
class rsl(section):
    """Class for displaying RSL curves."""

    def __init__(self,basename,config,sctn):

        self.section_type = 'RSL'
        self.template_name = 'rsl.tmpl'

        section.__init__(self,basename,config,sctn)

        TITLES = {'rsl':'relative sea-level curves',
                  'hist':'time dependent histograms of RSL residuals',
                  'res':'distribution of mean RSL residuals'}

        self.rslplots = ['rsl','hist','res']

        rsldb = self.get_option(sctn,'rsldb')
        if rsldb != "":
            rsldb = "-r %s"%rsldb

        self.plots = {}
        for r in self.rslplots:
            plot = plotcommand.plot('%s_%s'%(basename,r),[self.source])
            com = '%s %s'%(self.get_option(sctn,'%scommand'%r),rsldb)
            plot.plot_command = com
            cargs = self.get_option(sctn,'%sconvert'%r)
            if cargs==None:
                cargs = ''
            plot.convert_options = cargs
            plot.thumb_size = int(self.get_option(sctn,'thumb_size'))

            self.plots[r] = plot

        # create plots
        rsl = {}
        for r in self.rslplots:
            rsl[r] = {}
            rsl[r]['ps'] = os.path.basename(self.plots[r].plotps())
            rsl[r]['png'] = os.path.basename(self.plots[r].plotpng())
            rsl[r]['thumb'] = os.path.basename(self.plots[r].plotthumb())
            rsl[r]['title'] = TITLES[r]

        # filling template
        self.template.rsl = self.rslplots
        self.template.numr = len(self.rslplots)
        self.template.rslplots = rsl


        
handle_section = {'snapshots':snapshots,
                  'RSL':rsl,
                  'profiles':profiles}
