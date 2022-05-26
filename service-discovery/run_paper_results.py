import sys
from pprint import pformat
import os
from python.header import *

def change_key(file, key, val):
    #make sure we don't overwrite an original config file
    assert(file not in config_files.values())
    if type(key) is list:
        for k in key:
            regex = "\"s@^" + k + " .*@" + k + " " + str(val) + "@g\"" 
            result = os.system("sed -i " + regex + " " + file)
            #make sure the command succeeded
            assert(result == 0)
    else:
        regex = "\"s@^" + key + " .*@" + key + " " + str(val) + "@g\"" 
        result = os.system("sed -i " + regex + " " + file)
        #make sure the command succeeded
        assert(result == 0)

def run_sim(config_file):
    result = os.system("java -Xmx200000m -cp ./lib/djep-1.0.0.jar:lib/jep-2.3.0.jar:target/service-discovery-1.0-SNAPSHOT.jar:lib/gs-core-2.0.jar:lib/pherd-1.0.jar:lib/mbox2-1.0.jar:lib/gs-ui-swing-2.0.jar -ea peersim.Simulator " + config_file + "> /dev/null 2> /dev/null")
    assert(result == 0)

#turn a running config into a folder name
def params_to_dir(params, type):
    result = ""
    for param in params:
        if(features[param]['type'] == type):
            result += "_" + param + "-" + str(params[param])
    return result
#set all the parameters in the config file
def set_params(config_file, out_dir, params):
    os.system("dos2unix " + config_file)
    change_key(config_file, "control.3.rangeExperiment", out_dir)
    for param in params:
        key = features[param]['keyword']
        value = params[param]
        change_key(config_file, key, value)

def main() -> int:
    os.system('rm -rf ' + result_dir)

    for protocol in config_files.keys():
        print("Running ", protocol)
        in_config = config_files[protocol]
        #used to avoid running the same config multiple times
        already_run = set()
        params = {}
        is_attack = 'attack' in protocol
        for main_feature in features.keys():
            is_attack_feature = features[main_feature]['type'] == 'attack'
            #don't iterate benign features for attack configs
            #and vice-versa
            if( is_attack != is_attack_feature):
                continue
        
            for val in features[main_feature]['vals']:
                params[main_feature] = val
                #set default values for the remaining features
                for feature in features.keys():
                    if feature != main_feature:
                        #use defaultAttack for attack features during an attack scenario
                        if(is_attack and (features[feature]['type'] == 'attack') ):
                            params[feature] = features[feature]['defaultAttack']
                        else:    
                            params[feature] = features[feature]['default']
                print("params:", params)
                #by default you can't have a set of dictionaries
                #pformat turns a dictionary into a string that can be added to the set
                if(pformat(params) not in already_run):
                    already_run.add(pformat(params))
                    if(is_attack):
                        out_dir = result_dir + "/attack/" + protocol.replace("attack","").replace('D', 'd') + "/" + params_to_dir(params, type='attack') + "/"
                    else:    
                        out_dir = result_dir + "/benign/" + protocol + "/" + params_to_dir(params, type='benign') + "/"
                    os.system('mkdir -p ' + out_dir)
                    out_config = out_dir + 'config.txt'
                    os.system('cp ' + in_config + " " + out_config)
                    set_params(out_config, out_dir, params)
                    #run_sim(out_config)

if __name__ == '__main__':
    sys.exit(main())
