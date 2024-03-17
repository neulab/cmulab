#!/bin/bash -x

toolkit=$1
model_id=$2
lang_from=$3
lang_to=$4
text="$5"

http --form POST http://localhost:8088/annotator/translate toolkit=${toolkit} model_id=${model_id} lang_from=${lang_from} lang_to=${lang_to} text="${text}"