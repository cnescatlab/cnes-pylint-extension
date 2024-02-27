# cnes-pylint-extension

cnes-pylint-extension is a python checker, which adds CNES specific checks to pylint.

cnes-pylint-extension checks the following rules :
- R5101 - multiple-exit-statements
- R5102 - too-many-decorators
- R5103 - bad-exit-condition
- R5104 - builtin-name-used
- R5105 - recursive-call
- R5106 - use-context-manager
- R5401 - sys-exit-used
- R5402 - os-environ-used
- R5403 - sys-argv-used
- W9095 - missing-docstring-field
- W9096 - malformed-docstring-field
- W9097 - missing-docstring-description

cnes-pylint-extension checks the following metrics :
- R5301 - too-high-complexity (default < 25)
- R5302 - too-high-complexity-simplified (default < 20)
- R5201 - too-few-comments (default > 20%)

# Available versions :
- Version 1.0 - compatible pylint 1.5
- Version 2.0 - compatible pylint 1.6
- Version 3.0 - compatible pylint 1.7.4 and 1.9.1
- Version 4.0 - compatible pylint 2.1.1
- Version 5.0 - compatible pylint >=2.5.0,<2.12.0
- Version 6.0 - compatible pylint >=2.12,<3.0.0
- Version 7.0 - compatible pylint >=3.0.0,<4.0.0
    - **warning**: At 7.0.0 release, latest pylint was 3.0.3. If you encounter issue with pylint>3.0.3 and <4.0.0 please open an issue.

# To use these checkers:

## Install from PIP
`pip install cnes-pylint-extension`

## Install from sources

### Install Pylint

`pip install "pylint>=3.0.0,<4.0.0"`

### Install CNES Pylint extension checkers

Download the project's code source then add the checkers subdirectory to your PYTHONPATH :

```
unzip cnes-pylint-extension.zip
cd cnes-pylint-extension
echo export PYTHONPATH=$PYTHONPATH:$PWD/checkers >> ~/.bashrc
source ~/.bashrc
```

To enable Pylint to use the extension, you need to edit your pylintrc file, and add "cnes_checker" to the plugins list.
```
[MASTER]
load-plugins=cnes_checker
...
```

## Usage

Pylint is now able to use the extension.

Otherwise, add `--load-plugins=cnes_checker` to your pylint command line in order to activate it.
