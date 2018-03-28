#!/usr/bin/env python3


_NOTES_IN_OCTAVE = 12


def main():
    for scale in _create_major_pentatonic_scales():
        atab = ASCIITab(scale.notes)
        print('{}\n{}\n\n'.format(scale.name, atab), end='')


def _create_major_pentatonic_scales():
    a_maj_pen = MajorPentatonicScale('A', [
        Note('E', 5), Note('E', 6), Note('E', 8),
        Note('A', 5), Note('A', 7), Note('A', 8),
        Note('D', 5), Note('D', 7), Note('D', 8),
        Note('G', 5), Note('G', 7),
        Note('B', 5), Note('B', 6), Note('B', 8),
        Note('e', 5), Note('e', 6), Note('e', 8),
    ])

    scales = [a_maj_pen]
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 1, 'A#'))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 2, 'B'))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 3, 'C'))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 4, 'C#', wrap=False))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 5, 'D', wrap=False))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 6, 'D#', wrap=False))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 7, 'E'))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 8, 'F'))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 9, 'F#'))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 10, 'G'))
    scales.append(MajorPentatonicScale.from_other(a_maj_pen, 11, 'G#'))

    return scales


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
