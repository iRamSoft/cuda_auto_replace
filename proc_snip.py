import sys
import os
import string

SNIP_EXT='.cuda-snips'

def isword(s):    
    return s.isalnum() or s=='_'

def get_word(ed, x, y):

    if x<=0:
        return None, 0, 0
        
    s = ed.get_text_line(y)
    if not s or x>=len(s):
        return None, 0, 0

    x0 = x
    while (x0>0) and isword(s[x0-1]):
        x0 -= 1
    s1 = s[x0:x]

    x1 = x
    while (x1<len(s)) and isword(s[x1]):
        x1 += 1
    s2 = s[x:x1]

    return s1+s2, len(s1), len(s2)

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


def get_snips_for_lexer(dir, lex):
    res = []
    for root, subdirs, files in os.walk(os.path.join(dir, lex)):
        for f in files:
            if f.endswith(SNIP_EXT):
                res.append(os.path.join(root, f))

    r = []
    for fn in res:
        for s in open(fn, encoding='utf8').read().splitlines():
            if s and s[0] not in ('#', ' '):
                #print('s', '"'+s+'"')
                w = s.split(' ')
                if len(w)==2:
                    r.append(w)
    
    return sorted(r)
