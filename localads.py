#!/usr/bin/env python3

# Creates ads...

TOTAL_ADS = 36
LINES_PER_AD = 5

CENTER = b'\x18'
LEFT_JUSTIFY = b'\x19'

outfile = '../Prevue/local.ads'

my_ads = [
    [
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range( 0, 12)]),
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range(12, 24)]),
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range(24, 36)]),
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range(36, 48)]),
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range(48, 60)]),
    ],
    [
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range(60, 72)]),
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range(72, 84)]),
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range(84, 96)]),
        " " + " ".join(["\x03%02d%02d\x0321" % (d, d) for d in range(96, 100)]),
        " \x0356d r i n k m o r e b a w l s\x0321"
    ],


    [" ** \x0341Try the Delicious\x0321 **", " ** \x0357CHEESE SELECTION!\x0321 **", "", " Available now at your local", " Cheese Vendor"],
    [" ", " ", " \x0325You are now breathing manually."],
    [" ", " *B* *A* *W* *L* *S* ", " ", " How many can YOU take? ", " "],
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
