import opencc

def widthCnt(s):
    cnt = 0
    for c in s:
        if ord(c) <= 0x7e:
            cnt += 0.5
        else:
            cnt += 1
    return cnt

converter = opencc.OpenCC('t2s.json')
def format(s):
    s = '\n'.join([line.strip() for line in s.splitlines()])
    s = converter.convert(s)
    return s
