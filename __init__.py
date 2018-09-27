from cudatext import *
from .proc_snip import *

ini = os.path.join(app_path(APP_DIR_SETTINGS), 'cuda_auto_replace.ini')

if not os.path.isfile(ini):
    ini_write(ini, 'op', 'lexers', '*')

#-------options-------
opt_allow_lexers_for_config = ini_read(ini, 'op', 'lexers', '*')
opt_allow_lexers            = opt_allow_lexers_for_config.split(',')
#---------------------
TRANTAB = str.maketrans(
    r'%*:<>?/\{|}',
    r'___________'
    )

def is_name_listed(name, namelist):
    if not namelist: return True
    return bool(name) and (','+name+',' in ','+namelist+',')

def get_lexer_dir(lex):
    return lex.translate(TRANTAB)

def is_for_all_lexers():
    return opt_allow_lexers in ([''], ['*'])

def is_a_comment(style, c_styles):
    return style.lower() in c_styles

def _caret_in_comment(ed_self, c_styles, caret):
    if not caret: return False
    x0, y0, x1, y1 = caret

    tkn_list = ed_self.get_token(TOKEN_LIST_SUB, y0, y0)
    if not tkn_list: return False
    for tkn in tkn_list:
        if tkn['x1'] <= x0 <= tkn['x2']:
            return is_a_comment(tkn['style'], c_styles)

class Command:
    last_caret = None

    def __init__(self):
        self.do_load_snippets()

    def _checks(self, ed_self):
        if not self.snips: return
        if len(ed_self.get_carets())!=1: return

        lexer = ed_self.get_prop(PROP_LEXER_FILE).lower()
        if not self.snips.get(lexer.lower()): return

        if _caret_in_comment(ed_self, self.lexer_prop.get(lexer.lower(), []),
            self.last_caret if self.last_caret else ed_self.get_carets()[0]):
            self.last_caret = ed_self.get_carets()[0]
            return

        return True

    def do_load_snippets(self):
        self.snips = {}

        if is_for_all_lexers():
            lexers_all = lexer_proc(LEXER_GET_LEXERS, True)
        else:
            lexers_all = opt_allow_lexers

        dir = os.path.join(app_path(APP_DIR_DATA), 'autoreplace')
        for lex in lexers_all:
            d = get_snips_for_lexer(dir, get_lexer_dir(lex.lower()))
            if d:
                self.snips[lex.lower()] = d

        lexers = sorted(self.snips.keys())
        lexers_ex = [lexer for lexer in lexers_all
                     if lexer.lower() in lexers]

        self.lexer_prop = {}
        for lexer in lexers_ex:
            props = lexer_proc(LEXER_GET_PROP, lexer)
            s_c_list = [item.lower() for item in props['st_s']]
            s_c_list.extend([item.lower() for item in props['st_c']])
            self.lexer_prop[lexer.lower()] = s_c_list

        if not self.snips:
            log_msg = 'Auto Replace: no snippets to work'
        else:
            msgs = ['{}[{}]'.format(lexer, len(self.snips.get(lexer.lower(), []))) for lexer in lexers_ex]
            if is_for_all_lexers():
                log_msg = 'Auto Replace: for all lexers, found: ' + ', '.join(msgs)
            else:
                log_msg = 'Auto Replace: works for lexers: ' + ', '.join(msgs)

        print(log_msg)

    def get_snip_list_current(self):
        lexer = ed.get_prop(PROP_LEXER_CARET).lower()
        return self.snips.get(lexer, [])

    def get_item_for_replace(self, word):
        items = self.get_snip_list_current() #leave snips for lexer
        items = [i for i in items if i[0].lower()==word.lower() and i[1]!=word] #leave snips for name
        if items:
            return items[0][1]

    def replace_word_under_caret(self, ed_self, caret=None):
        word, len0, len1  = get_changed_word_from_editor(ed_self, caret)
        if not word: return
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
        if not word: return
#       print('word', word)
        rp_text = self.get_item_for_replace(word)
#       print('rp_text', rp_text)
        if not rp_text: return

        x0, y0, x1, y1 = ed_self.get_carets()[0]
        ed_self.replace(x0-len(word), y0, x0, y0, rp_text)

    def on_insert(self, ed_self, text):
        if not self._checks(ed_self): return
        self.last_caret = ed_self.get_carets()[0]
        self.replace_last_word(ed_self, text)

    def on_change(self, ed_self):
        if not self._checks(ed_self): return
        self.replace_word_under_caret(ed_self)
        self.last_caret = ed_self.get_carets()[0]

    def on_key(self, ed_self, key, state):
        # key is checked via install.inf
        if state: return
        if not self._checks(ed_self):
            #print('on_key not check')
            return
        #print('on_key for caret:', self.last_caret)
        self.replace_word_under_caret(ed_self, self.last_caret)

    def on_click(self, ed_self, state):
        if not self._checks(ed_self): return
        if self.last_caret != ed_self.get_carets()[0]:
            self.replace_word_under_caret(ed_self, self.last_caret)
        self.last_caret = ed_self.get_carets()[0]

    def config(self):
        global opt_allow_lexers
        global opt_allow_lexers_for_config

        res = dlg_input('Allowed lexers (comma-separated list, or "*" for all):',
            opt_allow_lexers_for_config)
        if not res: return
        if opt_allow_lexers == res.lower().split(','):
            msg_status('Auto Replace: List of lexers not changed')
            return

        ini_write(ini, 'op', 'lexers', res)

        opt_allow_lexers_for_config = res
        opt_allow_lexers            = opt_allow_lexers_for_config.split(',')

        self.do_load_snippets()

    def reload_snips(self):
        self.do_load_snippets()

    def on_start(self, ed_self):
        pass
