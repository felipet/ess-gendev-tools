==============================
ESS Generic Device Tools Pylib
==============================

.. include-readme-from-here

.. image:: https://gitlab.esss.lu.se/icshwi/mtca-management/ess-gendev-tools/badges/master/pipeline.svg
.. image:: https://sonarqube.esss.lu.se/api/project_badges/measure?project=gendev-tools&metric=alert_status
.. image:: https://sonarqube.esss.lu.se/api/project_badges/measure?project=gendev-tools&metric=ncloc
.. image:: https://sonarqube.esss.lu.se/api/project_badges/measure?project=gendev-tools&metric=coverage
.. image:: https://readthedocs.org/projects/ess-generic-devices-tools-pylib/badge/?version=latest

This Python library is scoped within the µTCA management tools project. The
purpose of this library is providing a set of modules for controlling some
of the most common devices that our group installs in the µTCA systems.

Using this library, most of the annoying details about handling µTCA based
systems are hidden. The main aim of this library is delivering an easy and
reliable interface to some of the devices that are commonly found in a µTCA
system.

Supported devices
=================

Currently, the following devices are supported by the library:

- **NAT MCH**

If you'd like to add support for another device, contact any of the maintainers
or feel free to contribute! But, please, take a look at the
:doc:`../contributing` guidelines first.

How to use the library
======================

The library will be available on some Python distribution tool eventually.
Until that happens, the code has to be pulled from source and manually
installed. The only system requirements are Python >= 3.7 and Pip. You might
use *virtualenv* to keep the installation isolated from the system (install
it using pip), if not, feel free to omit it from the following steps:

.. code-block:: bash

    $ git clone https://gitlab.esss.lu.se/icshwi/mtca-management/ess-gendev-tools.git
    $ cd ess-gendev-tools
    $ virtualenv env
    $ source env/bin/activate
    # From now, all the dependencies will be installed within the env directory
    # When not using virtualenv, the dependencies will be available outside
    # this project.
    $ python -m pip install --upgrade pip
    $ pip install build
    $ python -m build
    $ pip install -e .

You're ready to go!

How to run the tests
--------------------

The testing of the code relies on Pytest and it's automatized using
`Tox <https://tox.readthedocs.io/en/latest>`_ . By now, the code is tested
against two Python versions: **3.7** and **3.8**. There's no special requirement
about the version (yet) as long as Python 3 is used. By default, running
Tox without arguments will run the tests against all the included environments.
Since it's not common having multiple Python versions, run Tox this way
(considering that Python 3.8 is installed):

..  code-block:: bash

    $ cd ess-gendev-tools
    # Tox manages virtualenv behind the scenes, so no need to worry about
    # anything, just call it:
    $ tox -e py38

Some tests rely on a physical device (an NAT MCH). We only have one for the
tests, which means it might be used by others, so first check the MCH is not
used at the moment of running the tests.

Simple example of use
---------------------

Provided that the library is installed and available for the code that you're
writing, it is quite straightforward using the modules within the library.
Modules targeting specific communication interfaces should be avoided, unless
you know what you're doing. The best idea would be to use the main class
NATMCH from the module :py:mod:`gendev_tools.nat_mch.nat_mch`.

The following code snippet shows how to easily retrieve the information about
an MCH, check if the firmware is updated and perform an update when it's needed:

.. code-block:: python

    from gendev_tools.nat_mch.nat_mch import NATMCH
    from gendev_tools.gendev_interface import ConnType

    mymch = NATMCH('172.30.5.238', allowed_conn=[ConnType.TELNET, ConnType.ETHER])
    mchconfig = mymch.device_info()

    target_fw = 'V2.21.8'
    if target_fw != mchconfig['board']['fw_ver']:
        print("Updating the MCH fw....")
        # Get rid of the initial "V"
        mymch.update_fw(target_fw[1:])

In order to update an NAT MCH, the device should be accessible in the network
and Telnet shall be enabled (by default it is). The firmware is provided by
a TFTP server, so it's important to check that the server is available as well.
More details about using the modules, and why the
:py:class:`gendev_tools.gendev_interface.ConnType` could be found in the modules
section of this documentation.

Maintainers
===========

- Felipe Torres González (felipe.torresgonzalez@ess.eu)
