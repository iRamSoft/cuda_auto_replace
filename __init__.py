import shutil
from cudatext import *
from .proc_snip import *
                    
ini = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_auto_replace.ini')
ini0 = os.path.join(os.path.dirname(__file__), 'settings.sample.ini')

if os.path.isfile(ini0) and not os.path.isfile(ini):
    shutil.copyfile(ini0, ini)

#-------options-------
opt_allow_lexers = ini_read(ini, 'op', 'lexers', '*').lower().split(',')      
#---------------------
bad_chars = '~"#%&*:<>?/\\{|}.'
good_chars = '________________' 

 
def is_name_listed(name, namelist):
    if not namelist: return True
    return bool(name) and (','+name+',' in ','+namelist+',')
    
def get_lexer_dir(lex):
    trantab = str.maketrans(bad_chars, good_chars)
    return lex.translate(trantab)

def is_for_all_lexers():
    return opt_allow_lexers == [''] or opt_allow_lexers == ['*']

def _checks(ed_self):
    if len(ed_self.get_carets())!=1: return
    if is_for_all_lexers(): return True

    lexer = ed_self.get_prop(PROP_LEXER_FILE).lower() # _FILE works faster
    if lexer not in opt_allow_lexers: return 
        
    return True
    
class Command:
    def __init__(self):          
        self.do_load_snippets() 

    def do_load_snippets(self):     
        snips = []
        if is_for_all_lexers():
            lexers_all = lexer_proc(LEXER_GET_LEXERS, True)
        else:
            lexers_all = opt_allow_lexers
        
        for lex in lexers_all:
            dir = os.path.join(app_path(APP_DIR_DATA), 'autoreplace', get_lexer_dir(lex.lower()))
            snips.extend(get_snip_list_of_dicts(dir))

        lexers = []
        for d in snips:
            s = d[SNIP_LEX]
            if s:
                lexers += s.split(',')  
        lexers = sorted(list(set(lexers)))
        
        if is_for_all_lexers(): 
            print('Auto Replace works for lexers:', ', '.join(lexers))
        else:
            print('Auto Replace works for all lexers')

#       print('snips', snips)  

        self.snips_sort = {}

        for lexer in lexers_all:
            _items = [
                data for data in snips if
                (data[SNIP_LEX]=='') or
                is_name_listed(lexer.lower(), data[SNIP_LEX].lower())
                ]
            self.snips_sort[lexer.lower()] = _items

#       print('init', _items)   

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

    def replace_word_under_caret(self, ed_self):
        word, len0, len1  = get_changed_word_from_editor(ed_self)
#       print('word', word)
        rp_text = self.get_item_for_replace(word) 
#       print('rp_text', rp_text) 
        if not rp_text: return  
        x0, y0, x1, y1 = ed_self.get_carets()[0] 
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
        if not _checks(ed_self): return
        self.replace_last_word(ed_self, text)
        
    def on_change(self, ed_self):
        if not _checks(ed_self): return
        self.replace_word_under_caret(ed_self)
        return
        
    def on_key(self, ed_self, key, state):
        pass
            
    def on_click(self, ed_self, state):
        pass
            
    def config(self):
        res = dlg_input('Allowed lexers (comma-separated list, or "*" for all):', opt_allow_lexers_for_config)
        if not res: return
        ini_write(ini, 'op', 'lexers', res)
 