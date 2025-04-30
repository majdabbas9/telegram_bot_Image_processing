import re

str1 = "concatv"

if (match := re.match(r'^(cc|concat)(h|v|horizontal|vertical)?$', str1)):
    print(match.groups())
else:
    print("No match")