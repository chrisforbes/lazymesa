#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os

basepath = 'tests/spec'

def ext_dir(ext):
    return basepath + '/' + ext.lower()

def do_ext_dirs(ext):
    try:
        os.mkdir(ext_dir(ext))
    except OSError:
        pass    # already created

def create_file(path, content):
    try:
        with open(path, 'r') as f_test:
            pass
    except IOError:
        with open(path, 'w') as f:
            f.write(content)

def is_line_in_file(path, content):
    with open(path, 'r') as f:
        for line in f:
            if line.strip() == content.strip():
                return True
    return False

def ensure_line_in_file(path, content):
    if not is_line_in_file(path, content):
        with open(path, 'a') as f:
            f.write(content)

def ensure_line_in_section(path, start_section, end_section, content):
    ensure_line_in_file(path, start_section)
    if is_line_in_file(path, content):
        return

    in_section = False

    with open(path, 'r') as f_in:
        with open(path+'.temp', 'w') as f_out:
            for line in f_in:
                # put this line before the end_section match.
                if in_section and line.strip() == end_section.strip():
                    f_out.write(content)
                    in_section = False

                f_out.write(line)

                if line.strip() == start_section.strip():
                    in_section = True
            # didnt find the end of the section, so stick it right on the end
            if in_section:
                f_out.write(content)

    os.rename(path+'.temp', path)

# tests/spec/$ext/CMakeLists.txt
ext_cmake_template = 'piglit_include_target_api()\n'

# tests/spec/$ext/CMakeLists.gl.txt
ext_cmake_api_template_1 = \
"""include_directories (
\t${GLEXT_INCLUDE_DIR}
\t${OPENGL_INCLUDE_PATH}
)

link_libraries (
\tpiglitutil_${piglit_target_api}
\t${OPENGL_gl_LIBRARY}
\t${OPENGL_glu_LIBRARY}
)

"""

# tests/spec/$ext/$test.c
ext_c_test_template = \
"""/*
 * Copyright © 2014 Intel Corporation
 *
 * Permission is hereby granted, free of charge, to any person obtaining a
 * copy of this software and associated documentation files (the "Software"),
 * to deal in the Software without restriction, including without limitation
 * the rights to use, copy, modify, merge, publish, distribute, sublicense,
 * and/or sell copies of the Software, and to permit persons to whom the
 * Software is furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice (including the next
 * paragraph) shall be included in all copies or substantial portions of the
 * Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 * DEALINGS IN THE SOFTWARE.
 */
#include "piglit-util-gl.h"

PIGLIT_GL_TEST_CONFIG_BEGIN

    config.supports_gl_compat_version = 30;
    config.window_visual = PIGLIT_GL_VISUAL_RGB | PIGLIT_GL_VISUAL_DOUBLE;

PIGLIT_GL_TEST_CONFIG_END

enum piglit_result
piglit_display(void)
{
    return PIGLIT_FAIL;
}

void
piglit_init(int argc, char **argv)
{
    piglit_require_gl_extension("GL_%s");
}
"""


def do_c_test(ext, test):
    create_file(ext_dir(ext) + '/CMakeLists.txt', ext_cmake_template)
    create_file(ext_dir(ext) + '/CMakeLists.gl.txt', ext_cmake_api_template_1)
    ensure_line_in_file(ext_dir(ext) + '/CMakeLists.gl.txt',
            'piglit_add_executable (%s-%s %s.c)\n' % (
                ext.lower(), test.lower(), test.lower()))
    ensure_line_in_file(basepath + '/CMakeLists.txt',
            'add_subdirectory (%s)\n' % ext.lower())

    ensure_line_in_file('tests/all.py',
            '\n%s = {}\n' % ext.lower())
    ensure_line_in_section('tests/all.py',
            '%s = {}\n' % ext.lower(),
            '',
            "add_concurrent_test(%s, '%s-%s')\n" % (
            ext.lower(), ext.lower(), test.lower()))
    create_file(ext_dir(ext) + '/%s.c' % test.lower(),
            ext_c_test_template % (ext,))

def main(argv):
    opt, ext, test = argv[1:]

    if opt == '-c':
        do_ext_dirs(ext)
        do_c_test(ext, test)

if __name__ == '__main__':
    main(sys.argv)
