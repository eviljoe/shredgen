#!/usr/bin/env python3


import argparse
import os.path
import random
import sys

_NOTES_IN_OCTAVE = 12
_DEFAULT_LENGTH = 16
_DEFAULT_TUNING = 'A'

_KEYS = [
    ['A'],
    ['A#', 'A sharp', 'ASharp', 'Bb', 'B Flat', 'BFlat'],
    ['B'],
    ['C'],
    ['C#', 'C Sharp', 'CSharp', 'Db', 'D Flat', 'DFlat'],
    ['D'],
    ['D#', 'D Sharp', 'DSharp', 'Eb', 'E Flat', 'EFlat'],
    ['E'],
    ['F'],
    ['F#', 'F Sharp', 'FSharp', 'Gb', 'G Flat', 'GFlat'],
    ['G'],
    ['G#', 'G Sharp', 'GSharp', 'Ab', 'A Flat', 'AFlat']
]

_ERR_NO_SCALE_SPECIFIED = 2
_ERR_UNKNOWN_SCALE = 3
_ERR_LENGTH_NOT_INT = 4
_ERR_LENGTH_TOO_LOW = 5
_ERR_INVALID_KEY = 6
_ERR_CANT_FIND_SCALES_OF_TYPE = 7


def main():
    err = None

    try:
        opts = _parse_opts()
        _update_default_opts(opts)
        _perform_user_action(opts)
    except ExitCodeError as e:
        err = e.err_code
        _print_err_and_usage(e)

    sys.exit(0 if err is None else err)


def _parse_opts():
    parser = argparse.ArgumentParser(description='Generate boring rifts that solidify faces')

    # Positional Arguments
    parser.add_argument('scale', nargs='?', metavar='scale', default='AMajPen',
                        help='The scale to be used (default: %(default)s)')

    # Optional Arguments
    parser.add_argument('--all-scales', action='store_true', default=False, dest='all_scales',
                        help='Display all possible scales')
    parser.add_argument('--all-scale-names', action='store_true', default=False, dest='all_scale_names',
                        help='Display all possible scale names')
    parser.add_argument('--length', '-l', default=_DEFAULT_LENGTH, dest='length',
                        help='Number of notes to generate (default: %(default)s)')
    parser.add_argument('--only-tune', action='store_true', default=False, dest='only_tune',
                        help='Do not shred.  Instead, show the scale that will be used based on the requested scale '
                             'and tuning (default: %(default)s).')
    parser.add_argument('--tuning', '-t', default=_DEFAULT_TUNING, dest='tuning',
                        help='Guitar tuning key (default: %(default)s)')

    return parser.parse_args()


def _update_default_opts(opts):
    opts.length = _DEFAULT_LENGTH if opts.length is None else opts.length


def _perform_user_action(opts):
    if opts.all_scales:
        _display_all_scales(opts)
    elif opts.all_scale_names:
        _display_all_scale_names()
    elif opts.only_tune:
        _display_tuning(opts)
    else:
        _shred(opts)


def _display_all_scales(opts):
    if _get_key_offset(opts.tuning) == 0:
        _display_all_scales_no_tuning()
    else:
        _display_all_scales_with_tuning(opts)


def _display_all_scales_no_tuning():
    print('\n\n'.join(['{}\n{}'.format(scale.name, ASCIITab(scale.notes)) for scale in _get_all_scales()]))


def _display_all_scales_with_tuning(opts):
    scale_strs = []

    for scale in _get_all_scales():
        tuned_scale = _get_tuned_scale(scale, opts.tuning)

        scale_str = 'Original Scale: {}\n{}'.format(scale.name, ASCIITab(scale.notes))
        tuned_str = 'Tuned Scale: {}\n{}'.format(tuned_scale.name, ASCIITab(tuned_scale.notes))

        scale_strs.append(_join_multiline_strings(scale_str, tuned_str))

    print('\n\n'.join(scale_strs))


def _display_all_scale_names():
    print('\n'.join(['{} ({})'.format(scale.name, ', '.join(scale.aliases)) for scale in _get_all_scales()]))


