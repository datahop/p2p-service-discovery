#!/bin/bash

SYBIL_SIZES='10 50 100 500' 
ATTACK_TOPICS='1 3 5'
EVIL_PERCENTS='0.01 0.05 0.1 0.2 0.3'

IN_CONFIG='config/randomTopicAttack.cfg'

function run_sim(){
    OUT_CONFIG="config/attackspam_topic${TOPIC}_sybilsize${SYBIL_SIZE}_attackerPercent${PERCENT_EVIL}.cfg"
	echo output config $OUT_CONFIG
	cp $IN_CONFIG $OUT_CONFIG
    dos2unix $OUT_CONFIG
    sed -i "s/^init.1uniqueNodeID.iPSize .*$/init.1uniqueNodeID.iPSize $SYBIL_SIZE/g" $OUT_CONFIG
    sed -i "s/^init.1uniqueNodeID.nodeIdSize .*$/init.1uniqueNodeID.nodeIdSize $SYBIL_SIZE/g" $OUT_CONFIG
    sed -i "s/^init.1uniqueNodeID.attackTopic .*$/init.1uniqueNodeID.attackTopic $TOPIC/g" $OUT_CONFIG
    sed -i "s/^init.1uniqueNodeID.percentEvil .*$/init.1uniqueNodeID.percentEvil $PERCENT_EVIL/g" $OUT_CONFIG
    LOG_FILE="logs_attackTopic${TOPIC}_sybilSize${SYBIL_SIZE}_attackPercent${PERCENT_EVIL}"
    echo log file $LOG_FILE
    sed -i "s/^control.3.rangeExperiment .*$/control.3.rangeExperiment $LOG_FILE/g" $OUT_CONFIG
    ./run.sh $OUT_CONFIG &> /dev/null
}

for SYBIL_SIZE in $SYBIL_SIZES
do
	echo running size $SYBIL_SIZE
    for TOPIC in $ATTACK_TOPICS
    do 
	    echo running attack topic $TOPIC
        for PERCENT_EVIL in $EVIL_PERCENTS
        do
	        echo running percent evil $PERCENT_EVIL
            run_sim
        done
    done
done
