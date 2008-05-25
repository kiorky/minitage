# Copyright (C) 2008, 'Mathieu PASQUET <kiorky@cryptelium.net>'
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

__docformat__ = 'restructuredtext en'

import unittest
import os
import sys
import shutil
import optparse
import ConfigParser
import tempfile

from minitage.core import api, cli, objects, core
from minitage.core.tests import test_common

__cwd__ = os.getcwd()


path = '%s/test' % os.path.expanduser(tempfile.mkdtemp())
testopts = dict(path=path)
minilay = '%(path)s/minilays/myminilay1' % testopts
class testMinimerge(unittest.TestCase):
    """testMinimerge"""

    def setUp(self):
        """."""
        os.chdir(__cwd__)
        test_common.createMinitageEnv(path)
        os.makedirs(minilay)




        minibuilds = [
"""
[minibuild]
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-0
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-4 minibuild-1
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-2
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-0
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-7
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-5
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-6
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-8
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-0 minibuild-3
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-11
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-12
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-13
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
"""
[minibuild]
dependencies=minibuild-10
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""" ]


        pythonmbs = [
#1000
"""
[minibuild]
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=dependencies
""", #1001
"""
[minibuild]
dependencies=meta-python minibuild-1005
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=dependencies
""", #1002
"""
[minibuild]
dependencies=python-2.4 minibuild-1005
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=dependencies
""", #1003
"""
[minibuild]
dependencies=python-2.5 minibuild-1005
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=dependencies
""", #1004
"""
[minibuild]
dependencies=minibuild-1005
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=dependencies
""", #1005
"""
[minibuild]
dependencies=meta-python
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=eggs
""",
]


        for index, minibuild in enumerate(minibuilds):
            open('%s/minibuild-%s' % (minilay, index), 'w').write(minibuild)

        os.system("""cd %s ;
                  hg init;
                  hg add ;
                  hg ci -m 1;""" % minilay)
        for index, minibuild in enumerate(pythonmbs):
            open('%s/minibuild-100%s' % (minilay, index), 'w').write(minibuild)

        # fake 3 pythons.
        for minibuild in ['python-2.4', 'python-2.5']:
            open('%s/%s' % (minilay, minibuild), 'w').write("""
[minibuild]
src_uri=https://hg.minitage.org/minitage
src_type=hg
install_method=buildout
category=dependencies""")

        open('%s/%s' % (minilay, 'meta-python'), 'w').write("""
[minibuild]
dependencies=python-2.4 python-2.5
src_uri=https://hg.minitage.org/minitage
src_type=hg
category=meta
install_method=buildout""")

        os.system("""
                  cd %s ;
                  echo "[paths]">.hg/hgrc
                  echo "default = %s">>.hg/hgrc
                  hg add;
                  hg ci -m 2;""" % (minilay, minilay))

    def tearDown(self):
        """."""
        os.chdir(__cwd__)
        shutil.rmtree(os.path.expanduser(path))

    def testFindMinibuild(self):
        """testFindMinibuild
        find m0?"""
        # create minilays in the minilays dir, seeing if they get putted in
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        mb = minimerge._find_minibuild('minibuild-0')
        self.assertEquals('minibuild-0', mb.name)

    def testComputeDepsWithNoDeps(self):
        """testComputeDepsWithNoDeps
        m0 depends on nothing"""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        computed_packages = minimerge._compute_dependencies(['minibuild-0'])
        mb = computed_packages[0]
        self.assertEquals('minibuild-0', mb.name)

    def testSimpleDeps(self):
        """testSimpleDeps
        test m1 -> m0"""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        computed_packages = minimerge._compute_dependencies(['minibuild-1'])
        mb = computed_packages[0]
        self.assertEquals(mb.name, 'minibuild-0')
        mb = computed_packages[1]
        self.assertEquals(mb.name, 'minibuild-1')

    def testChainedandTreeDeps(self):
        """testChainedandTreeDeps
        Will test that this tree is safe:
              -       m3
                      /
                     m2
                     / \
                    m4 m1
                     \/
                     m0

               -   m9
                  / \
                 m0 m3
        """
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        computed_packages = minimerge._compute_dependencies(['minibuild-3'])
        wanted_list = ['minibuild-0', 'minibuild-4',
                       'minibuild-1', 'minibuild-2', 'minibuild-3']
        self.assertEquals([mb.name for mb in computed_packages], wanted_list)
        computed_packages = minimerge._compute_dependencies(['minibuild-9'])
        wanted_list = ['minibuild-0', 'minibuild-4', 'minibuild-1',
                       'minibuild-2', 'minibuild-3', 'minibuild-9']
        self.assertEquals([mb.name for mb in computed_packages], wanted_list)

    def testRecursivity(self):
        """testRecursivity
        check that:
             - m5  -> m6 -> m7
             - m8  -> m8
             - m10 -> m11 -> m12 -> m13 -> m10
        will throw some recursity problems.
        """
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()

        minimerge = api.Minimerge(opts)
        self.assertRaises(core.CircurlarDependencyError,
                          minimerge._compute_dependencies, ['minibuild-6'])

        minimerge = api.Minimerge(opts)
        self.assertRaises(core.CircurlarDependencyError,
                          minimerge._compute_dependencies, ['minibuild-8'])

        minimerge = api.Minimerge(opts)
        self.assertRaises(core.CircurlarDependencyError,
                          minimerge._compute_dependencies, ['minibuild-13'])

    def testMinibuildNotFound(self):
        """testMinibuildNotFound
        INOTINANYMINILAY does not exist"""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'foo']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        self.assertRaises(core.MinibuildNotFoundError,
                          minimerge._find_minibuild, 'INOTINANYMINILAY')

    def testCutDeps(self):
        """testCutDeps"""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path,
                    '--jump', 'minibuild-2',
                    'minibuild-1', 'minibuild-2', 'minibuild-3']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        p =  minimerge._cut_jumped_packages(
            ['minibuild-1', 'minibuild-2', 'minibuild-3']
        )
        self.assertEquals(p, ['minibuild-2', 'minibuild-3'])


    def testFetchOffline(self):
        """testFetchOffline"""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, '--offline', 'minibuild-0']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        self.assertTrue(minimerge._offline)

    def testFetchOnline(self):
        """testFetchOnline"""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'minibuild-0']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        self.assertFalse(minimerge._offline)
        minimerge._fetch(minimerge._find_minibuild('minibuild-0'))
        self.assertTrue(os.path.isdir('%s/eggs/minibuild-0/.hg' % path))


    def testSelectPython(self):
        """testSelectPython.
        Goal of this test is to prevent uneccesary python versions
        to be built.
        """
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'minibuild-0']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        self.assertTrue(minimerge._action, 'install')

        # we install a dependency which is not a egg
        # result is false, no eggs dict in return.
        computed_packages0, p0 = minimerge._select_pythons(
            minimerge._compute_dependencies(['minibuild-1000']))
        self.assertFalse(p0)

        # we install a dep that require python
        # the dict must contains eggs 2.5/2.4
        # available python = 2.4/2.5
        computed_packages1, p1 = minimerge._select_pythons(
            minimerge._compute_dependencies(['minibuild-1001']))
        for i in ['2.4', '2.5']:
            self.assertTrue(i in p1['minibuild-1005'])
            self.assertTrue('python-%s'%i
                            in [c.name for c in computed_packages1]
                           )

        # we install a dep that require python-2.4
        # the dict must contains eggs ==  2.4
        # available python = 2.4
        deps = minimerge._compute_dependencies(['minibuild-1002'])
        computed_packages2, p2 = minimerge._select_pythons(deps)
        self.assertTrue('python-2.4'
                        in [c.name for c in computed_packages2]
                       )
        self.assertTrue('python-2.5'
                        not in [c.name for c in computed_packages2]
                       )
        self.assertTrue('2.4' in p2['minibuild-1005'])
        self.assertTrue('2.5' not in p2['minibuild-1005'])

        # we install a dep that require python-2.5
        # the dict must contains eggs ==  2.5
        # available python = 2.5
        deps = minimerge._compute_dependencies(['minibuild-1003'])
        computed_packages3, p3 = minimerge._select_pythons(deps)
        self.assertTrue('python-2.5'
                        in [c.name for c in computed_packages3]
                       )
        self.assertTrue('python-2.4'
                        not in [c.name for c in computed_packages3]
                       )
        self.assertTrue('2.5' in p3['minibuild-1005'])
        self.assertTrue('2.4' not in p3['minibuild-1005'])

        # we install a dep that require only a egg, no pytthon
        # is specified specificly
        # the dict must contains eggs ==  2.5/2.4
        # available python = 2.5/2.4
        computed_packages4, p4 = minimerge._select_pythons(
            minimerge._compute_dependencies(['minibuild-1004']))
        for i in ['2.4', '2.5']:
            self.assertTrue(i in p4['minibuild-1005'])
            self.assertTrue('python-%s'%i
                            in [c.name for c in computed_packages4]
                           )

        # we install an egg directly
        # the dict must contains eggs ==  2.5/2.4
        # available python = 2.5/2.4
        minimerge._packages = ['minibuild-1005']
        computed_packagest, pt = minimerge._select_pythons(
            minimerge._compute_dependencies(['minibuild-1005']))
        for i in ['2.4', '2.5']:
            self.assertTrue(i in pt['minibuild-1005'])
            self.assertTrue('python-%s'%i
                            in [c.name for c in computed_packagest]
                           )

    def testActionDelete(self):
        """testActionDelete."""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'minibuild-0']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)

        ipath = '%s/dependencies/python-%s' % (path, '2.4')
        test_common.make_dummy_buildoutdir(ipath)

        py24 = minimerge._find_minibuild('python-2.4')
        self.assertTrue(os.path.isdir(ipath))
        minimerge._do_action('delete', [py24])
        self.assertTrue(not os.path.isdir(ipath))

    def testActionInstall(self):
        """testActionInstall."""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'minibuild-0']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)

        for i in ['2.4', '2.5']:
            test_common.make_dummy_buildoutdir(
                '%s/dependencies/python-%s' % (path, i)
            )

        test_common.make_dummy_buildoutdir(
            '%s/eggs/%s' % (path, 'minibuild-1005')
        )

        my_d = {'python-2.4': '2.4'}
        py24 = minimerge._find_minibuild('python-2.4')
        respy24 = '%s/dependencies/python-2.4/testres' % path
        minimerge._do_action('install', [py24], my_d)
        py25 = minimerge._find_minibuild('python-2.5')
        respy25 = '%s/dependencies/python-2.5/testres' % path

        minimerge._do_action('install', [py24], my_d)
        self.assertEquals(open(respy24,'r').read(), 'bar')
        minimerge._do_action('install', [py25], my_d)
        self.assertEquals(open(respy25,'r').read(), 'bar')

        m1005 = minimerge._find_minibuild('minibuild-1005')
        m1005res =   '%s/eggs/minibuild-1005/testres' % path
        m1005res24 = '%s/eggs/minibuild-1005/testres2.4' % path
        m1005res25 = '%s/eggs/minibuild-1005/testres2.5' % path
        minimerge._do_action('install', [m1005], {'minibuild-1005' :
                                                  ['2.4', '2.5']})
        self.assertEquals(open(m1005res24,'r').read(), '2.4')
        self.assertEquals(open(m1005res25,'r').read(), '2.5')
        self.assertFalse(os.path.isfile(m1005res))

    def testInvalidAction(self):
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'minibuild-0']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        test_common.make_dummy_buildoutdir(
            '%s/dependencies/python-2.4' % path
        )
        py = minimerge._find_minibuild('python-2.4')
        self.assertRaises(core.ActionError,
                          minimerge._do_action,
                          'invalid',
                          [py]
                         )

    def testSync(self):
        """testSync."""
        sys.argv = [sys.argv[0], '--config',
                    '%s/etc/minimerge.cfg' % path, 'minibuild-0']
        opts = cli.do_read_options()
        minimerge = api.Minimerge(opts)
        os.system("cd %s;hg up -r 0" % minilay)
        self.assertFalse(os.path.isfile('%s/%s' % (minilay, 'minibuild-1000')))
        minimerge._sync()
        self.assertTrue(
            os.path.isdir(
                '%s/minilays/%s' %
                (path, 'dependencies')
            )
        )
        self.assertTrue(os.path.isfile('%s/%s' % (minilay, 'minibuild-1000')))

if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testMinimerge))
    unittest.TextTestRunner(verbosity=2).run(suite)


