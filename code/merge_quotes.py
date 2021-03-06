import sys
import os
import re
import string
from tqdm import tqdm
filename = sys.argv[1]
windowsize = 7
namedic = {}
threshold = 0.06
def populate_namedic(namedic):
    f = open("..//data/skt-gretil-filenames.tab",'r')
    c = 0 
    for line in f:
        m = re.search("^([^\t]+)\t(.+)", line) 
        if m:
            namedic[m.group(1)] = m.group(2) + "\n (" + m.group(1) + ")"
            c += 1


def clean_quotes(list_of_quotes):
    result_quotes = []    
    if list_of_quotes:
        list_of_quotes.sort(key=lambda x: x[2]) # we are sorting by the position values
        c = 0
        while c < len(list_of_quotes):
            current_quote = list_of_quotes[c]
            current_quote_position = current_quote[2]
            current_quote_score = current_quote[0]
            if c < (len(list_of_quotes)-1):
                next_quote = list_of_quotes[c+1]
                next_quote_position = next_quote[2]
                next_quote_score = next_quote[0]
                if next_quote_position >= current_quote_position and next_quote_position < current_quote_position+windowsize:
                    if next_quote_score < current_quote_score:
                        current_quote[0] = next_quote_score
                    current_quote_unsandhied = current_quote[3].split(" / ")
                    next_quote_unsandhied = next_quote[3].split(" / ")
                    for unsandhied_sentence in next_quote_unsandhied:
                        if not unsandhied_sentence in current_quote_unsandhied:
                            current_quote_unsandhied.append(unsandhied_sentence)
                    current_quote[3] = " / ".join(current_quote_unsandhied)
                    current_quote[2] = next_quote_position # give the current quote the position of the consumed quote, so in the next round it counts from the last consumed quote
                    c += 1 # this is so we skip the next quote in case it has been consumed
            if c <= len(list_of_quotes):
                result_quotes.append(current_quote)
            c += 1
    else:
        result_quotes = list_of_quotes
    return result_quotes
        
# first transform the quotes into lists:
def transform_file_to_list(filename):
    f = open(filename,'r')
    our_lines = [line.rstrip('\n') for line in f]
    converted_lines = []
    last_sandhied = ""
    current_quotes = []
    last_filename = ""
    last_position = 0
    last_unsandhied = ""
    line_count = 0
    for current_line in our_lines:
        current_line = current_line.replace("##","#") # I know this is lame post-processing
        split_line = current_line.split("\t")
        head = split_line[0].split("#")
        head_filename = head[0]
        head_position = int(head[1])
        head_unsandhied = head[2]
        head_sandhied = head[3]
        if len(split_line) > 1:
            for quote in split_line[1:]:
                quote_list = quote.split("#")
                if len(quote_list) == 5:
                    quote_filename = quote_list[0]
                    if quote_filename.strip()[:-4] in namedic.keys():
                        quote_filename = namedic[quote_filename.strip()[:-4]].replace("\n", " ")
                    quote_position = int(quote_list[1])
                    quote_score = float(quote_list[2])
                    #quote_final_score = (quote_score / (quote_sif))
                    quote_unsandhied = quote_list[3]
                    quote_sandhied = quote_list[4]
                    if quote_score < threshold and quote_filename.strip():
                        current_quotes.append([quote_score,quote_filename,quote_position,quote_unsandhied,quote_sandhied,line_count])
        if head_sandhied.split(' / ')[0] not in last_sandhied.split(' / ') and not str(head_sandhied.split(' / ')[0][1:]) in last_sandhied.split(' / '):

            next_quotes = []
            result_quotes = []
            for quote in current_quotes:
                if quote[-1] < line_count - (windowsize /2):
                    result_quotes.append(quote)
                else:
                    next_quotes.append(quote)
            result_quotes = clean_quotes(result_quotes)
            while (result_quotes != clean_quotes(result_quotes)):
                result_quotes = clean_quotes(result_quotes)
            converted_lines.append([[last_filename,last_position, last_unsandhied, last_sandhied],sorted(result_quotes)])
            current_quotes = next_quotes
            last_sandhied = head_sandhied
            last_filename = head[0]
            last_position = int(head[1])
            last_unsandhied = head[2]
        line_count += 1
    return converted_lines

def list_to_string(converted_list):
    result_string = ""
    for entry in converted_list:
        head_filename,head_position, head_unsandhied, head_sandhied = entry[0]
        result_string +=  "\n" + "\"" + str(head_position) + "\",\"" + head_sandhied + "\"" 
        for quote in entry[1]:
            quote_final_score,quote_filename,quote_position,quote_unsandhied,quote_sandhied,line_count = quote
            result_string +=  ",\"" + str(quote_final_score)[:5] + "#" + quote_filename + "#" + str(quote_position) + "#" + quote_sandhied + "\""
    return result_string
if not os.path.isfile(filename[:-4] + ".csv"):
    print(filename)
    populate_namedic(namedic)
    converted_list = transform_file_to_list(filename)
    print_string = list_to_string(converted_list)
    with open(filename[:-4] + ".csv", "w") as text_file:
        text_file.write(print_string)
