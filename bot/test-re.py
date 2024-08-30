import re

function_regex = r'<function=(\w+)>(.*?)<\/function>|<function=(\w+)>(.*)'

test_strings = [
    '<function=hello>{world}</function>',
    '<function=goodbye>{cruel world}"</function>',
    '<function=spacey>{extra space} </function>',
    '<function=noclose>{this has no closing tag}',
    '<function=empty></function>'
]


for test_string in test_strings:
    function_name = ""
    arguments = ""

    match = re.search(function_regex, test_string)
    if match:
        if match.group(1):  # Case with closing tag
            function_name = match.group(1)
            arguments = match.group(2)
        else:  # Case without closing tag
            function_name = match.group(3)
            arguments = match.group(4)
    else:
        print(f"No match found for: {test_string}")

    print("---")
    print(f"Original string: {test_string}")
    arguments = re.sub(r'[\s"]+$', '', arguments)
    print(f"Function name: {function_name}")
    print(f"Arguments: {arguments}")
