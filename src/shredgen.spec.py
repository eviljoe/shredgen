# pylint: disable=invalid-name,line-too-long,no-member,protected-access


import argparse
import builtins
import os.path
import random
import sys

from expects import be, be_empty, be_none, expect, equal, raise_error
from mamba import after, before, description, it
from mockito import mock, unstub, when, verify
from mockito.matchers import arg_that

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
            opts = self.opts()
            shredgen._perform_user_action(opts)
            verify(shredgen)._display_all_scales(opts)

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
        with before.each:
            self.opts = mock({'tuning': 'A'})
            when(shredgen)._display_all_scales_no_tuning()
            when(shredgen)._display_all_scales_with_tuning(...)

        with it('displays the scales without tuning when the key offset is zero'):
            when(shredgen)._get_key_offset(...).thenReturn(0)
            shredgen._display_all_scales(self.opts)
            verify(shredgen)._display_all_scales_no_tuning()

        with it('displays the scales with tuning when the key offset is not zero'):
            when(shredgen)._get_key_offset(...).thenReturn(1)
            shredgen._display_all_scales(self.opts)
            verify(shredgen)._display_all_scales_with_tuning(self.opts)

    with description(shredgen._display_all_scales_no_tuning):
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
            shredgen._display_all_scales_no_tuning()
            verify(builtins).print(
                'Scale A\n'
                'ascii tab a\n\n'
                'Scale B\n'
                'ascii tab b\n\n'
                'Scale C\n'
                'ascii tab c'
            )

    with description(shredgen._display_all_scales_with_tuning):
        with before.each:
            scale_a = mock({'name': 'Scale A', 'notes': ['a']}, spec=shredgen.Scale)
            scale_b = mock({'name': 'Scale B', 'notes': ['b']}, spec=shredgen.Scale)
            scale_a_tuned = mock({'name': 'Scale A Tuned', 'notes': ['x']}, spec=shredgen.Scale)
            scale_b_tuned = mock({'name': 'Scale B Tuned', 'notes': ['y']}, spec=shredgen.Scale)

            atab_a = mock({'__str__': lambda: 'ascii tab a'}, spec=shredgen.ASCIITab)
            atab_b = mock({'__str__': lambda: 'ascii tab b'}, spec=shredgen.ASCIITab)
            atab_a_tuned = mock({'__str__': lambda: 'ascii tab a tuned'}, spec=shredgen.ASCIITab)
            atab_b_tuned = mock({'__str__': lambda: 'ascii tab b tuned'}, spec=shredgen.ASCIITab)

            when(shredgen)._get_all_scales().thenReturn([scale_a, scale_b])
            when(shredgen)._get_tuned_scale(scale_a, 'C').thenReturn(scale_a_tuned)
            when(shredgen)._get_tuned_scale(scale_b, 'C').thenReturn(scale_b_tuned)
            when(shredgen).ASCIITab(scale_a.notes).thenReturn(atab_a)
            when(shredgen).ASCIITab(scale_b.notes).thenReturn(atab_b)
            when(shredgen).ASCIITab(scale_a_tuned.notes).thenReturn(atab_a_tuned)
            when(shredgen).ASCIITab(scale_b_tuned.notes).thenReturn(atab_b_tuned)

            when(shredgen)._join_multiline_strings(
                'Original Scale: Scale A\nascii tab a',
                'Tuned Scale: Scale A Tuned\nascii tab a tuned'
            ).thenReturn('joined Scale A & Scale A Tuned')
            when(shredgen)._join_multiline_strings(
                'Original Scale: Scale B\nascii tab b',
                'Tuned Scale: Scale B Tuned\nascii tab b tuned'
            ).thenReturn('joined Scale B & Scale B Tuned')

            when(builtins).print(...)

        with it('displays the original scale & tuned scale for each scale'):
            shredgen._display_all_scales_with_tuning(mock({'tuning': 'C'}))
            verify(builtins).print(
                'joined Scale A & Scale A Tuned\n\n'
                'joined Scale B & Scale B Tuned'
            )

    with description(shredgen._display_tuning):
        def scale(_self, name, notes):  # pylint: disable=function-redefined
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
        def scale(_self, name, aliases):  # pylint: disable=function-redefined
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

        with it('returns the scale at the wrapped offset if the offset index is greater than the number of notes in an '
                'octave'):
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
            expect(shredgen._get_key_offset(orig_key='foo', tuning_key='bar')).to(equal(2))

        with it('uses the key of "A" when given no original key'):
            when(shredgen)._get_key_num('A').thenReturn(5)
            when(shredgen)._get_key_num('bar').thenReturn(7)
            expect(shredgen._get_key_offset(tuning_key='bar')).to(equal(2))

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

    with description(shredgen._join_multiline_strings):
        with before.each:
            self.str_a = 'abc\ndefgh\nij'
            self.str_b = '1234\n567\n89'
            self.str_c = 'foo\nbar'

        with it('displays the strings with their lines side by side'):
            expect(shredgen._join_multiline_strings(self.str_a, self.str_b, sep=' | ')).to(equal(
                'abc   | 1234\n'
                'defgh | 567\n'
                'ij    | 89'
            ))

        with it('keeps the strings aligned when the first string has more lines than the second string'):
            expect(shredgen._join_multiline_strings(self.str_a, self.str_c, sep=' | ')).to(equal(
                'abc   | foo\n'
                'defgh | bar\n'
                'ij    | '
            ))

        with it('keeps the strings aligned when the first string has less lines than the second string'):
            expect(shredgen._join_multiline_strings(self.str_c, self.str_a, sep=' | ')).to(equal(
                'foo | abc\n'
                'bar | defgh\n'
                '    | ij'
            ))

        with it('displays the first string as empty when it is None'):
            expect(shredgen._join_multiline_strings(None, self.str_a, sep=' | ')).to(equal(
                ' | abc\n'
                ' | defgh\n'
                ' | ij'
            ))

        with it('displays the second string as empty when it is None'):
            expect(shredgen._join_multiline_strings(self.str_a, None, sep=' | ')).to(equal(
                'abc   | \n'
                'defgh | \n'
                'ij    | '
            ))

    with description(shredgen.Note):
        with description(shredgen.Note.__eq__):
            def note(_self, string='A', fret=1):
                return shredgen.Note(string, fret)


            with it('returns true when given an equal note'):
                expect(self.note()).to(equal(self.note()))

            with it('returns false when given a note with a different string'):
                expect(self.note()).not_to(equal(self.note(string='x')))

            with it('returns false when given a note with a different fret'):
                expect(self.note()).not_to(equal(self.note(fret=-1)))

        with description(shredgen.Note.__hash__):
            def note(_self, string='A', fret=1):
                return shredgen.Note(string, fret)


            with it('returns the same hash for notes that have the same values'):
                expect(hash(self.note())).to(equal(hash(self.note())))

            with it('returns a different has for a note with a different string'):
                expect(hash(self.note())).not_to(equal(hash(self.note(string='x'))))

            with it('returns a different has for a note with a different fret'):
                expect(hash(self.note())).not_to(equal(hash(self.note(fret=-1))))

        with description(shredgen.Note.__str__):
            with it('returns a user readable represention of the note'):
                expect(str(shredgen.Note('A', 1))).to(equal('A1'))

        with description(shredgen.Note.offset):
            with it('returns an equal note when the offset is zero'):
                expect(shredgen.Note('A', 1).offset(0)).to(equal(shredgen.Note('A', 1)))

            with it('returns an equal note when wrapping and the offset is the number of notes in an octave'):
                expect(shredgen.Note('A', 1).offset(shredgen._NOTES_IN_OCTAVE)).to(equal(shredgen.Note('A', 1)))

            with it('returns a note whose fret is offset by the given amount'):
                expect(shredgen.Note('A', 1).offset(5)).to(equal(shredgen.Note('A', 6)))

            with it('can wrap when given an offset that would cause to fret to be greater than the number of notes in '
                    'an octave'):
                expect(shredgen.Note('A', 1).offset(shredgen._NOTES_IN_OCTAVE + 2)).to(equal(shredgen.Note('A', 3)))

            with it('does not wrap when it is turned off'):
                expect(shredgen.Note('A', 1).offset(shredgen._NOTES_IN_OCTAVE + 2, wrap=False)).to(
                    equal(shredgen.Note('A', 15))
                )

    with description(shredgen.Scale):
        with description(shredgen.Scale.__str__):
            with it('returns a user readable represention of the scale'):
                scale = shredgen.Scale(name='Test Scale', key='X', aliases=['ts', 'tscale'], notes=[
                    shredgen.Note('A', 1),
                    shredgen.Note('B', 2),
                    shredgen.Note('C', 3)
                ])
                expect(str(scale)).to(equal('Test Scale {A1, B2, C3}'))

    with description(shredgen.MajorPentatonicScale):
        with description(shredgen.MajorPentatonicScale.__eq__):
            def mps(_self, key='Test', notes=None):
                if notes is None:
                    notes = [shredgen.Note('A', 1), shredgen.Note('B', 2), shredgen.Note('C', 3)]

                return shredgen.MajorPentatonicScale(key, notes)


            with it('returns true when given two scales that have the same name and notes'):
                expect(self.mps()).to(equal(self.mps()))

            with it('returns false when given two scales with different keys'):
                expect(self.mps()).not_to(equal(self.mps(key='x')))

            with it('returns false when given two scales with different notes'):
                notes = [
                    shredgen.Note('a', 1),
                    shredgen.Note('b', 2),
                    shredgen.Note('c', 3)
                ]
                expect(self.mps()).not_to(equal(self.mps(notes=notes)))

            with it('returns true when given two scales with the same notes in different orders notes'):
                notes = [
                    shredgen.Note('C', 3),
                    shredgen.Note('A', 1),
                    shredgen.Note('B', 2)
                ]
                expect(self.mps()).to(equal(self.mps(notes=notes)))

        with description(shredgen.MajorPentatonicScale.from_other):
            with it('returns a new scale with each note from the given scale at the given offset'):
                note_a = shredgen.Note('a', 1)
                note_b = shredgen.Note('b', 1)
                note_c = shredgen.Note('c', 1)

                note_a_off = shredgen.Note('a', 2)
                note_b_off = shredgen.Note('b', 2)
                note_c_off = shredgen.Note('c', 2)

                when(note_a).offset(3, True).thenReturn(note_a_off)
                when(note_b).offset(3, True).thenReturn(note_b_off)
                when(note_c).offset(3, True).thenReturn(note_c_off)

                scale_1 = shredgen.MajorPentatonicScale('a', [note_a, note_b, note_c])
                scale_2 = shredgen.MajorPentatonicScale.from_other(scale_1, 3, 'b')

                expect(scale_2.key).to(equal('b'))
                expect(scale_2.notes).to(equal([note_a_off, note_b_off, note_c_off]))

        with description(shredgen.MajorPentatonicScale._get_aliases_for_key):
            with it('returns the aliases'):
                expect(shredgen.MajorPentatonicScale._get_aliases_for_key('x')).to(equal([
                    'x Major Pentatonic',
                    'xMajorPentatonic',
                    'x Maj Pen',
                    'xMajPen',
                ]))

    with description(shredgen.ASCIITab):
        with it('prints the notes in ASCII tab format'):
            expect(str(shredgen.ASCIITab([
                shredgen.Note('e', 13),
                shredgen.Note('B', 4),
                shredgen.Note('G', 6),
                shredgen.Note('D', 2),
                shredgen.Note('A', 11),
                shredgen.Note('E', 0),
            ]))).to(equal(
                'e|-13-----------------\n'
                'B|-----4--------------\n'
                'G|--------6-----------\n'
                'D|-----------2--------\n'
                'A|--------------11----\n'
                'E|------------------0-'
            ))

        with it('prints an empty ASCII tab when the given no notes'):
            expect(str(shredgen.ASCIITab([]))).to(equal(
                'e|--\n'
                'B|--\n'
                'G|--\n'
                'D|--\n'
                'A|--\n'
                'E|--'
            ))
