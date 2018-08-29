plugin for CudaText.
allows to auto-replace keywords/functions, when they are typed in the wrong case (e.g. "writeln" to "WriteLn"). and general words replace too, of course. to use it, you must create one or several snippet collection in .cuda-snips format:
http://wiki.freepascal.org/CudaText#Format_of_.cuda-snips

for ex, to replace words "readln" and "writeln" in lexer Pascal, create file "CudaText/data/autoreplace/pascal/mysnips.cuda-snips" with contents:

writeln WriteLn
readln ReadLn

note that you need subfolder "pascal" in lower case inside "data/autoreplace" folder.

author: Alexey T. (CudaText), Khomutov Roman (iRamSoft)
license: MIT