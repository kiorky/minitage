
Test of minitage Mercurial fetcher
====================================


::

    >>> globals().update(layer['globs'])

This fetcher can fetch something over mercurial.

Initial imports::

    >>> lang, lcall = os.environ.get('LANG', ''), os.environ.get('LC_ALL', '')
    >>> os.environ['LANG'], os.environ['LC_ALL'] = 'C', 'C'
    >>> from minitage.core.fetchers import interfaces
    >>> from minitage.core.common import md5sum
    >>> from minitage.core.fetchers import scm as scmm
    >>> n = scmm.__logger__

Install some magic to get the fetcher logs::

    >>> from zope.testing.loggingsupport import InstalledHandler
    >>> log_handler = InstalledHandler(n)

Instantiate our fetcher::

    >>> hg = scmm.HgFetcher()

Make a file available for download::

    >>> dest = os.path.join(p, 'hg/d')
    >>> path = os.path.join(p, 'hg/p0')
    >>> path1 = os.path.join(p, 'hg/p1')
    >>> path2 = os.path.join(p, 'hg/p2')
    >>> path3 = os.path.join(p, 'hg/p3')
    >>> path4 = os.path.join(p, 'hg/p4')
    >>> wc = os.path.join(p, 'hg/wc')
    >>> hguri = 'file://%s' % path2
    >>> hguri2= 'file://%s' % path3
    >>> opts = {'path': path, 'dest': dest, 'wc': wc}
    >>> opts.update({'path2': path2})
    >>> noecho = os.system("""
    ...          mkdir -p  %(path2)s        2>&1 >> /dev/null
    ...          cd %(path2)s               2>&1 >> /dev/null
    ...          echo '666'>file            2>&1 >> /dev/null
    ...          hg init                    2>&1 >> /dev/null
    ...          hg add                     2>&1 >> /dev/null
    ...          hg ci -m 'initial import'  2>&1 >> /dev/null
    ...          echo '666'>file2           2>&1 >> /dev/null
    ...          hg add                     2>&1 >> /dev/null
    ...          hg ci -m 'second revision' 2>&1 >> /dev/null
    ...          """ % opts)
    >>> noecho = copy_tree(path2, path3)

Checking our working copy is up and running
Fine.
Beginning simple, checkouting the code somewhere::

    >>> hg.fetch(wc, hguri)
    >>> ls(wc)
    .hg
    file
    file2
    >>> print log_handler; log_handler.clear()
    minitage.fetchers.scm INFO
      Checkouted .../wc / file://.../p2 (tip) [Mercurial].
    >>> sh('cd %s&&hg id'%wc)
    cd .../wc&&hg id
    ... tip...

Calling fetch on an already fetched clone::

    >>> touch(os.path.join(wc, 'foo'))
    >>> hg.fetch(wc, hguri)
    >>> print log_handler; log_handler.clear()
    minitage.fetchers.scm WARNING
      Destination .../wc already exists and is not empty, moving it away in ...wc/wc.old... for further user examination
    minitage.fetchers.scm WARNING
      Checkout directory is not the same as the destination, copying content to it. This may happen when you say to download to somwhere where it exists files before doing the checkout
    minitage.fetchers.scm INFO
      Checkouted .../wc / file://.../p2 (tip) [Mercurial].
    >>> oldp =  [os.path.join(wc, f) for f in os.listdir(wc) if f != '.hg' and os.path.isdir(os.path.join(wc, f))][0]
    >>> oldp, ls(oldp)
    .hg
    file
    file2
    foo
    ('...wc/wc.old...', None)

Calling fetch from another repository::

    >>> hg.fetch(wc, hguri2)
    >>> print log_handler; log_handler.clear()
    minitage.fetchers.scm WARNING
      Destination .../wc already exists and is not empty, moving it away in ...wc/wc.old... for further user examination
    minitage.fetchers.scm WARNING
      Checkout directory is not the same as the destination, copying content to it. This may happen when you say to download to somwhere where it exists files before doing the checkout
    minitage.fetchers.scm INFO
      Checkouted .../wc / file://.../p3 (tip) [Mercurial].

