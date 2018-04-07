def format_h1(str='', width=100, fc='='):
    str_len = len(str)
    if len(str) < width:
        flen = (width - str_len) / 2
        return ''.join([fc for i in range(1, flen)]) + str + ''.join([fc for i in range(1, flen)])
    else:
        return "\n" + str + "\n"