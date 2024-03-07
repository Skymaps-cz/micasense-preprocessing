#!/bin/bash --login
# The --login ensures the bash configuration is loaded,

# Temporarily disable strict mode and activate conda:
set +euo pipefail
conda activate micasense
# enable strict mode:
set -euo pipefail
