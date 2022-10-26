#!/bin/bash -x

srcData=$(readlink -ve $1) || exit 1
tgtData=$(readlink -ve $2) || exit 1
unlabeledData=$(readlink -ve $3) || exit 1
email=$4

#http --form POST http://localhost:8088/annotator/train_single_source_ocr/ trainData@${trainData} email=${email} unlabeledData@${unlabeledData}
http --form POST http://localhost:8088/annotator/train_single_source_ocr/ \
    srcData@${srcData} \
    tgtData@${tgtData} \
    email=${email} \
    unlabeledData@${unlabeledData}
