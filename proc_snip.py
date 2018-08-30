import sys
import os
import string

SNIP_EXT='.cuda-snips'
SNIP_LEX=2

def isword(s):    
    return s.isalnum() or s=='_'

def get_word(ed, x, y):
    if x==0: return None, 0, 0

    x0 = x
    while (x0>0) and isword(ed.get_text_substr(x0-1, y, x0, y)):
        x0-=1
    text1 = ed.get_text_substr(x0, y, x, y)

    x0 = x
    while isword(ed.get_text_substr(x0, y, x0+1, y)):
        x0+=1
    text2 = ed.get_text_substr(x, y, x0, y)

    return text1 + text2, len(text1), len(text2)

def _curent_word():
    s = ed.get_text_sel()
    nlen = len(s)
    if nlen <= 0:
        carets = ed.get_carets()
        if len(carets)!=1: return
        x0, y0, x1, y1 = carets[0]
        return         
    else:
        return ed.get_text_sel()


def get_last_word_from_editor(ed, char):
    if isword(char): return
    x, y, x1, y1 = ed.get_carets()[0]
    
    #selection? stop
    if y1>=0: return
    #check line index 
    if y>=ed.get_line_count(): return
    
    line = ed.get_text_line(y)
    if not line: return
    
    #caret after lineend? stop
    if x>len(line): return 
    
    x0=x            
    while (x>0) and (isword(line[x-1])): x-=1
    return line[x:x0]
    
def get_changed_word_from_editor(ed, caret=None):
    if caret:
        x0, y0, x1, y1 = caret
    else:
        x0, y0, x1, y1 = ed.get_carets()[0]
    word, len0, len2 = get_word(ed, x0, y0)
       
    if len2 == 0 and not caret: return None, 0, 0
    return word, len0, len2


def get_snip_list_of_dicts(dir, lex):
    res = []
    for root, subdirs, files in os.walk(os.path.join(dir, lex)):
        for f in files:
            if f.endswith(SNIP_EXT):
                res.append(os.path.join(root, f))

    result = []
    for fn in res:
        for s in open(fn, encoding='utf8').read().splitlines():
            if s and s[0] not in ('#', ' '):
                #print('s', '"'+s+'"')
                w = s.split(' ')
                if len(w)==2:
                    result += [ (w[0], w[1], lex) ]
    
    return sorted(result)
