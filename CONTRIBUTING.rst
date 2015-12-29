Contributing Code
=================

-  A good patch:
   -  is clear.
   -  works across all supported versions of Python.
   -  has comments included as needed.

-  A test case that demonstrates the previous flaw that now passes with
   the included patch.
-  If it adds/changes a public API, it must also include documentation
   for those changes.
-  Must be appropriately licensed.

Reporting An Issue/Feature
==========================

-  Check to see if there’s an existing issue/pull request for the
   bug/feature. All issues are at
   https://github.com/josegonzalez/python-beaver/issues and pull reqs
   are at https://github.com/josegonzalez/python-beaver/pulls.
-  If there isn’t an existing issue there, please file an issue. The
   ideal report includes:

-  A description of the problem/suggestion.
-  How to recreate the bug.
-  If relevant, including the versions of your:

   -  Python interpreter
   -  beaver
   -  Optionally of the other dependencies involved

-  If possible, create a pull request with a (failing) test case
   demonstrating what’s wrong. This makes the process for fixing bugs
   quicker & gets issues resolved sooner.

Maintenance
===========

You do not have to be labeled as a “mainatainer” to be able to help with
the triaging, resolving, and reviewing of beaver issues and pull
requests.

These are the processes that the maintainers follow, that you can also
follow to help speed up the resolution of an issue or pull request:

Pull Requests
-------------

There are some key points that are needed to be met before a pull
request can be merged:

-  All tests must pass for all python versions.
-  All pull requests require tests that either test the new feature or
   test that the specific bug is fixed. Pull requests for minor things
   like adding a new region or fixing a typo do not need tests.
-  All changes must be backwards compatible.
-  Minor commits within a larger PR should be squashed to reduce noise
   in the changelog.
-  Changes to public facing functionality should include relevant updates to the documentation

The best way to help with pull requests is to comment on pull requests
by noting if any of these key points are missing, it will both help get
feedback sooner to the issuer of the pull request and make it easier to
determine for an individual with write permissions to the repository if
a pull request is ready to be merged.

Issues
------

Here are the best ways to help with open issues:

-  If there is an issue without a set of instructions on how to
   reproduce the bug, feel free to try to reproduce the issue, comment
   with the minimal amount of steps to reproduce the bug (a code snippet
   would be ideal). If there is not a set of steps that can be made to
   reproduce the issue, at least make sure there are debug logs that
   capture the unexpected behavior.

-  Consolidate all related issue to one issues by closing out related
   issues and linking them to the single issue that outlines the general
   issue.

-  Submit pull requests for open issues.

Test Suite
------

The test suite is fairly straight-forward to run:

- ./install-dependencies.sh
- nosetests
