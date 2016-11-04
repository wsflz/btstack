#!/usr/bin/env python
#
# Create project files for all BTstack embedded examples in zephyr/samples/btstack

import os
import shutil
import sys
import time
import subprocess

mk_template = '''#
# BTstack example 'EXAMPLE' for nRF5-zephyr port
#
# Generated by TOOL
# On DATE

obj-y += EXAMPLE.o
obj-y += main.o
ccflags-y += -I${ZEPHYR_BASE}/subsys/btstack
ccflags-y += -I${ZEPHYR_BASE}/subsys/bluetooth/controller/ll

'''

gatt_update_template = '''#!/bin/sh
DIR=`dirname $0`
BTSTACK_ROOT=$DIR/../../../btstack
echo "Creating src/EXAMPLE.h from EXAMPLE.gatt"
$BTSTACK_ROOT/tool/compile_gatt.py $BTSTACK_ROOT/example/EXAMPLE.gatt $DIR/src/EXAMPLE.h
'''

# get script path
script_path = os.path.abspath(os.path.dirname(sys.argv[0]))

# validate nRF5x SDK root by reading include/zephyr.h
zpehyr_base = script_path + "/../../../"

zephyr_h = ""
try:
    with open(zpehyr_base + '/include/zephyr.h', 'r') as fin:
         zephyr_h = fin.read()  # Read the contents of the file into memory.
except:
    pass
if not "_ZEPHYR__H" in zephyr_h:
    print("Cannot find Zpehyr root. Make sure BTstack is checked out as zephyr/btstack")
    sys.exit(1)

# path to examples
examples_embedded = script_path + "/../../example/"

# path to zephyr/samples/btstack
apps_btstack = zpehyr_base + "/samples/btstack/"

print("Creating examples in samples/btstack:")

# iterate over btstack examples
for file in os.listdir(examples_embedded):
    if not file.endswith(".c"):
        continue

    example = file[:-2]
    gatt_path = examples_embedded + example + ".gatt"

    # filter LE-only applications
    if not os.path.exists(gatt_path) and not example in [
        "ancs_cient_demo","gap_le_advertisements", "gatt_battery_query","gatt_browser","sm_pairing_central"]:
        continue
    if example == "spp_and_le_counter":
        continue

    # create folder
    apps_folder = apps_btstack + example + "/"
    if not os.path.exists(apps_folder):
        os.makedirs(apps_folder)

    # copy nrf5.conf
    shutil.copyfile(script_path + '/nrf5.conf', apps_folder + '/nrf5.conf')

    # copy Makefile
    shutil.copyfile(script_path + '/Makefile', apps_folder + 'Makefile')

    # create src folder
    src_folder = apps_folder + "src/"
    if not os.path.exists(src_folder):
        os.makedirs(src_folder)

    # create Makefile file
    with open(src_folder + "Makefile", "wt") as fout:
        fout.write(mk_template.replace("EXAMPLE", example).replace("TOOL", script_path).replace("DATE",time.strftime("%c")))

    # copy port main.c
    shutil.copyfile(script_path + '/main.c', src_folder + "/main.c")

    # copy example file
    shutil.copyfile(examples_embedded + file, src_folder + "/" + example + ".c")

    # create update_gatt.sh if .gatt file is present
    gatt_path = examples_embedded + example + ".gatt"
    if os.path.exists(gatt_path):
        update_gatt_script = apps_folder + "update_gatt_db.sh"
        with open(update_gatt_script, "wt") as fout:
            fout.write(gatt_update_template.replace("EXAMPLE", example))        
        os.chmod(update_gatt_script, 0o755)
        subprocess.call(update_gatt_script + "> /dev/null", shell=True)
        print("- %s including compiled GATT DB" % example)
    else:
        print("- %s" % example)

