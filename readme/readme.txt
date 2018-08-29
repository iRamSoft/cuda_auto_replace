plugin for CudaText.
allows to auto-replace keywords/functions, when they are typed in the wrong case (e.g. "writeln" to "WriteLn"). allows usual word replace too. to use it, you must create one or several snippet collection(s) in .cuda-snips format:
http://wiki.freepascal.org/CudaText#Format_of_.cuda-snips

for ex, to replace words "readln" and "writeln" in lexer Pascal, create file "[CudaText dir]/data/autoreplace/pascal/mysnips.cuda-snips" with contents:

writeln WriteLn
readln ReadLn

word is replaced when user goes off this word: by Space, Tab, symbol chars, punctuation, Home/End, PageUp/PageDown, mouse click.

note that [CudaText dir] on Unix is "~/.cudatext".
note that you need subfolder in the lower case inside "data/autoreplace" folder.
plugin prints in the Console panel, that it actually has found some snippets, e.g. "Auto Replace: for all lexers: found Pascal[5]".
such snippet collections can be distributed as CudaText add-ons.
plugin gives configuration menu item: Options / Settings-plugins / Auto Replace / Config.

authors:
  Alexey T. (CudaText)
  Khomutov Roman (iRamSoft)
license: MIT