Going into past, revision 1::

    >>> hg.get_uri(wc)
    '.../p3'
    >>> hg._has_uri_changed(wc, hguri2)
    False
    >>> hg._has_uri_changed(wc, hguri)
    True
    >>> log_handler.clear()
    >>> commits = [a.strip() for a  in subprocess.Popen(['cd %s;hg log|grep changeset|awk -F : \'{print $3}\''%wc], shell=True, stdout=subprocess.PIPE).stdout.read().splitlines()]
    >>> hg.update(wc, hguri2, {"revision": 0, 'foo': 'foo'})
    >>> print log_handler; log_handler.clear()
    minitage.fetchers.scm DEBUG
      Updating .../wc / file://.../p3
    minitage.fetchers.scm DEBUG
      Running hg showconfig |grep paths.default in .../wc
    minitage.fetchers.scm DEBUG
      Running hg showconfig |grep paths.default in .../wc
    minitage.fetchers.scm INFO
      Updated .../wc / file://.../p3 (0) [Mercurial].
    >>> commits[1] == subprocess.Popen(['cd %s;hg id'%wc], shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    True

Going head, update without arguments sticks to HEAD::

    >>> hg.update(wc, hguri2)
    >>> print log_handler; log_handler.clear() # daoctest: +REPORT_NDIFF
    minitage.fetchers.scm DEBUG
      Updating .../wc / file://...p3
    minitage.fetchers.scm DEBUG
      Running hg showconfig |grep paths.default in .../wc
    minitage.fetchers.scm DEBUG
      Running hg showconfig |grep paths.default in .../wc
    minitage.fetchers.scm INFO
      Updated .../wc / file://.../p3 (tip) [Mercurial].
    >>> 'tip' in  subprocess.Popen(['cd %s;hg id'%wc], shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    True

Cleaning

    >>> shutil.rmtree(wc)

Test the fech or update method which clones or update a working copy::

    >>> hg.fetch_or_update(wc, hguri, {"revision": commits[1]})
    >>> commits[1] == subprocess.Popen(['cd %s;hg id'%wc], shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    True
    >>> hg.fetch_or_update(wc, hguri)
    >>> 'tip' in  subprocess.Popen(['cd %s;hg id'%wc], shell=True, stdout=subprocess.PIPE).stdout.read().strip()
    True
    >>> log_handler.clear()


Problem in older version, trailing slash cause API to have troubles::

    >>> shutil.rmtree(wc)
    >>> hg.fetch_or_update(wc, '%s/' % hguri)
    >>> log_handler.clear()
    >>> hg.fetch_or_update(wc, '%s/' % hguri)
    >>> print log_handler; log_handler.clear()
    minitage.fetchers.scm DEBUG
      Updating .../wc / file://.../p2/
    minitage.fetchers.scm DEBUG
      Running hg showconfig |grep paths.default in .../wc
    minitage.fetchers.scm WARNING
      It seems that the url given do not need the trailing slash (.../p2/). You would have better not to keep trailing slash in your urls if you don't have to.
    minitage.fetchers.scm INFO
      Updated .../wc / file://.../p2/ (tip) [Mercurial].

Other problem; update on an empty directory may fail on older version of this code::

    >>> shutil.rmtree(wc); mkdir(wc)
    >>> hg.update(wc, hguri)
    >>> print log_handler; log_handler.clear()
    minitage.fetchers.scm DEBUG
      Updating .../wc / file://.../p2
    minitage.fetchers.scm WARNING
      The working copy seems not to be a Mercurial repository. Getting a new working copy.
    minitage.fetchers.scm INFO
      Checkouted .../wc / file://.../p2 (tip) [Mercurial].
    minitage.fetchers.scm DEBUG
      Running hg showconfig |grep paths.default in .../wc
    minitage.fetchers.scm DEBUG
      Running hg showconfig |grep paths.default in .../wc
    minitage.fetchers.scm INFO
      Updated .../wc / file://.../p2 (tip) [Mercurial].

.. vim: set ft=doctest :

