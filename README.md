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
- R5302 - too-high-complexity-simplified (defailt < 20)
- R5201 - too-few-comments (default > 20%)

Available versions :
- Version 1.0 - compatible pylint 1.5
- Version 2.0 - compatible pylint 1.6
- Version 3.0 - compatible pylint 1.7.4
- Version 4.0 - compatible pylint 2.1.1
