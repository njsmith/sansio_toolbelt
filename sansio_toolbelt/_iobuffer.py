# -*- coding: utf-8 -*-

import sys
import operator

class IOBuffer(object):
    def __init__(self):
        self._data = bytearray()

    def __delitem__(self, slice_):
        if slice_.start is not None or slice_.step is not None:
            raise IndexError("I only support deletion like: del buf[:n]")
        del self._data[slice_]


class IOBuffer(object):
    """An efficient I/O buffer."""

    def __init__(self):
        self._data = bytearray()
        # These are both absolute offsets into self._data:
        self._start = 0
        self._looked_at = 0
        self._looked_for = None

    def __bool__(self):
        return bool(len(self))

    def __bytes__(self):
        return bytes(self._data[self._start:])

    if sys.version_info[0] < 3:  # version specific: Python 2
        __str__ = __bytes__
        __nonzero__ = __bool__

    def __len__(self):
        return len(self._data) - self._start

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            start = idx.start
            if start is None:
                start = 0
            if start >= 0:
                start + self._start

            stop = idx.stop
            if stop is None:
                stop = len(self)
            if stop >= 0:
                stop += self._start

            return self._data[start:stop:idx.step]
        else:
            return self._data[self._start + operator.index(idx)]

    def __iadd__(self, byteslike):
        self._data += byteslike
        return self

    def __repr__(self):
        if len(self) > 50:
            first = bytes(self[:20])
            last = bytes(self[-20:])
            data_repr = repr(first)[:-1] + "..."
            if sys.version_info[0] < 3:
                data_repr += repr(last)[1:]
            else:
                data_repr += repr(last)[2:]
        else:
            data_repr = repr(bytes(self))
        return "<IOBuffer with {} bytes: {}>".format(len(self), data_repr)

    # Note that starting in Python 3.4, deleting the initial n bytes from a
    # bytearray is amortized O(n), thanks to some excellent work by Antoine
    # Martin:
    #
    #     https://bugs.python.org/issue19087
    #
    # This means that if we only supported 3.4+, we could get rid of the code
    # here involving self._start and self.compress, because it's doing exactly
    # the same thing that bytearray now does internally.
    #
    # BUT unfortunately, we still support 2.7, and reading short segments out
    # of a long buffer MUST be O(bytes read) to avoid DoS issues, so we can't
    # actually delete this code. Yet:
    #
    #     https://pythonclock.org/
    #
    # (Two things to double-check first though: make sure PyPy also has the
    # optimization, and benchmark to make sure it's a win, since we do have a
    # slightly clever thing where we delay calling compress() until we've
    # processed a whole event, which could in theory be slightly more
    # efficient than the internal bytearray support.)
    def compress(self):
        # Heuristic: only compress if it lets us reduce size by a factor
        # of 2
        if self._start > len(self._data) // 2:
            del self._data[:self._start]
            self._looked_at -= self._start
            self._start -= self._start

    def discard_exactly(self, count):
        if len(self) < count:
            raise ValueError("not enough data to discard")
        else:
            self._start += count

    def maybe_extract_exactly(self, count):
        if len(self) < count:
            return None
        else:
            return self.maybe_extract_at_most(count)

    def maybe_extract_at_most(self, count):
        out = self._data[self._start:self._start + count]
        if not out:
            return None
        self._start += len(out)
        return out

    def maybe_extract_until_next(self, needle):
        # Returns extracted bytes on success (advancing offset), or None on
        # failure
        if self._looked_for == needle:
            search_start = max(self._start, self._looked_at - len(needle) + 1)
        else:
            search_start = self._start
        offset = self._data.find(needle, search_start)
        if offset == -1:
            self._looked_at = len(self._data)
            self._looked_for = needle
            return None
        new_start = offset + len(needle)
        out = self._data[self._start:new_start]
        self._start = new_start
        return out

    def maybe_extract_until_next_re(self, needle, max_match_len):
        if self._looked_for == needle:
            search_start = max(self._start, self._looked_at - max_match_len + 1)
        else:
            search_start = self._start
        match = needle.search(self._data, search_start)
        if match is None:
            self._looked_at = len(self._data)
            self._looked_for = needle
            return None
        out = self._data[self._start:match.end()]
        self._start = match.end()
        return out

import re
ambig_newline = re.compile(rb"\r\n|\n")
two_ambig_newlines = re.compile(rb"\r\n\r\n|\n\n")

def maybe_extract_lines(iobuf):
    if iobuf[:1] == b"\n":
        iobuf.discard_exactly(1)
    elif iobuf[:2] == b"\r\n":
        iobuf.discard_exactly(2)
        return []
    else:
        data = iobuf.maybe_extract_until_next_re(two_ambig_newlines, 4)
        if data is None:
            return None
        if data[-2:] == b"\n\n":
            lines = data.split(b"\n")
        else:
            lines = data.split(b"\r\n")
        assert lines[-2] == lines[-1] == b""
        del lines[-2:]
        return lines

def lines(iobuf):
    while True:
        yield iobuf.maybe_extract_until_next(b"\n")

gen = lines(iobuf)
while True:
    event = next(gen)
    if event is None:
        iobuf += get_more_data()
    else:
        yield event

