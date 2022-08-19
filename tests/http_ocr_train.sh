#!/bin/bash -x

trainData=$(readlink -ve $1) || exit 1
unlabeledData=$(readlink -ve $2) || exit 1

http --form POST http://localhost:8088/annotator/train_single_source_ocr/ trainData@${trainData} unlabeledData@${unlabeledData}
