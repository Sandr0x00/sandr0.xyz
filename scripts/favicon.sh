#!/bin/bash

resize() {
    inkscape resources/favicon.svg --export-type=png -h $1 --export-filename=static/favicon-$1.png
}

resize 32
resize 76
resize 120
resize 128
resize 144
resize 152
resize 167
resize 180
resize 192
resize 196
resize 228