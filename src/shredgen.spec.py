# pylint: disable=invalid-name,line-too-long,no-member,protected-access


import builtins
import os.path
import random

from expects import be_none, expect, equal, raise_error
from mamba import after, before, description, it
from mockito import arg_that, mock, unstub, when, verify

import shredgen


with description(shredgen) as self:
    with after.each:
        unstub()

    with description(shredgen._validate_scale_name):
        with it('does not throw an exception when given a non-empty scale name'):
            expect(lambda: shredgen._validate_scale_name('foo')).not_to(raise_error)

        with it('throws an exception when given an empty scale name'):
            expect(lambda: shredgen._validate_scale_name('')).to(raise_error(shredgen.ExitCodeError))

        with it('throws an exception when given None'):
            expect(lambda: shredgen._validate_scale_name(None)).to(raise_error(shredgen.ExitCodeError))

    with description(shredgen._validate_scale):
        with before.each:
            self.opts = mock({'scale': 'mock_scale'})
            when(shredgen)._basename().thenReturn('shredgen')

        with it('does not throw an error when the given scale exists'):
            expect(lambda: shredgen._validate_scale(self.opts, mock(shredgen.Scale))).not_to(raise_error)

        with it('throws an error when the given scale is None'):
            expect(lambda: shredgen._validate_scale(self.opts, None)).to(raise_error(shredgen.ExitCodeError))

    with description(shredgen._validate_length):
        with it('does not throw an error when the length is a positive integer'):
            expect(lambda: shredgen._validate_length('3')).not_to(raise_error)

        with it('throws an errow when the length is zero'):
            expect(lambda: shredgen._validate_length('0')).to(raise_error(shredgen.ExitCodeError))

        with it('throws an errow when the length is negative'):
            expect(lambda: shredgen._validate_length('-3')).to(raise_error(shredgen.ExitCodeError))

        with it('throw an error when the length is not a number'):
            expect(lambda: shredgen._validate_length('foo')).to(raise_error(shredgen.ExitCodeError))

        with it('throws an error when the length is a floating point number'):
            expect(lambda: shredgen._validate_length('1.1')).to(raise_error(shredgen.ExitCodeError))

        with it('throws an error when the length is a invalid base 10 number'):
            expect(lambda: shredgen._validate_length('FF')).to(raise_error(shredgen.ExitCodeError))

    with description(shredgen._shred_in_scale):
        with it('generates a random array of notes from the given scale of the given length'):
            note_a = mock(shredgen.Note)
            note_b = mock(shredgen.Note)
            note_c = mock(shredgen.Note)
            scale = mock({'notes': [note_a, note_b, note_c]}, spec=shredgen.Scale)

            when(builtins).print(...)
            when(random).randrange(...).thenReturn(2, 1, 0, 1, 2)
            shredgen._shred_in_scale(scale, 5)

            verify(builtins).print(arg_that(lambda arg: arg.notes == [
                note_c,
                note_b,
                note_a,
                note_b,
                note_c
            ]))

    with description(shredgen._get_scale_by_name):
        with before.each:
            self.scale_a = mock({'aliases': ['a', 'aa', 'aaa']}, spec=shredgen.Scale)
            self.scale_b = mock({'aliases': ['b', 'bb', 'bbb']}, spec=shredgen.Scale)
            self.scale_c = mock({'aliases': ['c', 'cc', 'ccc']}, spec=shredgen.Scale)

            when(shredgen)._get_all_scales().thenReturn([self.scale_a, self.scale_b, self.scale_c])

        with it('returns the first scale whose aliases contains the given name'):
            expect(shredgen._get_scale_by_name('bb')).to(equal(self.scale_b))

        with it('can find scales regarless of the case of the given name'):
            expect(shredgen._get_scale_by_name('bBb')).to(equal(self.scale_b))
            expect(shredgen._get_scale_by_name('C')).to(equal(self.scale_c))

        with it('returns None when none of the scales have an alias that matches the give scale'):
            expect(shredgen._get_scale_by_name('x')).to(be_none)

    with description(shredgen._get_tuned_scale):
        with before.each:
            self.scales = [mock(shredgen.Scale) for _ in range(0, 11)]
            when(shredgen)._get_key_offset(...).thenReturn(3)
            when(shredgen)._get_all_scales_of_type(...).thenReturn(self.scales)

        with it('returns the given scale when the key offset is zero'):
            scale = mock(shredgen.Scale)
            when(shredgen)._get_key_offset(...).thenReturn(0)
            expect(shredgen._get_tuned_scale(scale, 'C')).to(equal(scale))

        with it('returns the scale at the determined offset'):
            when(shredgen)._get_key_offset(...).thenReturn(3)
            expect(shredgen._get_tuned_scale(self.scales[1], 'C')).to(equal(self.scales[4]))

        with it('returns the scale at the wrapped offset if the offset index is greater than the number of notes in an octive'):
            when(shredgen)._get_key_offset(...).thenReturn(len(self.scales) + 1)
            expect(shredgen._get_tuned_scale(self.scales[1], 'C')).to(equal(self.scales[2]))

        with it('throws an exit code error when the other scales of the same type do not contain the given scale'):
            when(shredgen)._get_all_scales_of_type(...).thenReturn(self.scales)
            expect(lambda: shredgen._get_tuned_scale(mock(shredgen.Scale), 'C')).to(raise_error(shredgen.ExitCodeError))

        with it('throws an exit code error when the other scales of the same type are None'):
            when(shredgen)._get_all_scales_of_type(...).thenReturn(None)
            expect(lambda: shredgen._get_tuned_scale(mock(shredgen.Scale), 'C')).to(raise_error(shredgen.ExitCodeError))

    with description(shredgen._get_all_scales_of_type):
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

    with description(shredgen._get_all_scales):
        with before.each:
            self.maj_pen_1 = mock(shredgen.MajorPentatonicScale)
            self.maj_pen_2 = mock(shredgen.MajorPentatonicScale)

            when(shredgen)._get_major_pentatonic_scales().thenReturn([self.maj_pen_1, self.maj_pen_2])

        with it('returns the major pentatonic scales'):
            expect(shredgen._get_all_scales()).to(equal([self.maj_pen_1, self.maj_pen_2]))

    with description(shredgen._get_major_pentatonic_scales):
        with it('returns a scale for each key'):
            expect(len(shredgen._get_major_pentatonic_scales())).to(equal(12))

        with it('returns a major pentatonic scale for each key'):
            for scale in shredgen._get_major_pentatonic_scales():
                expect(isinstance(scale, shredgen.MajorPentatonicScale))

    with description(shredgen._get_key_offset):
        with it('returns key #2 number - key #1 number'):
            when(shredgen)._get_key_num('foo').thenReturn(5)
            when(shredgen)._get_key_num('bar').thenReturn(7)
            expect(shredgen._get_key_offset('foo', 'bar')).to(equal(2))

    with description(shredgen._get_key_num):
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


    with description(shredgen._basename):
        with before.each:
            when(os.path).basename(...).thenReturn('basename')

        with it('returns the the basename'):
            expect(shredgen._basename()).to(equal('basename'))
