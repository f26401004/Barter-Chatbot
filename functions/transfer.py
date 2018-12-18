input_file = "./main.py"  # e.g. source.py
output_file = "./out.py"  # e.g out.py
with open(input_file, 'r') as source:
    with open(output_file, 'a+') as result:
        for line in source:
            line = line.replace('\t', '    ')
            result.write(line)