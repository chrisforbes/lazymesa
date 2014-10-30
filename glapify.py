#!/usr/bin/env python2

import sys

outmode = 0
mode = 0
data = ''

def glify(name):
    return 'GL' + name if name not in ('const', 'void') else name

def parse(line):
    global mode
    global data

    if len(line.strip()) and line[0] not in (' ', '\t'):
        mode = 0
        line = line.strip()
        if line == 'New Tokens':
            mode = 1
            data = ''
        if line == 'New Procedures and Functions':
            mode = 2
            data = ''
        if line.startswith('Additions'):
            mode = 3
        return

    if mode == 1:
        parts = line.split('0x')
        if outmode == 0:
            if len(parts) == 2:
                print '<enum name="%s" value="0x%s"/>' % (
                    parts[0].strip(), parts[1].split(' ')[0].strip())

    if mode == 2:
        data += line.strip()
        # some specs have comments inline in this section
        if data.startswith('/*') and '*/' in data:
            data = data.split('*/', 1)[1]

        if ';' in data:
            xs = data.split('(')
            rettype, fname = xs[0].split(' ')
            args = xs[1].split(')')[0].split(',')

            if outmode == 0:
                print '<function name="%s" offset="assign">' % fname
                if rettype != 'void':
                    print '\t<return type="%s"/>' % glify(rettype)
                for arg in args:
                    argparts = arg.strip().split(' ')
                    isptr = '*' in argparts[-1]
                    print '\t<param name="%s" type="%s%s"/>' % (
                        argparts[-1][1:] if isptr else argparts[-1],
                        ' '.join(glify(z) for z in argparts[:-1]),
                        ' *' if isptr else ''
                        )
                print '</function>'
            else:
                print '%s%s GLAPIENTRY' % (
                    'extern ' if outmode==1 else '',
                    glify(rettype))
                outline = '_mesa_%s(' % fname
                indent = len(outline)

                for arg in args:
                    argparts = arg.strip().split(' ')
                    argstr = '%s %s' % (
                        ' '.join(glify(z) for z in argparts[:-1]),
                        argparts[-1])

                    if len(outline + argstr) > 80:
                        print outline + ','
                        outline = ' ' * indent + argstr
                    else:
                        outline += ('' if outline.endswith('(') else ', ') + argstr

                print outline + ')%s' % (';' if outmode==1 else '')
                if outmode == 2:
                    print '{'
                    print '   GET_CURRENT_CONTEXT(ctx);'
                    print '   _mesa_error(ctx, GL_INVALID_OPERATION, "gl%s\\n");' % fname
                    if rettype != 'void':
                        print '   return -1;'
                    print '}'

                print ''

            data = ''

def main():
    global outmode
    filename = None
    for arg in sys.argv[1:]:
        if '-x' == arg:
            outmode = 0
        elif '-h' == arg:
            outmode = 1
        elif '-c' == arg:
            outmode = 2
        else:
            filename = arg

    if not filename:
        print 'usage: glapify.py [-xhc] specfile'
        return

    with open(filename, 'r') as f:
        for line in f:
            parse(line)
            if mode == 3:
                return

if __name__ == '__main__':
    main()
