

import argparse
import io
import os
import sys

import jinja2
import roman

def jinja_filter_liters_to_imperial_gallons(text):
    return float(text) * 0.2199692

def jinja_filter_liters_to_us_gallons(text):
    return float(text) * 0.2641720

def jinja_filter_arabic_to_roman(number):

    try:
        number = int(number)
    except:
        sys.stderr.write("Number needs to be an integer.")
        return 'NaN'

    return roman.toRoman(number)

# Added US / IMPERIAL gallon switch
def get_jinja_environment(template_dir, config):
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                             autoescape=jinja2.select_autoescape(['html', 'xml']),
                             extensions=['jinja2.ext.do'])
    if (config.us_gallons):
        env.filters['l2gal'] = jinja_filter_liters_to_us_gallons
    else:
        env.filters['l2gal'] = jinja_filter_liters_to_imperial_gallons
    
    env.filters['arabic2roman'] = jinja_filter_arabic_to_roman
    return env


def main(argv):
    args = argparse.ArgumentParser(description='Templater')
    args.add_argument(
        '--template',
        dest='template',
        required=True,
        metavar='FILENAME.j2',
        help='Jinja2 template file')
    args.add_argument(
        '--input',
        dest='input',
        required=True,
        metavar='INPUT',
        help='Input filename'
    )
    args.add_argument(
        '--use-us-gallons',
        dest='us_gallons',
        required=False,
        action='store_true',
        help='Switch to US gallons'
    )
    args.add_argument(
        '-V',
        dest='added_variables',
        required=False,
        action='append',
        help='Add more variables'
    )

    config = args.parse_args(argv)

    env = get_jinja_environment(os.path.dirname(config.template), config)
    template = env.get_template(config.template)

    content = ""
    with open(config.input, 'r') as f:
        content = f.read()

    variables = {
        'content': content,
        'TEMPLATE': config.template,
        'INPUT': config.input,
    }

    # YAML header
    load_variables = False
    last_list_key = ""
    with open(config.input, 'r') as f:
        for line in f:
            # Negate variable loading state
            if (line.strip() == "---"):
                load_variables = not load_variables
            else:
                loaded_dict_values = line.strip().split()
                if (len(loaded_dict_values) == 2 and loaded_dict_values[0] != '-'):
                    variables[loaded_dict_values[0].replace(':', '')] = loaded_dict_values[1]
                elif (len(loaded_dict_values) == 1):
                    variables[loaded_dict_values[0].replace(':', '')] = []
                    last_list_key = loaded_dict_values[0].replace(':', '')
                elif (loaded_dict_values[0] == '-'):
                    variables[last_list_key].append(loaded_dict_values[1])

    # Load added variables
    for var in config.added_variables:
        key, value = var.strip().split("=")
        variables[key] = value

    # Use \n even on Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, newline='\n')

    result = template.render(variables)

    print(result)


if __name__ == '__main__':
    main(sys.argv[1:])
