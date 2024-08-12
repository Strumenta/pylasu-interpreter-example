# Pylasu Interpreter Example
This [Interpreter Example project](https://github.com/Strumenta/pylasu-interpreter-example) demonstrates an interpreter implementation using the [Pylasu](https://github.com/strumenta/pylasu) library. For details, you can check the the Virtual Meetup - [Building an interpreter in Python with Pylasu](https://www.youtube.com/watch?v=W1SqfflBwcc).

- Prerequisites: Python, Git
## Setup

### Installation

Clone the repository
```bash
git clone git@github.com:Strumenta/pylasu-interpreter-example.git
cd pylasu-interpreter-example
```

Activate the virtual environment
```python
python -m venv venv
source venv/bin/activate
pip install -r Requirements.txt
```

Generate the parsers  inside the **entity_parser** folder
```bash
sh generate_parsers.sh
```
### Usage

Run the interpreter though a local server at http://127.0.0.1:5000/
```bash
sh run_web.sh
```

### Version Compatibility
This project is designed to work with python 3.12. 
In case of version issues, you can use pyenv, e.g. 
```bash
pyenv install 3.<another-version>
pyenv local 3.<another-version>
```