def _display_tuning(opts):
    scale_name = opts.scale.strip().lower() if opts.scale else ''
    _validate_scale_name(scale_name)

    scale = _get_scale_by_name(scale_name)
    _validate_scale(opts, scale)

    tuned_scale = _get_tuned_scale(scale, opts.tuning)

    print('Original Scale: {}\n{}\n\nTuned Scale: {}\n{}'.format(
        scale.name,
        ASCIITab(scale.notes),
        tuned_scale.name,
        ASCIITab(tuned_scale.notes)))


def _shred(opts):
    scale_name = opts.scale.strip().lower() if opts.scale else ''
    _validate_scale_name(scale_name)

    scale = _get_scale_by_name(scale_name)
    _validate_scale(opts, scale)

    length_str = str(opts.length).strip()
    _validate_length(length_str)
    length = int(length_str)

    _shred_in_scale(scale, length)


def _validate_scale_name(scale_name):
    if not scale_name:
        raise ExitCodeError('A scale must be specified.', _ERR_NO_SCALE_SPECIFIED)


def _validate_scale(opts, scale):
    if not scale:
        basename = _basename()
        raise ExitCodeError(
            'Unknown scale: {}\n'
            'To see all supported scale names, execute: {} --all-scale-names\n'
            'To see all supported scales, execute: {} --all-scales'.format(opts.scale, basename, basename),
            _ERR_UNKNOWN_SCALE)


def _validate_length(length):
    try:
        length = int(length, 10)
    except ValueError as e:
        raise ExitCodeError('Length must be an integer.', _ERR_LENGTH_NOT_INT) from e

    if length < 1:
        raise ExitCodeError('Length must be greater than zero', _ERR_LENGTH_TOO_LOW)


def _shred_in_scale(scale, length):
    scale_notes_len = len(scale.notes)
    print(ASCIITab([scale.notes[random.randrange(scale_notes_len)] for _ in range(length)]))


def _get_scale_by_name(name):
    name = name.lower()
    return next((scale for scale in _get_all_scales() if name in [alias.lower() for alias in scale.aliases]), None)


def _get_tuned_scale(scale, tuning_key):
    offset = _get_key_offset(tuning_key)
    adjusted_scale = scale

    if offset != 0:
        all_scales = _get_all_scales_of_type(scale) or []

        try:
            starting_index = all_scales.index(scale)
        except ValueError as e:
            raise ExitCodeError(
                'Could not find other scales of same type as this:\n{}'.format(scale),
                _ERR_CANT_FIND_SCALES_OF_TYPE
            ) from e

        adjusted_scale = all_scales[(starting_index + offset) % len(all_scales)]

    return adjusted_scale


def _get_all_scales_of_type(scale):
    all_scales = None

    if isinstance(scale, MajorPentatonicScale):
        all_scales = _get_major_pentatonic_scales()

    return all_scales


def _get_all_scales():
    return _get_major_pentatonic_scales()


def _get_major_pentatonic_scales():
    a_maj_pen = MajorPentatonicScale('A', [
        Note('E', 5), Note('E', 6), Note('E', 8),
        Note('A', 5), Note('A', 7), Note('A', 8),
        Note('D', 5), Note('D', 7), Note('D', 8),
        Note('G', 5), Note('G', 7),
        Note('B', 5), Note('B', 6), Note('B', 8),
        Note('e', 5), Note('e', 6), Note('e', 8),
    ])

    return [
        a_maj_pen,
        MajorPentatonicScale.from_other(a_maj_pen, 1, 'A#'),
        MajorPentatonicScale.from_other(a_maj_pen, 2, 'B'),
        MajorPentatonicScale.from_other(a_maj_pen, 3, 'C'),
        MajorPentatonicScale.from_other(a_maj_pen, 4, 'C#', wrap=False),
        MajorPentatonicScale.from_other(a_maj_pen, 5, 'D', wrap=False),
        MajorPentatonicScale.from_other(a_maj_pen, 6, 'D#', wrap=False),
        MajorPentatonicScale.from_other(a_maj_pen, 7, 'E'),
        MajorPentatonicScale.from_other(a_maj_pen, 8, 'F'),
        MajorPentatonicScale.from_other(a_maj_pen, 9, 'F#'),
        MajorPentatonicScale.from_other(a_maj_pen, 10, 'G'),
        MajorPentatonicScale.from_other(a_maj_pen, 11, 'G#'),
    ]


