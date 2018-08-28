import re

def parse_snip_line(line, lex):
    """ Parse one-line snippet definition
            [word ][/L="My Lexer"] [/N="My Name"] text text
        If word is omitted then /N= is required.
        Quotes around lexer/name are required if value has blanks.
        Text part can has \t \n \r \\ to include chr(9) chr(10) chr(13) and '\' .
        Minimum line need to have two words or /N=name and text .
        Return
            {'id'  :'word',
             'name':'My Name',  # 'name':'word' if no /N= in line
             'lex' :'My Lexer', # 'lex' :''     if no /L= in line
             'text':['text text']
            }
    """
    if len(line.split()) < 2:
        return None

    key     = line.split()[0]   if  line[:3] not in ('/N=', '/L=') else ''
    line    = line[len(key):].lstrip()
                
    def opt_val(line, opt, defv):
        optv    = defv
        opt     = opt if opt[0]=='/' else '/'+opt+'='
        mtch= re.match(opt+r'("[^"]+")', line)
        if mtch:
            optv    = mtch.group(1)
            line    = line.replace(opt+optv, '').lstrip()
            optv    = optv.strip('"')
        else:
            mtch= re.match(opt+r'(\S+)', line)
            if mtch:
                optv    = mtch.group(1)
                line    = line.replace(opt+optv, '').lstrip()
        return optv,line
                
    name    = key
    lex_ex  = ''
    if line[:3]=='/N=':
        name,line   = opt_val(line, 'N', defv=key)
    if line[:3]=='/L=':
        lex_ex,line = opt_val(line, 'L', defv='')
    if line[:3]=='/N=':
        name,line   = opt_val(line, 'N', defv=name)

    if not key and not name:
        return None
                
    body    = line.lstrip()
    body    = body.replace('\\\\', chr(0))
    body    = body.replace('\\t', chr(9)).replace('\\n', chr(10)).replace('\\r', chr(13))
    body    = body.replace(chr(0), '\\')

    if not body:
        return None

    return {'id':key, 'name':name, 'lex':lex, 'text':body.splitlines() }
