# pylint: disable=no-member,protected-access


import os.path

from expects import be_none, expect, equal, raise_error
from mamba import after, before, context, description, it
from mockito import mock, unstub, when

import shredgen


with description(shredgen) as self:
    with after.each:
        unstub()

    with context(shredgen._get_all_scales_of_type):
        with before.each:
            self.maj_pen_1 = mock(shredgen.MajorPentatonicScale)
            self.maj_pen_2 = mock(shredgen.MajorPentatonicScale)

            when(shredgen)._get_major_pentatonic_scales().thenReturn([self.maj_pen_1, self.maj_pen_2])

        with it('returns all major pentatonic scales when given a major oentatonic scale'):
            expect(shredgen._get_all_scales_of_type(mock(shredgen.MajorPentatonicScale))).to(equal([
                self.maj_pen_1,
                self.maj_pen_2
            ]))

        with it('returns None when given a scale of an unsupported type'):
            expect(shredgen._get_all_scales_of_type(mock(shredgen.Scale))).to(be_none)

        with it('returns None when given None'):
            expect(shredgen._get_all_scales_of_type(None)).to(be_none)

    with context(shredgen._get_all_scales):
        with before.each:
            self.maj_pen_1 = mock(shredgen.MajorPentatonicScale)
            self.maj_pen_2 = mock(shredgen.MajorPentatonicScale)

            when(shredgen)._get_major_pentatonic_scales().thenReturn([self.maj_pen_1, self.maj_pen_2])

        with it('returns the major pentatonic scales'):
            expect(shredgen._get_all_scales()).to(equal([self.maj_pen_1, self.maj_pen_2]))

    with context(shredgen._get_major_pentatonic_scales):
        with it('returns a scale for each key'):
            expect(len(shredgen._get_major_pentatonic_scales())).to(equal(12))

        with it('returns a major pentatonic scale for each key'):
            for scale in shredgen._get_major_pentatonic_scales():
                expect(isinstance(scale, shredgen.MajorPentatonicScale))

    with context(shredgen._get_key_offset):
        with it('returns key #2 number - key #1 number'):
            when(shredgen)._get_key_num('foo').thenReturn(5)
            when(shredgen)._get_key_num('bar').thenReturn(7)
            expect(shredgen._get_key_offset('foo', 'bar')).to(equal(2))

    with context(shredgen._get_key_num):
        with before.each:
            self.keys = dict([
                ('A', 0),
                ('A#', 1), ('Bb', 1),
                ('B', 2),
                ('C', 3),
                ('C#', 4), ('Db', 4),
                ('D', 5),
                ('D#', 6), ('Eb', 6),
                ('E', 7),
                ('F', 8),
                ('F#', 9), ('Gb', 9),
                ('G', 10),
                ('G#', 11), ('Ab', 11),
            ])

        with it('returns the index of the key in the keys array'):
            for key_name, num in self.keys.items():
                expect(shredgen._get_key_num(key_name)).to(equal(num))

        with it('can find the key number regardless of the case of the given key'):
            for key_name, num in self.keys.items():
                expect(shredgen._get_key_num(key_name.upper())).to(equal(num))
                expect(shredgen._get_key_num(key_name.lower())).to(equal(num))

        with it('throws an exception when the given key is unknown'):
            expect(lambda: shredgen._get_key_num('foo')).to(raise_error(shredgen.ExitCodeError))

        with it('throws an exception when the given key is empty'):
            expect(lambda: shredgen._get_key_num('')).to(raise_error(shredgen.ExitCodeError))

        with it('throws an exception when then given key is None'):
            expect(lambda: shredgen._get_key_num(None)).to(raise_error(shredgen.ExitCodeError))


    with context(shredgen._basename):
        with before.each:
            when(os.path).basename(...).thenReturn('basename')

        with it('returns the the basename'):
            expect(shredgen._basename()).to(equal('basename'))
