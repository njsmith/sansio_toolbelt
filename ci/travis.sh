#!/bin/bash

set -eux -o pipefail

# ${foo:-} means "$foo, unless that's undefined, in which case an empty string"
if [ -n "${PYPY_VERSION:-}" ]; then
    curl -Lo pypy.tar.bz2 https://bitbucket.org/squeaky/portable-pypy/downloads/${PYPY_VERSION}-linux_x86_64-portable.tar.bz2
    tar xaf pypy.tar.bz2
    # something like "pypy-5.6-linux_x86_64-portable"
    PYPY_DIR=$(echo pypy-*)
    PYTHON_EXE=$(echo $PYPY_DIR/bin/pypy*)
    $PYTHON_EXE -m ensurepip
    $PYTHON_EXE -m pip install virtualenv
    $PYTHON_EXE -m virtualenv testenv
    # http://redsymbol.net/articles/unofficial-bash-strict-mode/#sourcing-nonconforming-document
    set +u
    source testenv/bin/activate
    set -u
fi

pip install -U pip setuptools wheel

python setup.py sdist --formats=zip
pip install dist/*.zip

if [ "$DOC_BUILD" = "1" ]; then
    pip install -U sphinx sphinx_rtd_theme sphinxcontrib-trio
    cd docs
    # -n (nit-picky): warn on missing references
    # -W: turn warnings into errors
    sphinx-build -nW  -b html source build
else
    # Actual tests
    pip install -Ur test-requirements.txt

    mkdir empty
    cd empty

    INSTALLDIR=$(python -c "import os, sansio_toolbelt; print(os.path.dirname(sansio_toolbelt.__file__))")
    pytest -W error -ra ${INSTALLDIR} --cov="$INSTALLDIR" --cov-config=../.coveragerc

    pip install codecov && codecov
fi
