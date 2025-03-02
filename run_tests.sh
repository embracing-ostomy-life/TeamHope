#!/usr/bin/env bash

result=0
coverage erase
coverage run manage.py test --noinput tests
if [[ $? -ne 0 ]]; then
  result=1
fi
coverage report -m

exit $result