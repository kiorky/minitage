# Copyright (C) 2009, Mathieu PASQUET <kiorky@cryptelium.net>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the <ORGANIZATION> nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.



__docformat__ = 'restructuredtext en'

import os
import sys
import logging

import urllib2

from minitage.core.makers  import interfaces
import minitage.core.core
import minitage.core.common

from iniparse import ConfigParser

class BuildoutError(interfaces.IMakerError):
    """General Buildout Error."""

__logger__ = 'minitage.makers.buildout'

class BuildoutMaker(interfaces.IMaker):
    """Buildout Maker.
    """
    def __init__(self, config = None, verbose=False):
        """Init a buildout maker object.
        Arguments
            - config keys:

                - options: cli args for buildout
        """
        if not config:
            config = {}
        self.logger = logging.getLogger(__logger__)
        self.config = config
        self.buildout_config = 'buildout.cfg'
        interfaces.IMaker.__init__(self)

    def match(self, switch):
        """See interface."""
        if switch == 'buildout':
            return True
        return False

    def reinstall(self, directory, opts=None):
        """Rebuild a package.
        Warning this will erase .installed.cfg forcing buildout to rebuild.
        Problem is that underlying recipes must know how to handle the part
        directory to be already there.
        This will be fine for minitage recipes in there. But maybe that will
        need boiler plate for other recipes.
        Exceptions
            - ReinstallError
        Arguments
            - directory : directory where the packge is
            - opts : arguments for the maker
        """
        mypath = os.path.join(
            directory,
            '.installed.cfg'
        )
        if os.path.exists(mypath):
            os.remove(mypath)
        self.install(directory, opts)

    def install(self, directory, opts=None):
        """Make a package.
        Exceptions
            - MakeError
        Arguments
            - dir : directory where the packge is
            - opts : arguments for the maker
        """
        if opts is None:
            opts = {}
        self.logger.info(
            'Running buildout in %s (%s)' % (directory,
                                             self.buildout_config))
        cwd = os.getcwd()
        os.chdir(directory)
        dcfg = os.path.expanduser('~/.buildout/default.cfg')
        downloads_caches = [
            os.path.abspath('../../downloads/dist'),
            os.path.abspath('../../downloads/minitage/eggs'),
            os.path.abspath('../../download/dist'),
            os.path.abspath('../../download/minitage/eggs'),
        ]
        if os.path.exists(dcfg):
            try:
                cfg = ConfigParser()
                cfg.read(dcfg)
                buildout = dict(cfg.items('buildout'))
                for k in ['download-directory', 'download-cache']:
                    if k in buildout:
                        places = [k,
                                  '%s/dist' % k,
                                  '%s/minitage/eggs'%k]
                        downloads_caches.extend(places)
            except Exception, e:
                pass
        find_links = []
        cache = os.path.abspath('../../eggs/cache')
        for c in [cache] + downloads_caches:
            if os.path.exists(c) and not c in find_links:
                find_links.append(c)
        bcmd = os.path.normpath('./bin/buildout')
        minibuild = opts.get('minibuild', None)
        dependency_or_egg = getattr(minibuild, 'category', None) in ['dependencies', 'eggs']
        if not opts:
            opts = {}
        try:
            argv = []
            if opts.get('verbose', False):
                self.logger.debug('Buildout is running in verbose mode!')
                argv.append('-vvvvvvv')
            installed_cfg = os.path.join(directory, '.installed.cfg')
            if (not opts.get('upgrade', True)
                and not dependency_or_egg
                and not os.path.exists(installed_cfg)):
                argv.append('-N')
            if opts.get('upgrade', False) or dependency_or_egg:
                self.logger.debug('Buildout is running in newest mode!')
                argv.append('-n')
            if opts.get('offline', False):
                self.logger.debug('Buildout is running in offline mode!')
                argv.append('-o')
            if opts.get('debug', False):
                self.logger.debug('Buildout is running in debug mode!')
                argv.append('-D')
            parts = opts.get('parts', False)
            if isinstance(parts, str):
                parts = parts.split()
            category = ''
            if minibuild: category = minibuild.category
            # Try to upgrade only if we need to
            # (we chech only when we have a .installed.cfg file
            if not opts.get('upgrade', True)\
               and os.path.exists(installed_cfg) and (not category=='eggs'):
                self.logger.info('Buildout will not run in %s'
                                  ' as there is a .installed.cfg file'
                                  ' indicating us that the software is already'
                                  ' installed but minimerge is running in'
                                  ' no-update mode. If you want to try'
                                  ' to update/rebuild it unconditionnaly,'
                                  ' please relaunch with -uUR.' % directory)
                return


            # running buildout in our internal way
            # always regenerating that buildout file
            #if not os.path.exists(
            #    os.path.join(
            #        directory,
            #        'bin',
            #        'buildout')):
            bootstrap_args = ''
            py = self.choose_python(directory, opts)
            if os.path.exists('bootstrap.py'):
                # if this bootstrap.py supports distribute, just use it!
                content = open('bootstrap.py').read()
                # special handly plone case
                buildout1 = False
                try:
                    def findcfgs(path, cfgs=None):
                        if not cfgs: cfgs=[]
                        for p, ids, ifs in os.walk(path):
                            for i in ifs:
                                if i.endswith('.cfg'):
                                    cfgs.append(os.path.join(p, i))
                        return cfgs
                    files = findcfgs('.')
                    for f in files:
                        fic = open(f)
                        if 'buildout.dumppick' in fic.read():
                            buildout1 = True
                        fic.close()
                except Exception, e:
                    pass
                if buildout1:
                    booturl = 'http://downloads.buildout.org/1/bootstrap.py'
                else:
                    booturl = 'http://downloads.buildout.org/2/bootstrap.py'
                # try to donwload an uptodate bootstrap
                if not opts['minimerge']._offline:
                    try:
                        try:
                            open(os.path.join(opts['minimerge'].history_dir, 'updated_bootstrap'))
                        except:
                            fic = open('bootstrap.py', 'w')
                            data = urllib2.urlopen(booturl).read()
                            fic.write(data)
                            content = data
                            fic.close()
                            self.logger.info('Bootstrap updated')
                            fic = open(os.path.join(opts['minimerge'].history_dir, 'updated_bootstrap'), 'w')
                            fic.write('foo')
                            fic.close()
                    except:
                        pass
                if '--distribute' in content:
                    self.logger.warning('Using distribute !')
                    bootstrap_args += ' %s ' % '--distribute'
                if opts['minimerge']._offline:
                    bootstrap_args += ' -t '
                if find_links:
                    bootstrap_args += ''.join([' -f %s ' % c for c in find_links])
                bootstrap_args += ' -c %s ' % self.buildout_config
                minitage.core.common.Popen(
                    '%s bootstrap.py %s ' % (py, bootstrap_args,),
                    opts.get('verbose', False)
                )
            else:
                minitage.core.common.Popen(
                    'buildout bootstrap -c %s' % self.buildout_config,
                    opts.get('verbose', False)
                )
            if parts:
                for part in parts:
                    self.logger.info('Installing single part: %s' % part)
                    minitage.core.common.Popen(
                        '%s -c %s %s install %s ' % (
                            bcmd,
                            self.buildout_config,
                            ' '.join(argv),
                            part
                        ),
                        opts.get('verbose', False)
                    )
            else:
                self.logger.debug('Installing parts')
                cmd = '%s -c %s %s ' % (
                    bcmd,
                    self.buildout_config,
                    ' '.join(argv))
                minitage.core.common.Popen(
                    cmd,
                    opts.get('verbose', False)
                )
        except Exception, instance:
            os.chdir(cwd)
            raise BuildoutError('Buildout failed:\n\t%s' % instance)
        os.chdir(cwd)

    def choose_python(self, directory, opts):
        python = sys.executable
        mb =  opts.get('minibuild', None)
        if os.path.exists(mb.python):
            python = mb.python
        return python

    def get_options(self, minimerge, minibuild, **kwargs):
        """Get python options according to the minibuild and minimerge instance.
        For eggs buildouts, we need to know which versions of python we
        will build site-packages for
        For parts, we force to install only the 'part' buildout part.
        Arguments
            - we can force parts with settings 'buildout_parts' in minibuild
            - minimerge a minitage.core.Minimerge instance
            - minibuild a minitage.core.object.Minibuild instance
            - kwargs:

                - 'python_versions' : list of major.minor versions of
                  python to compile against.
        """
        options = {}
        parts = self.buildout_config = [
            a.strip()
            for a in minibuild.minibuild_config._sections[
                'minibuild'].get('buildout_parts', '').split()]
        if kwargs is None:
            kwargs = {}

        # if it s an egg, we must install just the needed
        # site-packages if selected
        if minibuild.category == 'eggs':
            vers = kwargs.get('python_versions', None)
            if not vers:
                vers = minitage.core.core.PYTHON_VERSIONS
            parts = ['site-packages-%s' % ver for ver in vers]
        self.buildout_config = minibuild.minibuild_config._sections[
            'minibuild'].get('buildout_config',
                             'buildout.cfg')
        content = ''
        if minibuild.category == 'eggs':
            try:
                fic = open(os.path.join(minimerge.get_install_path(minibuild), self.buildout_config))
                content = fic.read()
                fic.close()
            except:
                pass
            parts = [p for p in parts+['site-packages'] if '[%s]'%p in content]

        options['parts'] = parts
        # prevent buildout from running if we have already installed stuff
        # and do not want to upgrade.
        options['upgrade'] = minimerge.getUpgrade()
        if minimerge.has_new_revision(minibuild):
            options['upgrade'] = True
        return options

# vim:set et sts=4 ts=4 tw=80:
