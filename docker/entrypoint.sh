#!/bin/sh
export PYTHONPATH="${PYTHONPATH}:/home/app/Pignus-py3.8.egg"
if [ -z "${AWS_LAMBDA_RUNTIME_API}" ]; then
    python3 /home/app/app.py cluster-check-in
else
    exec /usr/local/bin/python -m awslambdaric $1
fi
