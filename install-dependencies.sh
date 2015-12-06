#!/usr/bin/env bash
pip install -r requirements/zeromq.txt -r requirements/tests.txt --use-mirrors

mkdir ~/.aws/
cat > ~/.aws/credentials << EOL
[beaver_queue]
aws_access_key_id = 111
aws_secret_access_key = 1111
EOL
