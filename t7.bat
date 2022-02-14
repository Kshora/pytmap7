echo off
del prepout
del codeout
del tape1
del tape7.for
del tmapinp
copy %1.inp tmapinp
tmapp7.exe
if not exist tape7.for goto noeqn
g77 -c tape7.for
g77 tmapc7.o tape7.o
goto execute
:noeqn
g77 tmapc7.o equ.o
:execute
a.exe
Rem del a.exe
copy prepout+codeout %1.out
copy pltdata %1.plt
echo Task Complete, Arseny!
