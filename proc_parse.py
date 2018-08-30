def parse_snip_line(line, lex):
                
    w, ww = line.split(' ', maxsplit=2)
    return {'id': w, 'name': w, 'lex': lex, 'text': [ww] }
