#!/usr/bin/env python3

fcurday = "../curday.dat.pristine"
fcurdayout = "../Prevue/curday.dat"
fnxtday = "../nxtday.dat.pristine"
fnxtdayout = "../Prevue/nxtday.dat"

from collections import namedtuple
from copy import copy
from enum import Enum
import time

def read_byte(fp):
    while True:
        block = fp.read(1)
        if len(block) == 0:
            break
        yield block

class Thing(object):
    _bytes = None
    _obj = None

    def __init__(self, b=None, fp=None, **kw):
        if b is not None:
            self.SetBytes(b)
            # ChannelListing will not be byte-exact in many cases
            assert(isinstance(self, ChannelListing) or bytes(self) == b)
        elif fp is not None:
            self._readfile(fp)
            b = copy(self._bytes)
            assert(bytes(self) == b)
        else:
            self._create(**kw)

    def _readfile(self, fp):
        self._bytes = b''.join([b for b in read_byte(fp)])
        self._unpack()

    def __repr__(self):
        if self._obj is not None:
            return repr(self._obj)
        else:
            return repr(self._bytes)

    def _create(self):
        pass

    def _pack(self):
        pass

    def _unpack(self):
        pass

    def SetBytes(self, b):
        self._bytes = b
        self._unpack()

    def __bytes__(self):
        self._pack()
        return self._bytes

HeaderFlagsTuple = namedtuple('HeaderFlags', 'bck fwd scrollspeed numads linesperad unk6 timezone unk8 unk9 unk10 unk11 unk12 unk13 unk14 unk15 unk16')

class HeaderFlags(Thing):
    def _create(self,
        bck=b'A',
        fwd=b'E',
        scrollspeed=3,
        numads=36,
        linesperad=5,
        unk6=b'N',
        # ETX
        # SOH
        timezone=6,
        unk8=b'Y',
        unk9=b'Y',
        unk10=b'N',
        unk11=b'N',
        unk12=b'Y',
        unk13=b'Y',
        unk14=b'N',
        unk15=b'N',
        unk16=b'l',
    ):
        self._obj = HeaderFlagsTuple(
            bck=bck,
            fwd=fwd,
            scrollspeed=scrollspeed,
            numads=numads,
            linesperad=linesperad,
            unk6=unk6,
            # ETX
            # SOH
            timezone=timezone,
            unk8=unk8,
            unk9=unk9,
            unk10=unk10,
            unk11=unk11,
            unk12=unk12,
            unk13=unk13,
            unk14=unk14,
            unk15=unk15,
            unk16=unk16,
        )

    def _unpack(self):
        self._obj = HeaderFlagsTuple(
            bck=self._bytes[0:1],
            fwd=self._bytes[1:2],
            scrollspeed=int(self._bytes[2:3]),
            numads=int(self._bytes[3:5]),
            linesperad=int(self._bytes[5:6]),
            unk6=self._bytes[6:7],
            # ETX
            # SOH
            timezone=int(self._bytes[9:10]),
            unk8=self._bytes[10:11],
            unk9=self._bytes[11:12],
            unk10=self._bytes[12:13],
            unk11=self._bytes[13:14],
            unk12=self._bytes[14:15],
            unk13=self._bytes[15:16],
            unk14=self._bytes[16:17],
            unk15=self._bytes[17:18],
            unk16=self._bytes[18:19],
        )

    def _pack(self):
        if self._obj is not None:
            self._bytes = b''.join([
                self._obj.bck,
                self._obj.fwd,
                bytes(str(self._obj.scrollspeed).encode()),
                bytes(str(self._obj.numads).encode()),
                bytes(str(self._obj.linesperad).encode()),
                self._obj.unk6,
                b'\x03\x01',
                bytes(str(self._obj.timezone).encode()),
                self._obj.unk8,
                self._obj.unk9,
                self._obj.unk10,
                self._obj.unk11,
                self._obj.unk12,
                self._obj.unk13,
                self._obj.unk14,
                self._obj.unk15,
                self._obj.unk16,
            ])

HeaderTuple = namedtuple('Header', 'flags unk0 drev icao city jdate numchans unk1 unk2')