def _get_key_offset(tuning_key, orig_key='A'):
    return _get_key_num(tuning_key) - _get_key_num(orig_key)


def _get_key_num(key):
    ckey = str(key).lower()
    key_num = next((i for i, names in enumerate(_KEYS) if ckey in [name.lower() for name in names]), None)

    if key_num is None:
        raise ExitCodeError(
            'Invalid key: {}\nKey must be one of: {}'.format(
                key,
                ', '.join([k for keys in _KEYS for k in keys])
            ), _ERR_INVALID_KEY)

    return key_num


def _basename():
    return os.path.basename(sys.argv[0])


def _print_err_and_usage(err):
    print('{}\nFor usage, execute: {} -h'.format(err, _basename()), file=sys.stderr)


def _join_multiline_strings(str1, str2, sep='  '):  # TODO unit test
    lines_1 = str(str1 or '').splitlines()
    lines_2 = str(str2 or '').splitlines()
    line_count_1 = len(lines_1)
    line_count_2 = len(lines_2)
    max_line_length_1 = len(max(lines_1, key=len) if lines_1 else '')
    lines = []

    for x in range(0, max(line_count_1, line_count_2)):
        line = ''

        if x < line_count_1:
            line += lines_1[x].ljust(max_line_length_1, ' ')
        else:
            line += ''.ljust(max_line_length_1, ' ')

        line += sep if sep else ''

        if x < line_count_2:
            line += lines_2[x]

        lines.append(line)

    return '\n'.join(lines)


class Note:
    def __init__(self, string, fret):
        self.string = string
        self.fret = fret

    def __eq__(self, other):
        return (
            Note == other.__class__
            and self.string == other.string
            and self.fret == other.fret
        )

    def __hash__(self):
        return (
            hash(self.string)
            ^ hash(self.fret)
        )

    def __str__(self):
        return self.string + str(self.fret)

    def offset(self, offset, wrap=True):
        offset_fret = self.fret + offset

        if wrap:
            offset_fret %= _NOTES_IN_OCTAVE

        return Note(self.string, offset_fret)


class Scale:
    def __init__(self, name, key, aliases, notes):
        self.name = name
        self.key = key
        self.aliases = aliases
        self.notes = notes

    def __str__(self):
        return '{} {{{}}}'.format(self.name, ', '.join(str(n) for n in self.notes))


class MajorPentatonicScale(Scale):
    def __init__(self, key, notes):
        super().__init__(
            name='{} Major Pentatonic'.format(key),
            key=key,
            aliases=self._get_aliases_for_key(key),
            notes=notes
        )

    def __eq__(self, other):
        return (
            MajorPentatonicScale == other.__class__
            and self.name == other.name
            and set(self.notes) == set(other.notes)
        )

    @staticmethod
    def from_other(other, offset, key, wrap=True):
        return MajorPentatonicScale(key, [n.offset(offset, wrap) for n in other.notes])

    @staticmethod
    def _get_aliases_for_key(key):
        return [
            '{} Major Pentatonic'.format(key),
            '{}MajorPentatonic'.format(key),
            '{} Maj Pen'.format(key),
            '{}MajPen'.format(key),
        ]


class ASCIITab:
    def __init__(self, notes):
        self.notes = notes
        self._strings = ['e', 'B', 'G', 'D', 'A', 'E']

    def __str__(self):
        string_lines = dict()
        for string in self._strings:
            string_lines[string] = []

        for note in self.notes:
            for string, line in string_lines.items():
                placeholder = '-' if note.fret < 10 else '--'
                line.append(str(note.fret) if string == note.string else placeholder)

        return '\n'.join([self._format_string_line(string, string_lines) for string in self._strings])

    @staticmethod
    def _format_string_line(string, string_lines):
        return '{}|-{}-'.format(string, '--'.join(string_lines.get(string)))


class ExitCodeError(Exception):
    def __init__(self, message, err_code):
        super().__init__(message)
        self.err_code = err_code


if __name__ == '__main__':
    main()
