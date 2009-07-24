__all__ = ['plot']
    
import os, os.path

def isolder(target, sources):
    """Check if target is older than sources.

    sources: list of paths to check
    target: single path. if target does not exist return True."""

    if not os.path.exists(target):
        return True
    tage = os.path.getmtime(target)

    for p in sources:
        if os.path.getmtime(p) > tage:
            return True
    return False

class plot(object):

    def __init__(self,basename,sources,depends=[]):

        self.plot_command = 'plotCFvar.py --land -cthk -vis'
        self.convert_options = ''
        self.thumb_size = 300
        self.depends = sources+depends
        self.sources = ''
        for s in sources:
            self.sources = '%s %s'%(self.sources,s)
        self.bname = basename
        self.test = False
        self.avi_fps = 25
        self.avi_size = None

    def execute(self,command):
        if self.test:
            print command
        else:
            os.system(command)

    def basename(self,time=None):
        """Return basename modified for time."""

        if time==None:
            return self.bname
        else:
            return '%s.%s'%(self.bname,str(time))

    def plotps(self, time=None):
        """Create postscript file if it needs updating and return output filename"""
        outps = '%s.ps'%self.basename(time)
        if isolder(outps,self.depends):
            print 'Creating %s'%outps
            run_command = '%s '%self.plot_command
            if time!=None:
                run_command = '%s -t%s'%(run_command,str(time))
            run_command = '%s %s %s'%(run_command,self.sources,outps)
            self.execute(run_command)
        return outps

    def plotpng(self, time=None):
        """Create full sized png from ps and return output filename."""
        outpng = '%s.png'%self.basename(time)
        outps = self.plotps(time=time)
        if isolder(outpng,[outps]):
            print 'Creating %s'%outpng
            self.execute('convert -trim %s %s %s'%(self.convert_options,outps,outpng))
        return outpng

    def plotthumb(self,time=None):
        """Create thumbnail from ps and return output filename."""
        outthumb = '%s-thumb.png'%self.basename(time)
        outps = self.plotps(time=time)
        if isolder(outthumb,[outps]):
            print 'Creating %s'%outthumb
            self.execute('convert -trim %s -size %d %s -resize %d %s'%(self.convert_options,self.thumb_size,outps,self.thumb_size,outthumb))
        return outthumb

    def anim(self,time=[0,5]):
        """Create an avi animation using plotcommand and return output filename."""
        outavi = '%s.avi'%self.basename()
        if isolder(outavi,self.depends):
            print 'Creating %s'%outavi
            run_command = '%s '%self.plot_command
            run_command = '%s %s '%(run_command,self.sources)
            if self.avi_size==None:
                avisize=""
            else:
                avisize="-s%d"%self.avi_size
            if self.convert_options=='':
                conv_options = ''
            else:
                conv_options = ' --convert_options \"%s\"'%self.convert_options
            avi_command = "make_anim.py %s -o %s -f %d -t%d %d %s \"%s\""%(avisize,outavi,self.avi_fps,time[0],time[1],conv_options,run_command)
            self.execute(avi_command)
        return outavi


    
