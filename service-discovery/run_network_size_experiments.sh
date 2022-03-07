#!/bin/bash

SIZES='1000 2000 3000 4000 5000'
TOPICS='1 5 20 50 100'
ZIPFS='0.1 0.7 1.1'
BUCKET_SIZES='1 3 5 10'
BUCKET_ORDERS='0 1 2'
SPAM_OPTIONS='0 1'

DEFAULT_NETWORK_SIZE=5000
DEFAULT_TOPIC_NUM='5'

EXPERIMENT='network_size'
IN_CONFIGS='discv5dhtticket noattackdiscv4 discv5ticket discv5dhtnoticket'
IN_CONFIGS='discv5dhtticket noattackdiscv4 discv5ticket'
#IN_CONFIGS='noattackdiscv4'
#IN_CONFIGS='discv5dhtticket'

function run_sim(){

    STRATEGY='.'
    if [[ "$IN_CONFIG" == *discv4* ]]; then
        echo discv4
        STRATEGY='discv4'
    elif [[ "$IN_CONFIG" == *dhtticket* ]]; then
        echo dhtticket 
        STRATEGY='dhtticket'
    elif [[ "$IN_CONFIG" == *dhtnoticket* ]]; then
        echo dhtnoticket 
        STRATEGY='dhtnoticket'
    elif [[ "$IN_CONFIG" == *discv5* ]]; then
        echo discv5 
        STRATEGY='discv5'
    else
        echo "couldn't match config name to a strategy"
    fi

    OUT_CONFIG_FOLDER="./config/output/${EXPERIMENT}"
    OUT_CONFIG="${OUT_CONFIG_FOLDER}/${IN_CONFIG}_${SIZE}.cfg"
	echo output config $OUT_CONFIG
    mkdir -p "${OUT_CONFIG_FOLDER}"
	cp "config/${IN_CONFIG}.cfg" $OUT_CONFIG
    dos2unix $OUT_CONFIG
	sed  -i "s/^SIZE .*$/SIZE $SIZE/g" $OUT_CONFIG 
	sed  -i "s/^control.0traffic.maxtopicnum .*$/control.0traffic.maxtopicnum $DEFAULT_TOPIC_NUM/g" $OUT_CONFIG 
    LOG_FOLDER="${EXPERIMENT}/${STRATEGY}"
    LOG_FILE="${LOG_FOLDER}/logs_${IN_CONFIG}_${EXPERIMENT}_${SIZE}"
    mkdir -p "${LOG_FOLDER}"
    echo log file $LOG_FILE
    sed -i "s@control.3.rangeExperiment.*@control.3.rangeExperiment $LOG_FILE@g" $OUT_CONFIG
    #./run.sh $OUT_CONFIG &> /dev/null
    ./run.sh $OUT_CONFIG 
}


for IN_CONFIG in $IN_CONFIGS
do
	echo running config $IN_CONFIG
    for SIZE in $SIZES
    do
	    echo running size $SIZE
        run_sim
    done
done
