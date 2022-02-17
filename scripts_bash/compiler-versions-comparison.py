# Using readlines()
import os 
cid_file = open('cids_to_compile58.txt', 'r')
cids = cid_file.readlines()

MAX_REBUILD=1
i = 0
for cid in cids:

    encoded_cid = cid.replace('\n', '')
    config_filename = "config" + str(encoded_cid) + ".config"


    python_cmd = f'python3 kernel_generator.py --compiler gcc10 --dev 1 --linux_version 5.8 --configs configs_tobuild/{config_filename} --local --mount_host_dev --checksize --tagbuild "test {encoded_cid} with gcc10 instead of gcc6" --json "build{encoded_cid}-gcc10.json" --checksize'
    

    # curl copying the config file
    curl_cmd = f"curl --silent http://tuxml-data.irisa.fr/data/configuration/{encoded_cid}/config -o  configs_tobuild/config{encoded_cid}.config"
    
    print(curl_cmd)
    print(python_cmd)

    os.system(curl_cmd)
    os.system(python_cmd)


    if i == MAX_REBUILD:
        break 
    i = i + 1
