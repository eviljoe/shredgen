#!/usr/bin/env python3


import argparse
import sys


_NOTES_IN_OCTAVE = 12

_ERR_NO_SCALE_SPECIFIED = 2
_ERR_UNKNOWN_SCALE = 3


def main():
    opts = _parse_opts()
    err = _perform_user_action(opts)
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

    # TODO add --length option to specify how many notes generate when shredding

    return parser.parse_args()


def _perform_user_action(opts):
    err = None

    if opts.all_scales:
        _display_all_scales()
    elif opts.all_scale_names:
        _display_all_scale_names()
    else:
        err = _shred(opts)

    return err


def _display_all_scales():
    print('\n\n'.join(['{}\n{}'.format(scale.name, ASCIITab(scale.notes)) for scale in _get_all_scales()]))


def _display_all_scale_names():
    print('\n'.join(['{} ({})'.format(scale.name, ', '.join(scale.aliases)) for scale in _get_all_scales()]))


def _shred(opts):
    err = None
    scale_name = opts.scale.strip().lower() if opts.scale else ''
    scale = None

    if len(scale_name) == 0:
        err = _ERR_NO_SCALE_SPECIFIED
        # TODO todo print err msg

    if err is None:
        scale = _get_scale_by_name(scale_name)

        if not scale:
            err = _ERR_UNKNOWN_SCALE
            # TODO todo print err msg

    if err is None:
        _shred_in_scale(scale)

    return err


def _shred_in_scale(scale):
    # TODO todo shred in scale
    print('TODO: shred in this scale...')
    print(str(ASCIITab(scale.notes)))


def _get_scale_by_name(name):
    return next((scale for scale in _get_all_scales() if name in [alias.lower() for alias in scale.aliases]), None)


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


class Note:
    def __init__(self, string, fret):
        self.string = string
        self.fret = fret

    def __str__(self):
        return self.string + str(self.fret)

    def offset(self, offset, wrap=True):
        offset_fret = self.fret + offset

        if wrap:
            offset_fret %= _NOTES_IN_OCTAVE

        return Note(self.string, offset_fret)


class Scale:
    def __init__(self, name, aliases, notes):
        self.name = name
        self.aliases = aliases
        self.notes = notes

    def __str__(self):
        return '{} {{{}}}'.format(self.name, ', '.join(str(n) for n in self.notes))


class MajorPentatonicScale(Scale):
    def __init__(self, key, notes):
        super().__init__('{} Major Pentatonic'.format(key), self._get_aliases_for_key(key), notes)

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


if __name__ == '__main__':
    main()