class Header(Thing):
    def _create(self,
        flags=None,
        unk0=0,
        drev=b'DREV 5',
        icao=b'KROC',
        city=b'Rochester',
        jdate=None,
        numchans=0,
        unk1=131,
        unk2=1348,
    ):
        self._obj = HeaderTuple(
            flags=HeaderFlags(flags),
            unk0=unk0,
            drev=drev,
            icao=icao,
            city=city,
            jdate=jdate,
            numchans=numchans,
            unk1=unk1,
            unk2=unk2,
        )

        if self._obj.jdate is None:
            self.SetDate()

    def _unpack(self):
        s = self._bytes.split(b'\x00')

        flags = HeaderFlags(s[0])

        self._obj = HeaderTuple(
            flags=flags,
            unk0=int(s[2]),
            drev=s[3],
            icao=s[4],
            city=s[5],
            jdate=int(s[6]),
            numchans=int(s[7]),
            unk1=int(s[8]),
            unk2=int(s[9]),
            )

    def _pack(self):
        if self._obj is not None:
            self._bytes = b'\x00'.join([
                bytes(self._obj.flags),
                b'',
                bytes(str(self._obj.unk0).encode()),
                self._obj.drev,
                self._obj.icao,
                self._obj.city,
                bytes(str(self._obj.jdate).encode()),
                bytes(str(self._obj.numchans).encode()),
                bytes(str(self._obj.unk1).encode()),
                bytes(str(self._obj.unk2).encode()),
                b'',
            ])

    def SetDate(self, date=time.gmtime()):
        """Set the date in a header.

        The curdat format expects a Julian date from 0 to 255, resetting
        to 0 on day 256.
        """

        # Range from 1 to 366
        jd = int(time.strftime('%j', date))

        #XXX: don't decrement after Feb 29 on a leap year...
        #jd -= 1

        jd %= 256

        self._obj = self._obj._replace(jdate=jd)

    def SetNumChans(self, numchans):
        self._obj = self._obj._replace(numchans=numchans)

ChannelInfoTuple = namedtuple('ChannelInfo', 'jdate channum srcid call flag1 timeslotmask blackoutmask flag2 bgcolor brushid flag3 srcid2')

class ciParseFSM(Enum):
    # State machine for parsing curday files.
    parsejdate = 1
    parsechannum = 2
    parsesrcid = 3
    parsecall = 4
    parseflag1 = 5
    parsetimeslotmask = 6
    parseblackoutmask = 7
    parseflag2 = 8
    parsebgcolor = 9
    parsebrushid = 10
    parseflag3 = 11
    parsesrcid2 = 12

