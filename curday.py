#!/usr/bin/env python3

fcurday = "../Prevue/curday.dat"
fnxtday = "../Prevue/nxtday.dat"

from copy import copy
from enum import Enum
from collections import namedtuple

class Thing(object):
    _bytes = b""

    def __init__(self, b):
        self._bytes = b

    def _parse(self):
        return self._bytes

    def __repr__(self):
        dat = self._parse()
        return repr(dat)

HeaderTuple = namedtuple('Header', 'flags1 flags2 unk0 drev icao city jdate numchans unk1 unk2')

class Header(Thing):
    _channels = []

    def _parse(self):
        s = self._bytes.split(b'\x00')

        return HeaderTuple(
            s[0][0:7],
            s[0][9:19],
            *s[2:10]
            )

ChannelInfoTuple = namedtuple('Channel', 'jday channum srcid call flag1 timeslotmask blackoutmask flag2 bgcolor brushid flag3 srcid2')

class ciParseFSM(Enum):
    # State machine for parsing curday files.
    parsejday = 1
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

    def __init__(self, b):
        self._bytes = b
        self._listings = []

    def _parse(self):
        this_state = ciParseFSM.parsejday
        next_state = ciParseFSM.parsejday
        first_ptr = 0
        cur_ptr = 0
        result = []

        while cur_ptr < len(self._bytes):
            if next_state != this_state:
                first_ptr = cur_ptr

            this_state = next_state
            cur_ptr += 1

            #print(this_state, cur_ptr, self._bytes[cur_ptr:cur_ptr+1], result)

            if this_state == ciParseFSM.parsejday:
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

        return ChannelInfoTuple(*result)

    def AddListing(self, listing):
        self._listings.append(listing)

    def GetListings(self):
        return self._listings

ChannelListingTuple = namedtuple('Listing', 'timeslot progflags progtype moviecat unk desc')

class ChannelListing(Thing):

    def IsLastEntry(self):
        return self._bytes.startswith(b'\x0049\x00')

    def _parse(self):
        s = self._bytes.split(b'\x00')[1:7]
        if s[0] == b'49':
            # invalid/pad entry
            return ChannelListingTuple(b'49', b'0', b'0', b'0', b'0', b'')
        else:
            return ChannelListingTuple(*s)

def read_byte(fp):
    while True:
        block = fp.read(1)
        if len(block) == 0:
            break
        yield block

class cdParseFSM(Enum):
    # State machine for parsing curday files.
    ParseHeader = 1
    ParseChannelInfo = 2
    ParseChannelListing = 3

class Curday(object):
    """
    EPG for the current day.  (DREV 5)

    With serious props to: http://prevueguide.com/wiki/Prevue_Emulation:Curday.dat_and_Nxtday.dat
    """

    _header = None
    _channels = []

    def __init__(self, fp=None):
        if fp is not None:
            state = cdParseFSM.ParseHeader
            null_count = 0
            buf = b""
            current_channel = None

            for b in read_byte(fp):
                buf += b
                if b == b'\x00':
                    null_count += 1

                if state is cdParseFSM.ParseHeader and null_count is 10:
                    # This is our header.  Proceed forth into the channels.
                    self._header = Header(buf)
                    buf = b""
                    state = cdParseFSM.ParseChannelInfo
                    null_count = 0
                    #print("State transition: ParseHeader -> ParseChannelInfo")

                elif state is cdParseFSM.ParseChannelInfo and len(buf) > 50 and b == b'\x00':
                    # Channel information is here.
                    current_channel = ChannelInfo(buf)
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
                        self._channels.append(current_channel)
                        #print("State transition: ParseChannelListing -> ParseChannelInfo")
                    else:
                        null_count = 1
                        buf = b"\x00"

    def GetHeader(self):
        return self._header

    def GetChannels(self):
        return self._channels

def unpack_file(fname):
    with open(fname, 'rb') as fp:
        cdobj = Curday(fp)

        return cdobj


o = unpack_file(fcurday)

print(o.GetHeader())
for c in o.GetChannels():
    print("  %s" % c)
    for l in c.GetListings():
        print("    %s" % l)
