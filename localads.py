#!/usr/bin/env python3

# Creates ads...

TOTAL_ADS = 36
LINES_PER_AD = 5

CENTER = b'\x18'
LEFT_JUSTIFY = b'\x19'

outfile = '../Prevue/local.ads'

my_ads = [
    [" ** Try the Delicious **", " ** CHEESE SELECTION! **", "", " Available now at your local", " Cheese Vendor"],
    [" ", " ", " You are now breathing manually."],
]

def render_ad(ad):
    while len(ad) < LINES_PER_AD:
        ad.append(' ')

    out = b''.join([
        b'1',   # start timeslot?
        b'\x00',
        b'48',  # end timeslot?
        b'\x00',
        b'\x0321',  # color?
    ])

    for r in ad:
        if r.startswith(' '):
            out += CENTER
            r = r.lstrip(' ')
        else:
            out += LEFT_JUSTIFY
        out += bytes(r.encode())

    out += b'\x00'

    return out        

def null_ad():
    return b'0\x000\x00\x00'

if __name__ == '__main__':
    with open(outfile, 'wb') as fp:
        for ad in my_ads:
            fp.write(render_ad(ad))
        for i in range(len(my_ads), TOTAL_ADS):
            fp.write(null_ad())
