# Python wrapper for TMAP7

## Setup your environment



![cmd1](\img\cmd1.png)

g77 is not recognized, but it is in TMAP7/bin. 



## Use  proper batch files to run

run this batch to execute TMAP7 run:

> `call g.bat`
>
> `call g.bat`
>
> `call t7 Origin`

Here `g.bat` sets up environment, `t7` stands for `t7.bat` and `Origin` stands for input file `Origin.inp`.

`g.bat`, forgot why, but everything works fine if it is called twice.

> SET OLDPATH=%PATH%
>
> PATH=c:\TMAP7\bin;c:\TMAP7;%PATH%
>
> SET LIBRARY_PATH=c:\tmap7\lib
>
> SET DIR=c:\TMAP7

t7.bat

> echo off
>
> del prepout
>
> del codeout
>
> del tape1
>
> del tape7.for
>
> del tmapinp
>
> copy %1.inp tmapinp
>
> tmapp7.exe
>
> if not exist tape7.for goto noeqn
>
> g77 -c tape7.for
>
> g77 tmapc7.o tape7.o
>
> goto execute
>
> :noeqn
>
> g77 tmapc7.o equ.o
>
> :execute
>
> a.exe
>
> del a.exe
>
> copy prepout+codeout %1.out
>
> copy pltdata %1.plt
>
> echo Task Complete!

### Compiling problems.

> g77 -c tape7.for
>
> g77 tmapc7.o tape7.o
>
> g77 tmapc7.o equ.o

All these files are in the source archive of TMAP7, `srcTMAP7.zip`.  Copy files if they are missing.

Run `t7.bat` with `echo on` to see where the problems are.

If g77 complains that crt1.o can't be open, means that `libc0-.1-dev` or `lib64` are missing. [StackOverflow: cannot find crt1.o](https://stackoverflow.com/questions/6329887/compiling-problems-cannot-find-crt1-o).

 