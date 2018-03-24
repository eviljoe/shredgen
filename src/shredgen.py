#!/usr/bin/env python3


_NOTES_IN_OCTAVE = 12


def main():
    a_maj_pen = MajorPentatonicScale('A', [
        Note('e', 5), Note('e', 6), Note('e', 8),
        Note('B', 5), Note('B', 6), Note('B', 8),
        Note('G', 5), Note('G', 7),
        Note('D', 5), Note('D', 7), Note('D', 8),
        Note('A', 5), Note('A', 7), Note('A', 8),
        Note('E', 5), Note('E', 6), Note('E', 8),
    ])

    as_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 1, 'A#')
    b_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 2, 'B')
    c_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 3, 'C')
    cs_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 4, 'C#', dont_wrap=['D'])
    d_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 5, 'D', dont_wrap=['D'])
    ds_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 6, 'D#', dont_wrap=['D'])
    e_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 7, 'E')
    f_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 8, 'F')
    fs_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 9, 'F#')
    g_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 10, 'G')
    gs_maj_pen = MajorPentatonicScale.from_other(a_maj_pen, 11, 'G#')

    print(a_maj_pen)
    print(as_maj_pen)
    print(b_maj_pen)
    print(c_maj_pen)
    print(cs_maj_pen)
    print(d_maj_pen)
    print(ds_maj_pen)
    print(e_maj_pen)
    print(f_maj_pen)
    print(fs_maj_pen)
    print(g_maj_pen)
    print(gs_maj_pen)


class Note:
    def __init__(self, string, fret):
        self.string = string
        self.fret = fret

    def __str__(self):
        return self.string + str(self.fret)

    def offset(self, offset, dont_wrap=None):
        if dont_wrap is None:
            dont_wrap = set()

        offset_fret = self.fret + offset
        if self.string not in dont_wrap:
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
        super().__init__('{} Major Pentatonic'.format(key), MajorPentatonicScale._get_aliases(key), notes)

    @staticmethod
    def from_other(other, offset, key, dont_wrap=None):
        return MajorPentatonicScale(key, [n.offset(offset, dont_wrap) for n in other.notes])

    @staticmethod
    def _get_aliases(key):
        return [
            '{} Major Pentatonic'.format(key),
            '{}MajorPentatonic'.format(key),
            '{} Maj Pen'.format(key),
            '{}MajPen'.format(key),
        ]


if __name__ == '__main__':
    main()