class ChannelInfo(Thing):
    _listings = []

    def _create(self, channum, srcid, call, jdate=None, 
            flag1=b'\x81', timeslotmask=b'\xff\xff\xff\xff\xff\xff',
            blackoutmask=b'\x00\x00\x00\x00\x00\x00', flag2=b'\x82', bgcolor=b'\xff\xff',
            brushid=b'00', flag3=b'\x03', srcid2=None, listings=[]):

        self._obj = ChannelInfoTuple(jdate=jdate, channum=channum, srcid=srcid,
            call=call, flag1=flag1, timeslotmask=timeslotmask,
            blackoutmask=blackoutmask, flag2=flag2, bgcolor=bgcolor,
            brushid=brushid, flag3=flag3, srcid2=srcid2 if srcid2 is not None else srcid)

        self._listings = listings + [ChannelListing(timeslot=49)]

        if self._obj.jdate is None:
            self.SetDate()

    def _unpack(self):
        self._listings = []
        this_state = ciParseFSM.parsejdate
        next_state = ciParseFSM.parsejdate
        first_ptr = 0
        cur_ptr = 0
        result = []

        while cur_ptr < len(self._bytes):
            if next_state != this_state:
                first_ptr = cur_ptr

            this_state = next_state
            cur_ptr += 1

            #print(this_state, cur_ptr, self._bytes[cur_ptr:cur_ptr+1], result)

            if this_state == ciParseFSM.parsejdate:
                result.append(self._bytes[first_ptr:cur_ptr])
                next_state = ciParseFSM.parsechannum

            if this_state == ciParseFSM.parsechannum:
                if self._bytes[cur_ptr:cur_ptr+1] == b'\x00':
                    result.append(self._bytes[first_ptr:cur_ptr])
                    next_state = ciParseFSM.parsesrcid

            if this_state == ciParseFSM.parsesrcid:
                first_ptr += 6  # skip 6 nulls
                cur_ptr = first_ptr + 6
                result.append(self._bytes[first_ptr:cur_ptr].strip(b'\x00'))
                next_state = ciParseFSM.parsecall

            if this_state == ciParseFSM.parsecall:
                first_ptr += 1  # skip 1 null
                cur_ptr = first_ptr + 6
                result.append(self._bytes[first_ptr:cur_ptr].strip(b'\x00'))
                next_state = ciParseFSM.parseflag1

            if this_state == ciParseFSM.parseflag1:
                first_ptr += 2  # skip 2 nulls
                cur_ptr = first_ptr + 1
                result.append(self._bytes[first_ptr:cur_ptr])
                next_state = ciParseFSM.parsetimeslotmask

            if this_state == ciParseFSM.parsetimeslotmask:
                cur_ptr = first_ptr + 6
                result.append(self._bytes[first_ptr:cur_ptr])
                next_state = ciParseFSM.parseblackoutmask

            if this_state == ciParseFSM.parseblackoutmask:
                cur_ptr = first_ptr + 6
                result.append(self._bytes[first_ptr:cur_ptr])
                next_state = ciParseFSM.parseflag2

            if this_state == ciParseFSM.parseflag2:
                cur_ptr = first_ptr + 1
                result.append(self._bytes[first_ptr:cur_ptr])
                next_state = ciParseFSM.parsebgcolor

            if this_state == ciParseFSM.parsebgcolor:
                cur_ptr = first_ptr + 2
                result.append(self._bytes[first_ptr:cur_ptr])
                next_state = ciParseFSM.parsebrushid

            if this_state == ciParseFSM.parsebrushid:
                cur_ptr = first_ptr + 2
                result.append(self._bytes[first_ptr:cur_ptr])
                next_state = ciParseFSM.parseflag3

            if this_state == ciParseFSM.parseflag3:
                first_ptr += 2  # skip 2 nulls
                cur_ptr = first_ptr + 1
                result.append(self._bytes[first_ptr:cur_ptr])
                next_state = ciParseFSM.parsesrcid2

            if this_state == ciParseFSM.parsesrcid2:
                cur_ptr = first_ptr + 6
                result.append(self._bytes[first_ptr:cur_ptr].strip(b'\x00'))
                break

        self._obj = ChannelInfoTuple(*result)

    def _pack(self):
        if self._obj is not None:
            self._bytes = b'\x00'.join([
                self._obj.jdate + self._obj.channum,
                b'', b'', b'', b'', b'',
                self._obj.srcid.ljust(6, b'\x00'),
                self._obj.call.ljust(6, b'\x00'),
                b'',
                (
                    self._obj.flag1 +
                    self._obj.timeslotmask +
                    self._obj.blackoutmask +
                    self._obj.flag2 +
                    self._obj.bgcolor +
                    self._obj.brushid
                ),
                b'',
                (
                    self._obj.flag3 +
                    self._obj.srcid2
                ),
            ])

    def __bytes__(self):
        self._pack()
        return b''.join([self._bytes] + [bytes(listing) for listing in self._listings])

    def AddListing(self, listing):
        self._listings.append(listing)

    def GetListings(self):
        return self._listings

    def SetDate(self, date=time.gmtime()):
        """Set the date in a channel.

        The curdat format expects a Julian date from 0 to 255, resetting
        to 0 on day 256.
        """

        # Range from 1 to 366
        jd = int(time.strftime('%j', date))

        #XXX: don't decrement after Feb 29 on a leap year...
        #jd -= 1

        jd %= 256

        self._obj = self._obj._replace(jdate=bytes([jd]))

ChannelListingTuple = namedtuple('ChannelListing', 'timeslot progflags progtype moviecat unk desc')

class ChannelListing(Thing):

    def IsLastEntry(self):
        #return self._bytes.startswith(b'\x0049\x00')
        return self._obj.timeslot == 49

    def _create(self, timeslot, progflags=1, progtype=34, moviecat=0, unk=0, desc="To Be Announced"):
        if isinstance(desc, str):
            desc = bytes(desc.encode())
        if timeslot == 49:
            self._obj = ChannelListingTuple(49, 0, 0, 0, 0, b'')
        else:
            self._obj = ChannelListingTuple(timeslot, progflags, progtype, moviecat, unk, desc)

    def _unpack(self):
        if self._bytes.startswith(b'\x0049\x00'):
            self._bytes = b'\x0049\x00'
            self._obj = ChannelListingTuple(49, 0, 0, 0, 0, b'')
        else:
            s = self._bytes.split(b'\x00')[1:7]
            self._obj = ChannelListingTuple(
                timeslot=int(s[0]),
                progflags=int(s[1]),
                progtype=int(s[2]),
                moviecat=int(s[3]),
                unk=int(s[4]),
                desc=s[5]
            )

    def _pack(self):
        if self._obj is not None:
            if self._obj.timeslot != 49:
                self._bytes = b'\x00'.join([
                    b'',
                    bytes(str(self._obj.timeslot).encode()),
                    bytes(str(self._obj.progflags).encode()),
                    bytes(str(self._obj.progtype).encode()),
                    bytes(str(self._obj.moviecat).encode()),
                    bytes(str(self._obj.unk).encode()),
                    self._obj.desc,
                ])
            else:
                self._bytes = b'\x0049\x00'

