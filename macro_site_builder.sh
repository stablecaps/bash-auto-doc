#!/bin/bash -e

rm -rf  mkdocs_sys_bashrc gbm-docs

# python autodocumatix/main.py --infiles $(find /home/bsgt/stablecaps_bashrc/ -name "*.sh")  \
#     --out-dir `pwd`/gbm-docs \
#     --exclude-files "zsdoc" "test" "theme_settings_BACKUP" "unused_scrap_functions"
python gen_mkdocs_site.py

./make_mkdocs_site.sh

cd mkdocs_sys_bashrc
mkdocs build
mkdocs serve
cd -
