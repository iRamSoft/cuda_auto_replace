from cudatext import *
from .proc_snip import *
                    
ini = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_auto_replace.ini')

if not os.path.isfile(ini):
    ini_write(ini, 'op', 'lexers', '*')

#-------options-------
opt_allow_lexers_for_config = ini_read(ini, 'op', 'lexers', '*')
opt_allow_lexers            = opt_allow_lexers_for_config.split(',')
opt_allow_lexers_check      = opt_allow_lexers_for_config.lower().split(',')
#---------------------
bad_chars  = '~"#%&*:<>?/\\{|}.'
good_chars = '________________' 
trantab    = str.maketrans(bad_chars, good_chars)
 
no_snips   = True
 
def is_name_listed(name, namelist):
    if not namelist: return True
    return bool(name) and (','+name+',' in ','+namelist+',')
    
def get_lexer_dir(lex):
    return lex.translate(trantab)

def is_for_all_lexers():
    return opt_allow_lexers == [''] or opt_allow_lexers == ['*']

def is_not_a_comment(style):
    return style.lower() not in ['string','comment']

def _caret_in_comment(ed_self, caret):
    if not caret: return False 
    x0, y0, x1, y1 = caret
    
    tkn_list = ed_self.get_token(TOKEN_LIST_SUB, y0, y0)
    if not tkn_list: return False    
    for tkn in tkn_list:
        if tkn['x1'] <= x0 <= tkn['x2']: 
            return not is_not_a_comment(tkn['style'])

def _checks(self, ed_self):    
    if no_snips: return
    if len(ed_self.get_carets())!=1: return
    if is_for_all_lexers(): return True

    lexer = ed_self.get_prop(PROP_LEXER_FILE).lower() # _FILE works faster

    if lexer not in opt_allow_lexers_check: return 
    if len(self.snips_sort.get(lexer.lower(), [])) == 0: return
      
    if _caret_in_comment(ed_self, self.last_carret_pos if self.last_carret_pos else ed_self.get_carets()[0]):
        self.last_carret_pos = ed_self.get_carets()[0]
        return  
        
    return True
    
class Command:
    last_carret_pos = None   
    on_key_process  = False 
    
    def __init__(self):          
        self.do_load_snippets() 

    def do_load_snippets(self):     
        global no_snips
        
        snips = []
        if is_for_all_lexers():
            lexers_all = lexer_proc(LEXER_GET_LEXERS, True)
        else:
            lexers_all = opt_allow_lexers
        
        for lex in lexers_all:
            dir = os.path.join(app_path(APP_DIR_DATA), 'autoreplace')
            snips.extend(get_snip_list_of_dicts(dir, get_lexer_dir(lex.lower())))

        lexers = []
        for d in snips:
            s = d[SNIP_LEX]
            if s:
                lexers += s.split(',')  
        lexers = sorted(list(set(lexers)))
        
        lexers_ex = [lexer for lexer in lexers_all
                     if lexer.lower() in lexers]

        self.snips_sort = {}

        for lexer in lexers_all:
            _items = [
                data for data in snips if
                (data[SNIP_LEX]=='') or
                is_name_listed(lexer.lower(), data[SNIP_LEX].lower())
                ]
            self.snips_sort[lexer.lower()] = _items

        no_snips = len(lexers_ex) == 0;

        msgs = ['{}[{}]'.format(lexer, len(self.snips_sort.get(lexer.lower(), []))) for lexer in lexers_ex]

        if no_snips:
            log_msg = 'Auto Replace: not found any snippets for work.'
        else:
            if is_for_all_lexers(): 
                log_msg = 'Auto Replace: for all lexers, found: ' + ', '.join(msgs)
            else:
                log_msg = 'Auto Replace: works for lexers: ' + ', '.join(msgs)
            
        print(log_msg)    

    def get_snip_list_current(self):
        lexer = ed.get_prop(PROP_LEXER_CARET).lower()
        return self.snips_sort.get(lexer, [])

    def get_item_for_replace(self, word):
        if not word: return  
        items = self.get_snip_list_current() #leave snips for lexer
#       print('items', items)
        items = [i for i in items if i[SNIP_TEXT][0].lower()==word.lower() and i[SNIP_TEXT][0]!=word] #leave snips for name
#       print('items', items) 
        if not items: return
        return items[0][SNIP_TEXT][0] 

    def replace_word_under_caret(self, ed_self, caret=None):
        word, len0, len1  = get_changed_word_from_editor(ed_self, caret)
#       print('word', word)
        rp_text = self.get_item_for_replace(word) 
#       print('rp_text', rp_text) 
        if not rp_text: return  
        if not caret:
            x0, y0, x1, y1 = ed_self.get_carets()[0]
        else:
            x0, y0, x1, y1 = caret     
        ed_self.replace(x0-len0, y0, x0+len1, y0, rp_text)
        
    def replace_last_word(self, ed_self, text):
        word = get_last_word_from_editor(ed_self, text)
#       print('word', word)
        rp_text = self.get_item_for_replace(word) 
#       print('rp_text', rp_text) 
        if not rp_text: return

        x0, y0, x1, y1 = ed_self.get_carets()[0] 
        ed_self.replace(x0-len(word), y0, x0, y0, rp_text)

    def on_insert(self, ed_self, text):
        if not _checks(self, ed_self): return
        self.last_carret_pos = ed_self.get_carets()[0]
        self.replace_last_word(ed_self, text)
        
    def on_change(self, ed_self):
        if not _checks(self, ed_self): return
        self.replace_word_under_caret(ed_self)
        self.last_carret_pos = ed_self.get_carets()[0]        
        
    def on_key(self, ed_self, key, state):
        #Tab=9 Enter=13 PgUp=33 PgDn=34 End=35 Home=36
        if key not in [9,13,33,34,35,36]: return
        if state!='': return
        if not _checks(self, ed_self): return
        if self.on_key_process: 
            print('Dbl on_key hooked!')
            return
        self.on_key_process = True
        self.replace_word_under_caret(ed_self, self.last_carret_pos)        
        self.on_key_process = False
            
    def on_click(self, ed_self, state):
        if not _checks(self, ed_self): return        
        if self.last_carret_pos != ed_self.get_carets()[0]:
            self.replace_word_under_caret(ed_self, self.last_carret_pos)
        self.last_carret_pos = ed_self.get_carets()[0]        
            
    def config(self):
        global opt_allow_lexers 
        global opt_allow_lexers_for_config
        global opt_allow_lexers_check
        
        res = dlg_input('Allowed lexers (comma-separated list, or "*" for all):', 
            opt_allow_lexers_for_config)
        if not res: return
        if opt_allow_lexers == res.lower().split(','): 
            msg_status('Auto Replace: List of lexers not changed')
            return

        ini_write(ini, 'op', 'lexers', res)
        
        opt_allow_lexers_for_config = res
        opt_allow_lexers            = opt_allow_lexers_for_config.split(',')    
        opt_allow_lexers_check      = opt_allow_lexers_for_config.lower().split(',')
        
        self.do_load_snippets()            
        
    def reload_snips(self):
        self.do_load_snippets()  
       
    def on_start(self, ed_self):
        pass