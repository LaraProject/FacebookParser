# Facebook Parser

Facebook Parser is a python tool which can parse *facebook conversation json file* creating at the end a final **.json** file adapted.

## Installation
Use Python 3.5 or above

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install json
pip install re
pip install ftfy
pip install unidecode
```

## Usage
Don't forget to check if required libraries are imported
```python
import json
import re
import ftfy
import unidecode
```

Then, set up the correct settings : 
```python
#Settings            
delayBetween2Conv = 50000 #in milliseconds
nbMessages = 100
fbConvFilename = 'conversation_LouisRiad.json'
```

Then, you can run the parser ! :)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
