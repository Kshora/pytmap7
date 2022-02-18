import time as tm
import subprocess
import os
import numpy as np
from nt import times

t7outputfile = 'C:\TMAP7\Origin.plt'
outfile = 'C:\\TMAP7\\Origin.inp'
#tbat = 'C:\TMAP7\origin.bat'
tbat = 'C:\TMAP7\miura.bat'
cwd = "C:/TMAP7/"
#------------------------------------------------------------------------------ 
infile = 'template.inp'
pfile = 'pirani.dat'
testfit = "Data/testfit.txt"
testfitgoal = "Data/testfitgoal.txt"

def min_sec(t):
    def s(tt):
        if int(tt/10.) < 1:
            return "0%d"%(int(tt))
        else:
            return "%d"%(int(tt))
    hh,mm,ss = 0,0,0
    if int(t/60.) > 59:
        hh = int(t/3600.)
        mm = int((t - hh*3600)/60.)
        ss = int((t - hh*3600 - mm*60))
    else:
        mm = int(t/60.)
        ss = t - mm*60
    return "%s:%s:%s"%(s(hh),s(mm),s(ss))

def ltexp(exp,decplace = 1):
    ''' converts 1e29 float to the scientific notation LaTeX string '''
    exponent = int(np.floor(np.log10(abs(exp))))
    coeff = round(exp / np.float(10**exponent), decplace)
    return r"%s\times 10^{%d}"%(coeff,exponent)

def writePirani(waveform, pfile = pfile):
    ''' Output to txt T7 incident flux '''
    t,p = waveform
    with open(pfile,"w") as f:
        for i,item in enumerate(t):
            f.write("%.2f,%.4f\n"%(item,p[i]))

def runT7(ksubd,ku,kd,tstep = 0.7,pfile = pfile):
    ''' runs T7, using infile as template for T7 task, writes T7 directions to the 
    outfile. '''
    INPwrite(outfile,infile,pfile,tstep,ksubd,ku,kd)
    child = subprocess.Popen(tbat,
                             creationflags=subprocess.CREATE_NEW_CONSOLE,
                             stdout = open(os.devnull,'wb'),
                             shell = True,
                             cwd = cwd
                             )
    #creationflags = subprocess.CREATE_NEW_CONSOLE
    #show console 
    #stdout = open(os.devnull,'wb')
    #hide console
    streamdata = child.communicate()[0]
    rc = child.returncode
    data = np.loadtxt(t7outputfile, skiprows = 5) 
    t = data[:,0]
    gamma = data[:,2]
    return t,gamma 

def INPwrite(t7inpfile,templatefile,pfile,tstep,ksubd,ku,kd):
    ''' writes input file for T7 based on a template.
    looks into template for my keywords (commented for T7) and inserts 
    given values.'''
    with open(templatefile) as f:
        with open(t7inpfile,'w') as out:
            k,T,j,jt = 0,0,0,-1
            stag = ''
            tag = ['$enc1','$enc2']
            for line in f:
                if line.startswith('$pressure'):
                    line = line
                    out.write(line)
                    k += 1
                    if k<2: 
                        with open(pfile,'r') as pressure:
                            for pline in pressure:
                                out.write(
                                          "{0},{1}\n".format(
                                                             float(pline.split(',')[0]),
                                                             float(pline.split(',')[1])*ksubd
                                                              ))
                                T = float(pline.split(',')[0])+1
                            out.write('%.4f,0.0,end\n' % T)
                else:
                    if k == 2 or k == 0:
                        if line.startswith('timend'):
                            line = "timend=%.4f,end        $end of computations, sec\n" % T
                        if line.startswith('tstep'):
                            line = "tstep=%.4f,end            $time step, sec\n" % tstep
                        if line.startswith('$enc1'):
                            jt = j+1
                            stag = tag[0]
                        if j == jt:
                            if stag == tag[0]:
                                line = "difbcl=ratedep,encl,1,spc,h,exch,h2\nksubd,const,{:.2e},h,ksubr,const,{:.2e},end\n".format(ksubd,ku)

                            if stag == tag[1]:
                                line = "difbcr=ratedep,encl,2,spc,h,exch,h2\nksubd,const,{:.2e},h,ksubr,const,{:.2e},end \n".format(ksubd,kd) 
                                                 
                        if line.startswith('$enc2'):
                            jt = j+1
                            stag = tag[1]
                        out.write(line)
                j+=1
                
