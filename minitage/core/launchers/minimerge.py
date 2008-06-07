#!/usr/bin/env python
__docformat__ = 'restructuredtext en'

import sys
import os
import re
import shutil

from pkg_resources import Requirement, resource_filename
from minitage.core.cli import do_read_options
from minitage.core import core 

def launch():
    try:
        ## first time create default config !
        prefix = os.path.abspath(sys.exec_prefix)
        config = os.path.join(prefix, 'etc', 'minimerge.cfg')
        if not os.path.isfile(config):
            print """\n\n\n
    ====================================================
    \t\tWELCOME TO THE MINITAGE WORLD
    ====================================================

    You seem to be running minitage for the first time.

    \t* Creating some default stuff...
    \t* Generating default config: %s """ % config
            print '\t* Creating minilays dir'
            for dir in (os.path.split(config)[0],
                        os.path.join(sys.exec_prefix, 'minilays'),
                        os.path.join(sys.exec_prefix, 'logs'),
                        os.path.join(sys.exec_prefix, 'eggs', 'cache'),
                        os.path.join(sys.exec_prefix, 'eggs', 'develop-cache'),
                        os.path.join(sys.exec_prefix, 'share', 'minitage'),
                       ):
                if not os.path.isdir(dir):
                    os.makedirs(dir)
            tconfig = resource_filename(Requirement.parse(
                'minitage.core == %s' % core.__version__),
                'etc/minimerge.cfg')
            changelog= resource_filename(Requirement.parse(
                'minitage.core == %s' % core.__version__),
                'share/minitage/CHANGES.txt')
            readme= resource_filename(Requirement.parse(
                'minitage.core == %s' % core.__version__),
                'share/minitage/README.txt')
            prefixed = re.sub('%PREFIX%',prefix,open(tconfig,'r').read())
            open(config, 'w').write(prefixed)
            print '\t* Installing CHANGELOG.'
            shutil.copy(changelog,
                        os.path.join(
                            sys.exec_prefix,
                            'share', 'minitage',
                            'CHANGES.txt'
                        )
                       )
            print '\t* Installing README.'
            shutil.copy(readme,
                        os.path.join(
                            sys.exec_prefix,
                            'share', 'minitage',
                            'README.TXT'
                        )
                       )
            print '\n\n'
        options = do_read_options()
        minimerge = core.Minimerge(options)
        minimerge.main()
    except Exception, e:
        sys.stderr.write('Minimerge executation failed:\n')
        sys.stderr.write('\t%s\n' % e)

# vim:set ft=python sts=4 ts=4 tw=80 et: