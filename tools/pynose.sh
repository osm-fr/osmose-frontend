#!/bin/bash
cd $(dirname $0)
cd ..

nosetests --with-xunit tools/*.py
