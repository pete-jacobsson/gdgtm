### This script should generate the docs and put them in the docs folder

#!/bin/bash
python -m pydoc -w gdgtm.manage && mv gdgtm.manage.html docs/
python -m pydoc -w gdgtm.get && mv gdgtm.get.html docs/
python -m pydoc -w gdgtm.transform && mv gdgtm.transform.html docs/