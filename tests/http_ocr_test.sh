#!/bin/bash -x

testData=$(readlink -ve $1) || exit 1
model_id=$2

http --form POST http://localhost:8088/annotator/test_single_source_ocr/ model_id=${model_id} testData@${testData}
