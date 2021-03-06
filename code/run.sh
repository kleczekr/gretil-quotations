#!/usr/bin/env bash
sh generate_word_vectors.sh;
python calculate_sanskrit2sanskrit.py;
python split_into_files.py;
cd ../work;
find . -name "*.parallels" | parallel -j80 --bar -I% --max-args 1 python3 ../code/merge_quotes.py %;
find . -name "*.csv" | parallel -j80 --bar -I% --max-args 1 python3 ../code/csv_to_html.py %;
rm *csv;
mv *html ../html/;


