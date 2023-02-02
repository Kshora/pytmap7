import subprocess
import os
import numpy as np


def writePirani(waveform, pfile):
    """Output to txt T7 incident flux"""
    t, pressure = waveform
    with open(pfile, "w") as f:
        for t, p in zip(t, pressure):
            f.write(f"{t:.2f},{p:.4f}\n")


class TmapTask:
    """
    Define Tmap7 parameters, prep for exectution, run.
    """

    t7_outputfile = "C:\TMAP7\Origin.plt"
    t7_instructions = "C:\\TMAP7\\Origin.inp"  # TMAP7 run instructions
    # tbat = 'C:\TMAP7\origin.bat'
    tbat = "C:\TMAP7\miura.bat"
    cwd = "C:/TMAP7/"
    # ------------------------------------------------------------------------------
    infile = "template.inp"
    pfile = "pirani.dat"  # incident atomic flux waveform data
    testfit = "Data/testfit.txt"
    testfitgoal = "Data/testfitgoal.txt"

    def __init__(self, basepath=".") -> None:
        self.basepath = os.path.abspath(basepath)
        self.update_path()

    def update_path(self):
        """
        Update paths to infile, pfile, testfit, testfitgoal
        """
        self.infile = os.path.join(self.basepath, self.infile)
        self.pfile = os.path.join(self.basepath, self.pfile)

    def prep_parameters(self, parameters,template):
        """Populate T7 parameters"""
        self.parameters = parameters
        self.template = template

    def run(self):
        """run"""
        self.write_t7_instructions()
        self.run_t7()

    def run_t7(self):
        """
        runs T7, using infile as template for T7 task, writes T7 instructions to 
        t7_instructions.
        """

        child = subprocess.Popen(
            self.tbat,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            stdout=open(os.devnull, "wb"),
            shell=True,
            cwd=self.cwd,
        )
        # creationflags = subprocess.CREATE_NEW_CONSOLE
        # show console
        # stdout = open(os.devnull,'wb')
        # hide console
        print("run finished")
        streamdata = child.communicate()[0]
        rc = child.returncode
        data = np.loadtxt(self.t7_outputfile, skiprows=5)
        t = data[:, 0]
        gamma = data[:, 2]
        self.data = data
        self.t = t
        self.gamma = gamma

    def write_t7_instructions(self, silent=True):
        """
        Writes input file for T7 based on a template.
        looks into template for my keywords (commented for T7) and inserts 
        given values.
        """
        ksubd = float(self.parameters["ksubd"]) if self.parameters["ksubd"]!=False else False
        ku = float(self.parameters["ku"]) if self.parameters["ku"]!=False else False
        kd = float(self.parameters["kd"]) if self.parameters["kd"]!=False else False
        dif = float(self.parameters["dif"]) if self.parameters["dif"]!=False else False
        temp = float(self.parameters["temp"]) if self.parameters["temp"]!=False else False
        tstep = float(self.parameters["tstep"]) if self.parameters["tstep"]!=False else False

        if not silent:
            print(f"template:\t{self.template}\ninstructions\t{self.t7_instructions}")
        with open(self.template) as f:
            with open(self.t7_instructions, "w") as out:
                k, T, j, jt = 0, 0, 0, -1
                stag = ""
                tag = ["$enc1", "$enc2","$eq1","$eq2"]
                for line in f:
                    if line.startswith("$pressure"):
                        line = line
                        out.write(line)
                        k += 1
                        if k < 2:
                            with open(self.pfile, "r") as pressure:
                                for pline in pressure:
                                    out.write(
                                        "{0},{1}\n".format(
                                            float(pline.split(",")[0]), float(pline.split(",")[1]) * ksubd
                                        )
                                    )
                                    T = float(pline.split(",")[0]) + 1
                                out.write("%.4f,0.0,end\n" % T)
                    else:
                        if k == 2 or k == 0:
                            if line.startswith("  etemp") and temp!=False:
                                line = f"  etemp=const,{temp},end\n"
                            if line.startswith("  tempd") and temp!=False:
                                line = f"  tempd=52*{temp},end $initial temperature distribution between the nodes\n"
                            if line.startswith("timend"):
                                line = "timend=%.4f,end        $end of computations, sec\n" % T
                            if line.startswith("tstep"):
                                line = "tstep=%.4f,end            $time step, sec\n" % tstep
                            if line.startswith("$enc1"):
                                jt = j + 1
                                stag = tag[0]
                            if j == jt:
                                if stag == tag[0]:
                                    if ku != False:
                                        line = "difbcl=ratedep,encl,1,spc,h,exch,h2\nksubd,const,{:.2e},h,ksubr,const,{:.2e},end\n".format(
                                            ksubd, ku
                                        )
                                    else:
                                        line = "difbcl=ratedep,encl,1,spc,h,exch,h2\nksubd,const,{:.2e},h,ksubr,equ,3,end\n".format(
                                            ksubd
                                        )

                                if stag == tag[1]:
                                    if kd != False:
                                        line = "difbcr=ratedep,encl,2,spc,h,exch,h2\nksubd,const,{:.2e},h,ksubr,const,{:.2e},end \n".format(
                                            ksubd, kd
                                        )
                                    else:
                                        line = "difbcr=ratedep,encl,2,spc,h,exch,h2\nksubd,const,{:.2e},h,ksubr,equ,4,end \n".format(
                                            ksubd
                                        )                                
                                if stag == tag[2]:
                                    line = f"y={temp}+0.0*time,end\n"
                                if stag == tag[3]:
                                    line = f"y={dif},end\n"

                            if line.startswith("$enc2"):
                                jt = j + 1
                                stag = tag[1]
                            if line.startswith("$eq1") and temp!=False:
                                jt = j + 1
                                stag = tag[2]
                            if line.startswith("$eq2") and dif != False:
                                jt = j + 1
                                stag = tag[3]
                                


                            out.write(line)
                    j += 1

    def plot(self):
        """Plot T7 result"""
        import matplotlib.pyplot as plt

        t = self.data[:, 0]
        permeated = self.data[:, 2]
        returned = -self.data[:, 1]

        plt.plot(t, permeated, label="permeated")
        plt.plot(t, returned, "--", label="returned")
        plt.legend(loc=1, bbox_to_anchor=[1, 1.2])
