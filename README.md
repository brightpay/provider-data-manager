# README #

This README would normally document whatever steps are necessary to get your application up and running.

### Virtual Env ###

python3.12 -m venv provider-data-manager
source provider-data-manager/venv/bin/activate
pip install pytest

### Deploying to Lambda Function ###

rm -rf provdatamgr.zip
zip -r "provdatamgr.zip" * 1> /dev/null
aws lambda update-function-code --function-name provider-data-manager --region ap-south-1 --zip-file "fileb://provdatamgr.zip"