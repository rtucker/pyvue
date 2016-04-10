#!/usr/bin/python3

from curday import ChannelInfo, ChannelListing, Curday, Header, HeaderFlags, pack_file, get_mask, get_timeslot
from datetime import datetime, time
from collections import namedtuple

fcurdayout = "../Prevue/curday.dat"
TIMEZONE=6

def get_git_revision():
    import subprocess
    return subprocess.check_output(["git", "describe"]).decode().strip()

def iter_msg(msgs, seed=0):
    if len(msgs) > 1:
        tsrange = range(1, 49)
    else:
        tsrange = [1]

    for ts in tsrange:
        msg = msgs[(ts+seed) % len(msgs)]
        yield ChannelListing(timeslot=ts, progflags=1, progtype=0,
                             moviecat=0, unk=0, desc=msg)

def iter_schedule(sched):
    for f in sched:
        ts = get_timeslot(TIMEZONE, f.time)
        if f.length > 0:
            desc = bytes("{0.desc} ({0.length} min)".format(f).encode())
        else:
            desc = bytes("{0.desc}".format(f).encode())
        yield ChannelListing(timeslot=ts, desc=desc, progflags=f.flag)

ScheduleItem = namedtuple('ScheduleItem', 'flag time desc length')

if __name__ == '__main__':

    # o = unpack_file(fcurday)

    # # UGLY HACKS FOLLOW
    # o.GetHeader()._obj.flags._obj = o._obj.header._obj.flags._obj._replace(timezone=6)
    # o.GetHeader()._obj = o._obj.header._obj._replace(icao=b'KROC', city=b'Rochester')
    # o.GetHeader().SetDate()
    # for c in o.GetChannels():
    #     c.SetDate()

    # print(o.GetHeader())
    # for c in o.GetChannels():
    #     print("  %s" % c)
    #     for l in c.GetListings():
    #         print("    %s" % l)

    # pack_file(fcurdayout, o)

    top_messages = [
        b"Hungry?  RIT's Global Village has great dining options, such"
        b" as Salsarita's, Oishii Sushi, the Global Grille, and the Cafe"
        b" and Market at Crossroads.",

        b"\x9f Marty's Meats will be parked outside the North Entrance from 11am"
        b" to 3pm today!\x9f",

        b"Check out the Hacker Store!  Buy cool things!",

        b"You must construct additional Pythons.",

        b"Please take a moment to thank our awesome sponsors!",
    ]

    all_timeslots       =   list(range(get_timeslot(TIMEZONE, time(8,00)), get_timeslot(TIMEZONE, time(21,00))))

    track_timeslots     =   list(range(get_timeslot(TIMEZONE, time(10,00)), get_timeslot(TIMEZONE, time(12,00))))
    track_timeslots     +=  list(range(get_timeslot(TIMEZONE, time(14,00)), get_timeslot(TIMEZONE, time(18,00))))

    plenary_timeslots   =   list(range(get_timeslot(TIMEZONE, time(9,00)), get_timeslot(TIMEZONE, time(10,00))))
    plenary_timeslots   +=  list(range(get_timeslot(TIMEZONE, time(12,00)), get_timeslot(TIMEZONE, time(14,00))))
    plenary_timeslots   +=  list(range(get_timeslot(TIMEZONE, time(18,00)), get_timeslot(TIMEZONE, time(20,00))))

    all_mask        =   get_mask(on=all_timeslots)
    plenary_mask    =   get_mask(on=plenary_timeslots)
    track_mask      =   get_mask(on=track_timeslots)
    funny_mask      =   get_mask(off=plenary_timeslots+track_timeslots)

    if True:
        all_mask     = b'\xff\xff\xff\xff\xff\xff'
        plenary_mask = b'\xff\xff\xff\xff\xff\xff'
        track_mask   = b'\xff\xff\xff\xff\xff\xff'
        funny_mask   = b'\xff\xff\xff\xff\xff\xff'

    plenary_schedule    =   [
        ScheduleItem(2, time(9,00), "\"Breakfast\" Ops, volunteers, attendees, and speakers consume the most important meal of the day.", 30),
        ScheduleItem(2, time(9,30), "\"Boot\" Conference Program Counter is set to the boot vector and conference execution begins.", 30),
        ScheduleItem(2, time(12,00), "\"Keynote\" Description goes here.", 60),
        ScheduleItem(1, time(13,00), "Lunch", 60),
        ScheduleItem(2, time(18,00), "\"Closing Ceremony\" CTF results, prizes, and announcements are promulgated to the masses.", 60),
        ScheduleItem(1, time(19,00), "Teardown", 30),
        ScheduleItem(1, time(19,30), "Getting so drunk", 30),
    ]

    track1_schedule     =   [
        ScheduleItem(2, time(10,00), "To be announced", 50),
        ScheduleItem(2, time(11,00), "To be announced", 50),
        ScheduleItem(2, time(14,00), "To be announced", 50),
        ScheduleItem(2, time(15,00), "To be announced", 50),
        ScheduleItem(2, time(16,00), "To be announced", 50),
        ScheduleItem(2, time(17,00), "To be announced", 50),
    ]

    track2_schedule     =   [
        ScheduleItem(2, time(10,00), "To be announced", 50),
        ScheduleItem(2, time(11,00), "To be announced", 50),
        ScheduleItem(2, time(14,00), "To be announced", 50),
        ScheduleItem(2, time(15,00), "To be announced", 50),
        ScheduleItem(2, time(16,00), "To be announced", 50),
        ScheduleItem(2, time(17,00), "To be announced", 50),
    ]

    track3_schedule     =   [
        ScheduleItem(2, time(10,00), "To be announced", 20),
        ScheduleItem(2, time(10,30), "To be announced", 20),
        ScheduleItem(2, time(11,00), "To be announced", 20),
        ScheduleItem(2, time(11,30), "To be announced", 20),
        ScheduleItem(2, time(14,00), "To be announced", 20),
        ScheduleItem(2, time(14,30), "To be announced", 20),
        ScheduleItem(2, time(15,00), "To be announced", 20),
        ScheduleItem(2, time(15,30), "To be announced", 20),
        ScheduleItem(2, time(16,00), "To be announced", 20),
        ScheduleItem(2, time(16,30), "To be announced", 20),
        ScheduleItem(2, time(17,00), "To be announced", 20),
        ScheduleItem(2, time(17,30), "To be announced", 20),
    ]

    commroom_schedule     =   [
        ScheduleItem(2, time(10,00), "Community Programming", 60),
        ScheduleItem(2, time(11,00), "Community Programming", 60),
        ScheduleItem(2, time(14,00), "Community Programming", 60),
        ScheduleItem(2, time(15,00), "Community Programming", 60),
        ScheduleItem(2, time(16,00), "Community Programming", 60),
        ScheduleItem(2, time(17,00), "Community Programming", 60),
    ]

    notice_flag1    = b'\xa2'
    info_flag1      = b'\xe0'
    track_flag1     = b'\x84'
    listing_flag1   = b'\x81'


    generated_at = "Generated {0.hour:02}:{0.minute:02}:{0.second:02} by PyVUE {1}".format(datetime.now(), get_git_revision())

    hf = HeaderFlags(timezone=TIMEZONE)
    h = Header(flags=hf)

    c = [
        # # No idea what this channel does.  It was in the original file.
        # ChannelInfo(channum=b'     ', srcid=b'SBP003', call=b'', flag1=b'\x13',
        #             timeslotmask=b'\x00\x00\x00\x00\x00\x00', blackoutmask=b'\x00\x00\x00\x00\x00\x00',
        #             flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03', srcid2=b'SBP003',
        #             listings=[
        #             ]),

        # # No idea what this one does, either.
        # ChannelInfo(channum=b'     ', srcid=b'SBP004', call=b'', flag1=b'\x13',
        #             timeslotmask=b'\x00\x00\x00\x00\x00\x00', blackoutmask=b'\x00\x00\x00\x00\x00\x00',
        #             flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03', srcid2=b'SBP004',
        #             listings=[
        #             ]),

        ChannelInfo(channum=b'     ', srcid=b'PRV001', call=b'', flag1=b'\xa0',
                    timeslotmask=b'\xff\xff\xff\xff\xff\xff', blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=1, desc=bytes(generated_at.encode()))
                    ]),

        # First listing displayed.
        ChannelInfo(channum=b'     ', srcid=b'SPAM', call=b'', flag1=notice_flag1,
                    timeslotmask=plenary_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg(top_messages)),
                    ),



        # About Plenary
        ChannelInfo(channum=b'     ', srcid=b'TRK000', call=b'', flag1=info_flag1,
                    timeslotmask=plenary_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg([
                        b"Multicast sessions are located in the big auditorium on the"
                        b" main level, with overflow into the large atrium."
                        ])),
                    ),

        # Plenary Listings
        ChannelInfo(channum=b'  0  ', srcid=b'TRACK0', call=b'ff02::', flag1=track_flag1,
                    timeslotmask=plenary_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=iter_schedule(plenary_schedule)),



        # About Track 1
        ChannelInfo(channum=b'     ', srcid=b'TRK001', call=b'', flag1=info_flag1,
                    timeslotmask=track_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg([
                        b"Track 1 is in the big auditorium on the main level. Seating"
                        b" capacity is 150."
                        ])),
                    ),

        # Track 1 listings
        ChannelInfo(channum=b'  1  ', srcid=b'TRACK1', call=b'Track1', flag1=track_flag1,
                    timeslotmask=track_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=iter_schedule(track1_schedule)),



        # About Track 2
        ChannelInfo(channum=b'     ', srcid=b'TRK002', call=b'', flag1=info_flag1,
                    timeslotmask=track_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg([
                        b"Track 2 is located out back, behind the dumpsters."
                        ])),
                    ),

        # Track 2 listings
        ChannelInfo(channum=b'  2  ', srcid=b'TRACK2', call=b'Track2', flag1=track_flag1,
                    timeslotmask=track_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=iter_schedule(track2_schedule)),



        # About Track 3
        ChannelInfo(channum=b'     ', srcid=b'TRK003', call=b'', flag1=info_flag1,
                    timeslotmask=track_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg([
                        b"Track 3 is in the back of Mark's car."
                        ])),
                    ),

        # Track 3 listings
        ChannelInfo(channum=b'  3  ', srcid=b'TRACK3', call=b'Track3', flag1=track_flag1,
                    timeslotmask=track_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=iter_schedule(track3_schedule)),





        # Another repeat of that notice thing
        ChannelInfo(channum=b'     ', srcid=b'SPAM', call=b'', flag1=notice_flag1,
                    timeslotmask=all_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg(top_messages, 1)),
                    ),




        # About Community Room
        ChannelInfo(channum=b'     ', srcid=b'TRK004', call=b'', flag1=info_flag1,
                    timeslotmask=all_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg([
                        b"The Community Room is located somewhere back there, I'm sure."
                        ])),
                    ),

        # Community Room listings
        ChannelInfo(channum=b'  4  ', srcid=b'TRACK4', call=b'CommAc', flag1=track_flag1,
                    timeslotmask=all_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=iter_schedule(commroom_schedule)),




        # About CTF
        ChannelInfo(channum=b'     ', srcid=b'TRK005', call=b'', flag1=info_flag1,
                    timeslotmask=all_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg([
                        b"Hacker Battleship is located in the lounge area. Visit"
                        b" www.bsidesroc.com/hacker-battleship/ for more information."
                        ])),
                    ),

        # CTF listings
        ChannelInfo(channum=b'  5  ', srcid=b'TRACK5', call=b'CTF', flag1=listing_flag1,
                    timeslotmask=all_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=ts, progtype=5, desc=b"Hacker Battleship") for ts in range(1,49,3)
                    ]),




        # Another repeat of that notice thing
        ChannelInfo(channum=b'     ', srcid=b'SPAM', call=b'', flag1=notice_flag1,
                    timeslotmask=b'\xff\xff\xff\xff\xff\xff', blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=list(iter_msg(top_messages, 2)),
                    ),





        ChannelInfo(channum=b'     ', srcid=b'SPAM', call=b'', flag1=info_flag1,
                    timeslotmask=funny_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=t, desc=b"JustBill Pee Counter: 6")
                            if t % 2 == 0 else
                        ChannelListing(timeslot=t, desc=b"Watch JustBill Pee on \x98")
                            for t in range(1, 49, 1)
                    ]),


        ChannelInfo(channum=b'  69 ', srcid=b'THC', call=b'HIST', flag1=listing_flag1,
                    timeslotmask=funny_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=t, desc=bytes(str("Antiques Buttshow %d \xa3" % t).encode())) for t in range(1, 49)
                    ]),


        ChannelInfo(channum=b'  86 ', srcid=b'VINCE', call=b'x56', flag1=listing_flag1,
                    timeslotmask=funny_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=t, desc=b"in ur iPhone, hakin ur snapchatz <3") for t in range(2, 49, 3)
                    ]),

        ChannelInfo(channum=b' 1076', srcid=b'VHDL', call=b'VHDL', flag1=listing_flag1,
                    timeslotmask=funny_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=int(1+t*2), desc=b"end architecture ; -- arch")
                            if t % 2 == 0 else
                        ChannelListing(timeslot=int(1+t*2), desc=b"end architecture arch;")
                            for t in range(1, 24, 1)
                    ]),

        ChannelInfo(channum=b' 1337', srcid=b'JYNIK', call=b'Jynik', flag1=listing_flag1,
                    timeslotmask=funny_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=int(t*2), desc=b"Yak Shaving for Dummies \x9f")
                            if t % 2 == 0 else
                        ChannelListing(timeslot=int(t*2), desc=b"Yak Shaving for Professionals \x9c")
                            for t in range(1, 24, 1)
                    ]),

        ChannelInfo(channum=b' 1701', srcid=b'TRACK7', call=b'Track7', flag1=listing_flag1,
                    timeslotmask=funny_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=t, desc=b"John Cage Revival \x7c") for t in range(2, 49, 2)
                    ]),

        ChannelInfo(channum=b' 2817', srcid=b'BRAINS', call=b'Brains', flag1=listing_flag1,
                    timeslotmask=funny_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=t, desc=b"mmmm zombies") for t in range(1, 49, 2)
                    ]),




        # ChannelInfo(channum=b'  97 ', srcid=b'YV1002', call=b'VC1', flag1=b'\x96',
        #             timeslotmask=funny_mask, blackoutmask=b'\x00\x00\x00\x00\x00\x00',
        #             flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
        #             listings=[
        #                 ChannelListing(timeslot=1, progflags=2, progtype=1, moviecat=4, unk=0,
        #                     desc=b'"Pee-wee\'s Big Adventure" \x8f (1985) Paul Reubens, Elizabeth Daily. Pee-wee Herman '
        #                          b'searches for his missing bisexual. | (1 hr 30 min)'),

        #                 ChannelListing(timeslot=4, progflags=2, progtype=1, moviecat=9, unk=0,
        #                     desc=b'"The Blair Witch Project" \x84 (1999) Heather Donahue, Michael Williams. Independent '
        #                          b'hit about student filmmakers who are terrorized in the forest. \x91 | (1 hr 21 min)'),

        #                 ChannelListing(timeslot=7, progflags=2, progtype=1, moviecat=18, unk=0,
        #                     desc=b'"The Matrix" \x84 (1999) Keanu Reeves, Laurence Fishburne. Dazzling special effects '
        #                          b'frame a compelling story about a hacker on the run. \x91 | (2 hrs 28 min)'),

        #                 ChannelListing(timeslot=14, progflags=2, progtype=1, moviecat=4, unk=0,
        #                     desc=b'"Pee-wee\'s Big Adventure" \x8f (1985) Paul Reubens, Elizabeth Daily. Pee-wee Herman '
        #                          b'searches for his missing bisexual. | (1 hr 30 min)'),

        #                 ChannelListing(timeslot=17, progflags=2, progtype=1, moviecat=9, unk=0,
        #                     desc=b'"The Blair Witch Project" \x84 (1999) Heather Donahue, Michael Williams. Independent '
        #                          b'hit about student filmmakers who are terrorized in the forest. \x91 | (1 hr 21 min)'),

        #                 ChannelListing(timeslot=21, progflags=2, progtype=1, moviecat=18, unk=0,
        #                     desc=b'"The Matrix" \x84 (1999) Keanu Reeves, Laurence Fishburne. Dazzling special effects '
        #                          b'frame a compelling story about a hacker on the run. \x91 | (2 hrs 28 min)'),

        #                 ChannelListing(timeslot=24, progflags=2, progtype=1, moviecat=4, unk=0,
        #                     desc=b'"Pee-wee\'s Big Adventure" \x8f (1985) Paul Reubens, Elizabeth Daily. Pee-wee Herman '
        #                          b'searches for his missing bisexual. | (1 hr 30 min)'),

        #                 ChannelListing(timeslot=27, progflags=2, progtype=1, moviecat=9, unk=0,
        #                     desc=b'"The Blair Witch Project" \x84 (1999) Heather Donahue, Michael Williams. Independent '
        #                          b'hit about student filmmakers who are terrorized in the forest. \x91 | (1 hr 21 min)'),

        #                 ChannelListing(timeslot=31, progflags=2, progtype=1, moviecat=18, unk=0,
        #                     desc=b'"The Matrix" \x84 (1999) Keanu Reeves, Laurence Fishburne. Dazzling special effects '
        #                          b'frame a compelling story about a hacker on the run. \x91 | (2 hrs 28 min)'),

        #                 ChannelListing(timeslot=38, progflags=2, progtype=1, moviecat=4, unk=0,
        #                     desc=b'"Pee-wee\'s Big Adventure" \x8f (1985) Paul Reubens, Elizabeth Daily. Pee-wee Herman '
        #                          b'searches for his missing bisexual. | (1 hr 30 min)'),

        #                 ChannelListing(timeslot=41, progflags=2, progtype=1, moviecat=9, unk=0,
        #                     desc=b'"The Blair Witch Project" \x84 (1999) Heather Donahue, Michael Williams. Independent '
        #                          b'hit about student filmmakers who are terrorized in the forest. \x91 | (1 hr 21 min)'),

        #                 ChannelListing(timeslot=44, progflags=2, progtype=1, moviecat=18, unk=0,
        #                     desc=b'"The Matrix" \x84 (1999) Keanu Reeves, Laurence Fishburne. Dazzling special effects '
        #                          b'frame a compelling story about a hacker on the run. \x91 | (2 hrs 28 min)'),
        #             ]),



        # Last line!
        ChannelInfo(channum=b'     ', srcid=b'PRV002', call=b'', flag1=b'\xa0',
                    timeslotmask=b'\xff\xff\xff\xff\xff\xff', blackoutmask=b'\x00\x00\x00\x00\x00\x00',
                    flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                    listings=[
                        ChannelListing(timeslot=t, desc=b"Rochester's only free and open hacker conference")
                            if t % 2 == 0 else
                        ChannelListing(timeslot=t, desc=b"www.bsidesroc.com")
                            for t in range(1, 49, 1)
                    ]),
    ]

    o = Curday(header=h, channels=c)

    pack_file(fcurdayout, o)