class cdParseFSM(Enum):
    # State machine for parsing curday files.
    ParseHeader = 1
    ParseChannelInfo = 2
    ParseChannelListing = 3

CurdayTuple = namedtuple('Curday', 'header channels')

class Curday(Thing):
    """
    EPG for the current day.  (DREV 5)

    With serious props to: http://prevueguide.com/wiki/Prevue_Emulation:Curday.dat_and_Nxtday.dat
    """

    def _create(self, header, channels):
        self._obj = CurdayTuple(header, channels)
        self._obj.header.SetNumChans(len(self._obj.channels))

    def _unpack(self):
        state = cdParseFSM.ParseHeader
        null_count = 0
        buf = b''
        current_channel = None

        header = None
        channels = []

        for b in self._bytes:
            b = bytes([b])
            buf += b
            if b == b'\x00':
                null_count += 1

            if state is cdParseFSM.ParseHeader and null_count is 10:
                # This is our header.  Proceed forth into the channels.
                header = Header(buf)
                buf = b""
                state = cdParseFSM.ParseChannelInfo
                null_count = 0
                #print("State transition: ParseHeader -> ParseChannelInfo")

            elif state is cdParseFSM.ParseChannelInfo and len(buf) > 50 and b == b'\x00':
                # Channel information is here.
                current_channel = ChannelInfo(buf[:-1])
                buf = b"\x00"
                state = cdParseFSM.ParseChannelListing
                null_count = 1
                #print("State transition: ParseChannelInfo -> ParseChannelListing")

            elif state is cdParseFSM.ParseChannelListing and null_count is 7:
                cl = ChannelListing(buf)
                current_channel.AddListing(cl)
                if cl.IsLastEntry():
                    # This was the end marker
                    buf = buf.lstrip(b"\x0049\x00")
                    null_count = 0
                    state = cdParseFSM.ParseChannelInfo
                    channels.append(current_channel)
                    current_channel = None
                    #print("State transition: ParseChannelListing -> ParseChannelInfo")
                else:
                    null_count = 1
                    buf = b"\x00"

        # Deal with straggler
        if state is cdParseFSM.ParseChannelListing:
            cl = ChannelListing(buf)
            current_channel.AddListing(cl)
            channels.append(current_channel)

        self._obj = CurdayTuple(header, channels)

    def _pack(self):
        if self._obj is not None:
            # print("")
            # print("*** ORIGINAL ***")
            # print("")
            # print(self._bytes)
            self._obj.header.SetNumChans(len(self._obj.channels))
            self._bytes = b''.join([
                bytes(self._obj.header),
                b''.join([bytes(channel) for channel in self._obj.channels]),
            ])
            # print("")
            # print("*** NEW ***")
            # print("")
            # print(self._bytes)

    def GetHeader(self):
        return self._obj.header

    def GetChannels(self):
        return self._obj.channels

def unpack_file(fname):
    with open(fname, 'rb') as fp:
        cdobj = Curday(fp=fp)

        return cdobj

def pack_file(fname, curday):
    with open(fname, 'wb') as fp:
        fp.write(bytes(curday))

if __name__ == '__main__':

    if True:
        hf = HeaderFlags()
        h = Header()

        c = [
              ChannelInfo(channum=b'  69 ', srcid=b'THC', call=b'HIST', flag1=b'\x81', timeslotmask=b'\xff\xff\xff\xff\xff\xff',
                blackoutmask=b'\x00\x00\x00\x00\x00\x00', flag2=b'\x82', bgcolor=b'\xff\xff', brushid=b'00', flag3=b'\x03',
                srcid2=b'THC', listings=[
                    ChannelListing(timeslot=t, desc="Antiques Buttshow %d" % t) for t in range(1, 49)
                ])
        ]

        o = Curday(header=h, channels=c)



        print(o.GetHeader())
        for c in o.GetChannels():
            print("  %s" % c)
            for l in c.GetListings():
                print("    %s" % l)

        pack_file(fcurdayout, o)

    if False:

        o = unpack_file(fcurday)

        # UGLY HACKS FOLLOW
        o.GetHeader()._obj.flags._obj = o._obj.header._obj.flags._obj._replace(timezone=6)
        o.GetHeader()._obj = o._obj.header._obj._replace(icao=b'KROC', city=b'Rochester')
        o.GetHeader().SetDate()
        for c in o.GetChannels():
            c.SetDate()

        print(o.GetHeader())
        for c in o.GetChannels():
            print("  %s" % c)
            for l in c.GetListings():
                print("    %s" % l)

        pack_file(fcurdayout, o)
