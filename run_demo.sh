#!/bin/bash
curl -X 'GET' 'http://localhost:8005/run_workflow?username=admin&password=secret&title=Data%20Scientist&skills=Python,Machine%20Learning' \
  -H 'accept: application/json'