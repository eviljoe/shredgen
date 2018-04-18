# pylint: disable=invalid-name,line-too-long,no-member,protected-access


import argparse
import builtins
import os.path
import random
import sys

from expects import be, be_empty, be_none, expect, equal, raise_error
from mamba import after, before, description, it
from mockito import arg_that, mock, unstub, when, verify

import shredgen


with description(shredgen) as self:
    with after.each:
        unstub()

    with description(shredgen.main):
        with before.each:
            self.opts = mock({})
            when(shredgen)._parse_opts(...).thenReturn(self.opts)
            when(shredgen)._update_default_opts(...)
            when(shredgen)._perform_user_action(...)
            when(shredgen)._print_err_and_usage(...)
            when(sys).exit(...)

        with it('parses the options'):
            shredgen.main()
            verify(shredgen)._parse_opts()

        with it('updates the default options'):
            shredgen.main()
            verify(shredgen)._update_default_opts(self.opts)

        with it('performs the user action'):
            shredgen.main()
            verify(shredgen)._perform_user_action(self.opts)

        with it('prints the error & usage when an error is raised'):
            err = shredgen.ExitCodeError('foo', 7)
            when(shredgen)._perform_user_action(...).thenRaise(err)
            shredgen.main()
            verify(shredgen)._print_err_and_usage(err)

        with it('exits with the code from the error when there is an error'):
            when(shredgen)._perform_user_action(...).thenRaise(shredgen.ExitCodeError('foo', 7))
            shredgen.main()
            verify(sys).exit(7)

        with it('exits with zero when there is no error'):
            shredgen.main()
            verify(sys).exit(0)

    with description(shredgen._parse_opts):
        with it('returns the parsed arguments'):
            parser = mock(argparse.ArgumentParser)
            args = mock({'foo': 'bar'})

            when(parser).add_argument(...)
            when(parser).parse_args(...).thenReturn(args)
            when(argparse).ArgumentParser(...).thenReturn(parser)

            expect(shredgen._parse_opts()).to(be(args))

    with description(shredgen._update_default_opts):
        with before.each:
            self.opts = mock({'length': None})

        with it('sets the length to the default length when the length is None'):
            self.opts.length = None
            shredgen._update_default_opts(self.opts)
            expect(self.opts.length).to(equal(shredgen._DEFAULT_LENGTH))

        with it('does not set the length to the default length whtn the length is an empty string'):
            self.opts.length = ''
            shredgen._update_default_opts(self.opts)
            expect(self.opts.length).to(be_empty)

        with it('does not set the length to the default length whtn the length is a non-emtpy string'):
            self.opts.length = 'foo'
            shredgen._update_default_opts(self.opts)
            expect(self.opts.length).to(equal('foo'))

    with description(shredgen._perform_user_action):
        def opts(_self, all_scales=True, all_scale_names=True, only_tune=True):
            return mock({
                'all_scales': all_scales,
                'all_scale_names': all_scale_names,
                'only_tune': only_tune
            })

        with before.each:
            when(shredgen)._display_all_scales(...)
            when(shredgen)._display_all_scale_names(...)
            when(shredgen)._display_tuning(...)
            when(shredgen)._shred(...)

        with it('displays all the scales when that flag is true'):
            shredgen._perform_user_action(self.opts())
            verify(shredgen)._display_all_scales()

        with it('displays all scale names when that is the first true option'):
            shredgen._perform_user_action(self.opts(all_scales=False))
            verify(shredgen)._display_all_scale_names()

        with it('displays the tuning when that is the first true option'):
            opts = self.opts(all_scales=False, all_scale_names=False)
            shredgen._perform_user_action(opts)
            verify(shredgen)._display_tuning(opts)

        with it('shreds when all options are false'):
            opts = self.opts(all_scales=False, all_scale_names=False, only_tune=False)
            shredgen._perform_user_action(opts)
            verify(shredgen)._shred(opts)

    with description(shredgen._display_all_scales):
        def scale(_self, name, notes):
            return mock({'name': name, 'notes': notes}, spec=shredgen.Scale)

        with before.each:
            scale_a = self.scale('Scale A', ['a', 'aa', 'aaa'])
            scale_b = self.scale('Scale B', ['b', 'bb', 'bbb'])
            scale_c = self.scale('Scale C', ['c', 'cc', 'ccc'])

            atab_a = mock({'__str__': lambda: 'ascii tab a'}, spec=shredgen.ASCIITab)
            atab_b = mock({'__str__': lambda: 'ascii tab b'}, spec=shredgen.ASCIITab)
            atab_c = mock({'__str__': lambda: 'ascii tab c'}, spec=shredgen.ASCIITab)

            when(shredgen).ASCIITab(scale_a.notes).thenReturn(atab_a)
            when(shredgen).ASCIITab(scale_b.notes).thenReturn(atab_b)
            when(shredgen).ASCIITab(scale_c.notes).thenReturn(atab_c)

            when(shredgen)._get_all_scales(...).thenReturn([scale_a, scale_b, scale_c])
            when(builtins).print(...)

        with it('displays the scale name & ASCII tab for each scale'):
            shredgen._display_all_scales()
            verify(builtins).print(
                'Scale A\n'
                'ascii tab a\n\n'
                'Scale B\n'
                'ascii tab b\n\n'
                'Scale C\n'
                'ascii tab c'
            )

    with description(shredgen._display_tuning):
        def scale(_self, name, notes): # pylint: disable=function-redefined
            return mock({'name': name, 'notes': notes}, spec=shredgen.Scale)

        with before.each:
            self.opts = mock({'scale': ' \t\r\nFoO\n\r\t ', 'tuning': 'T'})
            self.orig_scale = self.scale('scale, original', ['a', 'aa', 'aaa'])
            self.tune_scale = self.scale('scale, tuned', ['b', 'bb', 'bbb'])

            orig_atab = mock({'__str__': lambda: 'ascii tab original'}, spec=shredgen.ASCIITab)
            tune_atab = mock({'__str__': lambda: 'ascii tab tuned'}, spec=shredgen.ASCIITab)

            when(shredgen).ASCIITab(self.orig_scale.notes).thenReturn(orig_atab)
            when(shredgen).ASCIITab(self.tune_scale.notes).thenReturn(tune_atab)

            when(shredgen)._validate_scale_name(...)
            when(shredgen)._validate_scale(...)
            when(shredgen)._get_scale_by_name(...).thenReturn(self.orig_scale)
            when(shredgen)._get_tuned_scale(...).thenReturn(self.tune_scale)
            when(builtins).print(...)

        with it('validates the stripped and lowered scale name when the opts has a scale'):
            shredgen._display_tuning(self.opts)
            verify(shredgen)._validate_scale_name('foo')

        with it('validates the scale name as an empty string when the opts has no scale'):
            self.opts.scale = None
            shredgen._display_tuning(self.opts)
            verify(shredgen)._validate_scale_name('')

        with it('gets and validates the scale by name'):
            shredgen._display_tuning(self.opts)
            verify(shredgen)._validate_scale(self.opts, self.orig_scale)

        with it('gets the tuned scale'):
            shredgen._display_tuning(self.opts)
            verify(shredgen)._get_tuned_scale(self.orig_scale, 'T')

        with it('dispalys the original scale & the tuned scales'):
            shredgen._display_tuning(self.opts)
            verify(builtins).print(
                'Original Scale: scale, original\n'
                'ascii tab original\n\n'
                'Tuned Scale: scale, tuned\n'
                'ascii tab tuned'
            )

    with description(shredgen._display_all_scale_names):
        def scale(_self, name, aliases): # pylint: disable=function-redefined
            return mock({'name': name, 'aliases': aliases}, spec=shredgen.Scale)

        with before.each:
            scale_a = self.scale('Scale A', ['a', 'aa', 'aaa'])
            scale_b = self.scale('Scale B', ['b', 'bb', 'bbb'])
            scale_c = self.scale('Scale C', ['c', 'cc', 'ccc'])
            when(shredgen)._get_all_scales(...).thenReturn([scale_a, scale_b, scale_c])
            when(builtins).print(...)

        with it('displays the scale name & aliases for each scale'):
            shredgen._display_all_scale_names()
            verify(builtins).print(
                'Scale A (a, aa, aaa)\n'
                'Scale B (b, bb, bbb)\n'
                'Scale C (c, cc, ccc)'
            )

    with description(shredgen._shred):
        with before.each:
            self.opts = mock({
                'scale': ' \t\r\nFoO\n\r\t ',
                'length': ' \t\r\n5\n\r\t '
            })
            self.scale = mock(shredgen.Scale)
            when(shredgen)._get_scale_by_name(...).thenReturn(self.scale)
            when(shredgen)._validate_scale_name(...)
            when(shredgen)._validate_scale(...)
            when(shredgen)._validate_length(...)
            when(shredgen)._shred_in_scale(...)

        with it('validates the scale stripped and lowered name when the opts has a scale'):
            shredgen._shred(self.opts)
            verify(shredgen)._validate_scale_name('foo')

        with it('validates the scale name as an empty string when opts have no scale'):
            self.opts.scale = None
            shredgen._shred(self.opts)
            verify(shredgen)._validate_scale_name('')

        with it('validates the scale'):
            shredgen._shred(self.opts)
            when(shredgen)._get_scale_by_name('foo').thenReturn(self.scale)
            verify(shredgen)._validate_scale(self.opts, self.scale)

        with it('validates the stripped length'):
            shredgen._shred(self.opts)
            verify(shredgen)._validate_length('5')

        with it('shreds in the scale'):
            shredgen._shred(self.opts)
            verify(shredgen)._shred_in_scale(self.scale, 5)

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
