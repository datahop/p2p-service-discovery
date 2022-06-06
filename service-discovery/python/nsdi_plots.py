#!/usr/bin/python3
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from numpy import genfromtxt
import numpy as np
import array
import sys
import csv
import scipy.stats as sp # for calculating standard error
import os
import seaborn as sns
from .header import *

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

from enum import Enum, unique
@unique
class GraphType(Enum):
    line = 1
    bar = 2
    violin = 3


#csv.field_size_limit(sys.maxsize)

def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

def getProtocolFromPath(path):
    return  path.split('/')[0]


#security_features = ['idDistribution', 'sybilSize', 'attackTopic', 'percentEvil', 'discv5regs']
security_features = []
#current dir format: _size-3000_topic-40_...
def getFeatureListFromPath(path):
    print("Getting features from path:", path)
    result = set()
    for item in path.strip('/').split('/')[-1].split('_')[1:]:
        feature = item.split('-')[0]
        print("extrated feature:", feature)
        assert(feature not in result)
        if(feature in security_features):
            continue
        result.add(feature)
    return result

def getFeatureFromPath(feature, path):
    print("feature:", feature)
    print("path: ", path)
    return  path.split('_' + feature + '-')[1].split('_')[0].replace('/', '')

def createPerNodeStats(dir):
    features = set()
    df_list = []
    object_list = os.listdir(dir)
    dirs = []
    for obj in object_list:
        if(os.path.isdir(obj)):
            dirs.append(obj)
    
    for log_dir in dirs:
        print("log_dir:", log_dir)
        if(log_dir not in config_files.keys()): #['discv5', 'dht', 'dhtnoticket', 'discv4']):
            continue
        tmp = next(os.walk(log_dir))
        print("tmp:", tmp)
        sub_dirs = tmp[1]
        for subdir in sub_dirs:
            path = log_dir + '/' + subdir + '/'
            path.replace('//','/').rstrip()
            print("cwd:", os.getcwd())
            print('Reading folder: ', path+"|")

            try:
                df = pd.read_csv(path + 'msg_received.csv')
                protocol = getProtocolFromPath(path)
                df['protocol'] = protocol
                
                #include features read from the path
                dir_features = getFeatureListFromPath(path)
                if(len(features) == 0):
                    features = dir_features
                else:
                    #make sure we have the same set of features in every dir
                    assert(dir_features == features)

                for feature in features:
                    #we use ints, floats and strings
                    to_convert = getFeatureFromPath(feature, path)
                    try:
                        #try converting to int
                        value = int(to_convert)
                    except ValueError:
                        try:
                            #try converting to float
                            value = float(to_convert) 
                        except ValueError:
                            #if th above don't work, keep as string
                            value = to_convert
                    df[feature] = value

                df['percentageMaliciousDiscovered'] = np.where(df['discovered'] == 0, 0, df['maliciousDiscovered']/df['discovered'])
                df['percentageEclipsedLookups'] = np.where(df['lookupOperations'] == 0, 0, df['eclipsedLookupOperations']/df['lookupOperations'])

                if(protocol == 'discv4'):
                    #should be all 0 in discv4, but including anyway for sanity check
                    reg_cols = ['MSG_REGISTER', 'MSG_TICKET_REQUEST', 'MSG_TICKET_RESPONSE', 'MSG_REGISTER_RESPONSE']
                    df['registrationMsgs'] = df[reg_cols].sum(axis=1)
                    look_cols = ['MSG_FIND', 'MSG_RESPONSE', 'MSG_TOPIC_QUERY', 'MSG_TOPIC_QUERY_REPLY']
                    df['lookupMsgs'] = df[look_cols].sum(axis=1)    
                    #msg_cols=['MSG_FIND', 'MSG_RESPONSE', 'MSG_TOPIC_QUERY', 'MSG_TOPIC_QUERY_REPLY','MSG_REGISTER', 'MSG_TICKET_REQUEST', 'MSG_TICKET_RESPONSE', 'MSG_REGISTER_RESPONSE']
                    #df['totalMsg'] = df[msg_cols].sum(axis=1)  
                    df['totalMsg'] = df['lookupMsgs'] + (df['registrationMsgs'] / 4)

                else:
                    reg_cols = ['MSG_REGISTER', 'MSG_TICKET_REQUEST', 'MSG_TICKET_RESPONSE', 'MSG_REGISTER_RESPONSE', 'MSG_FIND', 'MSG_RESPONSE']
                    df['registrationMsgs'] = df[reg_cols].sum(axis=1)
                    look_cols = ['MSG_TOPIC_QUERY', 'MSG_TOPIC_QUERY_REPLY']
                    df['lookupMsgs'] = df[look_cols].sum(axis=1) 
                    #msg_cols=['MSG_REGISTER', 'MSG_TICKET_REQUEST', 'MSG_TICKET_RESPONSE', 'MSG_REGISTER_RESPONSE', 'MSG_FIND', 'MSG_RESPONSE','MSG_TOPIC_QUERY', 'MSG_TOPIC_QUERY_REPLY']
                    #df['totalMsg'] = df[msg_cols].sum(axis=1)    
                    df['totalMsg'] = df['lookupMsgs'] + (df['registrationMsgs'] / 4)


                df_list.append(df)
                df.to_csv(path + 'df.csv')
            except FileNotFoundError:
                print("Error: ", path + "msg_received.csv not found")
                quit()
    #merge all the dfs
    dfs = pd.concat(df_list, axis=0, ignore_index=True)
    #print(dfs)
    dfs.to_csv('dfs.csv')
    return dfs

# Used for eclipsing results
def createPerLookupOperationStats(dir):
    df_list = []
    object_list = os.listdir(dir)
    dirs = []
    for obj in object_list:
        if(os.path.isdir(obj)):
            dirs.append(obj)
    
    for log_dir in dirs:
        print("log_dir:", log_dir)
        tmp = next(os.walk(log_dir))
        print("tmp:", tmp)
        sub_dirs = tmp[1]
        for subdir in sub_dirs:
            path = log_dir + '/' + subdir + '/'
            path.replace('//','/')
            print('Reading folder ', path)
            try:
                df = pd.read_csv(path + 'eclipse_counts.csv')
                protocol = getProtocolFromPath(path)
                sybilSize = int(getFeatureFromPath('sybil_size', path))
                attackTopic = getFeatureFromPath('attackTopic', path)
                distribution = getFeatureFromPath('id_distribution', path)
                percentEvil = getFeatureFromPath('percentEvil', path)
                print("From path:", path, "Extracted protocol:", protocol, "sybil size:", sybilSize, "attack topic:", attackTopic, "ID distribution: ",distribution )

                percentDiscoveredField = 'PercentEvilDiscovered-t' + attackTopic
                percentEclipsedField = 'PercentEclipsed-t' + attackTopic
                df = df.loc[~(df[percentDiscoveredField] == 0)]
                print('Series: ', df[percentDiscoveredField])
                print('Here')
                df['PercentEvilDiscovered'] = df[percentDiscoveredField]
                df['PercentEclipsed'] = df[percentEclipsedField] 
                df['percentEvil'] = percentEvil
                
                df['protocol'] = protocol
                df['sybilSize'] = sybilSize
                df['attackTopic'] = attackTopic
                df['distribution'] = distribution
                 
                df_list.append(df)
                df.to_csv(path + 'df.csv')
            except FileNotFoundError:
                print("Error: ", path, "eclipse_counts.csv not found")
                quit()
    #merge all the dfs
    dfs = pd.concat(df_list, axis=0, ignore_index=True)
    #print(dfs)
    dfs.to_csv('dfs.csv')
    return dfs

def plotPerNodeStats(OUTDIR, simulation_type, graphType = GraphType.violin):
    #pd.set_option('display.max_rows', None)
    print("Reading:", os.getcwd(), "/dfs.csv")
    dfs = pd.read_csv('dfs.csv')
    
    #features = ['size']
    #default values for all the features
    defaults = {}
    for feature in features:
        if( (simulation_type == 'attack') and (features[feature]['type'] == 'attack')):
            defaults[feature] = features[feature]['defaultAttack']    
        else:
            defaults[feature] = features[feature]['default']

    print("############# Features:", features)
    print("############# Defaults:", defaults)

    #x-axis
    for feature in features:
        if(features[feature]['type'] != simulation_type):
            continue
        #make sure we don't modify the initial df
        df = dfs.copy(deep=True)
        #filter the df so that we only have default values for non-primary features
        for secondary_feature in features:
            if(features[secondary_feature]['type'] != simulation_type):
                continue
            if(secondary_feature != feature):
                print("Secondary Feature:",secondary_feature)
                df = df[df[secondary_feature] == defaults[secondary_feature]]
                #for attack scenarios take into account uniquely results from nodes involved in the attacked topic

                if(secondary_feature == "attackTopic" and defaults['attackTopic'] != 'ALL'):
                    df = df[df['nodeTopic'] == defaults['attackTopic']]
        
        
        print("Feature:",feature)

        #y-axis
        if simulation_type == 'benign':
            y_vals = benign_y_vals
        else:
            y_vals = attack_y_vals

        #df.to_csv("dupa.csv")
        

        for graph in y_vals:
            fig, ax = plt.subplots(figsize=(10, 4))
            print("Plotting y-axis:", graph, "x-axis", feature)
            #quit(1)
            if "Eclipsed" in graph:
                graphType = GraphType.bar
            else:
                graphType = GraphType.violin
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            if(graphType == GraphType.violin):
                violin = sns.violinplot(ax = ax,
                                data = df,
                                x = feature,
                                y = graph,
                                hue = 'protocol',
                                inner=None,#"point",  # Representation of the datapoints in the violin interior.
                                split = False, 
                                scale = 'width', #make the width of each violin equal (by default it's the area)
                                cut = 0, #cut = 0 limits the violin range within the range of the observed data 
                                palette='colorblind'
                                ) 
                
                #the below set the y_lim from header.py to make graphs more readible
                #it also prints a max value as an annotation is its above the set y_lim
                lim_key = graphType.name + "_" + feature + "_" + graph
                protocol_xpos = {'discv5' : -0.35,
                                 'dht' : -0.15,
                                 'discv4'    : 0.15,
                                 'dhtTicket': 0.35
                                }
                if(lim_key in y_lims):
                    y_lim = y_lims[lim_key]
                    ax.set_ylim(0, y_lim)
                    #indicate the maximum values                    
                    groups = df.groupby('protocol')
                    max_vals = {}
                    
                    for protocol, group in groups:
                        if(protocol not in max_vals):
                            max_vals[protocol] = {}
                        i = 0
                        for x_val in features[feature]['vals']:
                            assert(x_val not in max_vals[protocol])
                            local_df = group[group[feature] == x_val]
                            max_val = local_df[graph].max()
                            max_vals[protocol][x_val] = max_val
                            if(max_val > y_lim):
                                violin.annotate("max:" + human_format(max_val), xy = (protocol_xpos[protocol]+i, 0.7*y_lim), horizontalalignment = 'center', color='red', rotation=90)
                            i += 1


                    

            else:
                groups = df.groupby('protocol')

                #set bar in the middle of x-tics
                i = (len(groups)-1) * -0.5
                i = -1.5
                for protocol, group in groups:
                    #NaN -> 0
                    group.to_csv("dupa.csv")
                    print("protocol:", protocol)
                    #print("group:", group)
                    group = group.fillna(0)
                    avg = group.groupby(feature)[graph].mean()
                    #print("avg_index:", avg.index)
                    #x_vals = range(0, int(avg.index[-1]),  int(avg.index[-1]/len(avg.index)))
                    #x_vals = list(x_vals)
                    
                    #print('x_vals: ', x_vals)
                    std = group.groupby(feature)[graph].std()
                    if(graphType == GraphType.line):
                        avg.plot(x=feature, y=graph, yerr=std, ax=ax, legend=True, label=protocol)
                    elif(graphType == GraphType.bar):
                        #calculate bar width based on the max x-value and the number of protocols
                        #width = avg.index[-1]/(len(groups)*(len(groups)+3))
                        width = 0.1
                        #x = [int(val) + (i * width) for val in avg.index]
                        #x = [int(val) + (i * width) for val in x_vals]
                        x = np.arange(len(avg.index))+(width*i)
                        #print("x:", x)
                        #print("avg:", avg)
                        plt.bar(x, avg, width, label=protocolPrettyText[protocol])
                     #   ax.legend(loc=9)
                        ticks = avg.index
                        ax.set_xticks(range(len(ticks)))
                        ax.set_xticklabels(ticks)
                        i += 1
                    else:
                        print("Unknown graph type:", graphType)
                        exit(-1)

                        #evenly space the x ticks
                        ax.set_xticks(x_vals)
                        ax.set_xticklabels(list(avg.index))
            ax.set_xlabel(titlePrettyText[feature])
            ax.set_ylabel(titlePrettyText[graph])
            ax.spines['top'].set_visible(True)
            ax.spines['right'].set_visible(True)
            ax.spines['bottom'].set_visible(True)
            ax.spines['left'].set_visible(True)
            ax.legend(bbox_to_anchor=(0.5, 1.1), loc='upper center', ncol=4)
            fig.set_size_inches(9, 6.5)

            try:
 #               print(ticksPrettyText[feature])
                ax.set_xticklabels(ticksPrettyText[feature])
            except KeyError:
                print("ticksPrettyText not found")
            #ax.set_title(titlePrettyText[graph])
            fig.tight_layout()
            fig.savefig(OUTDIR + '/' + graphType.name + "_" + feature + "_" + graph,format='eps')

            #quit()

def plotPerLookupOperation():
    pd.set_option('display.max_rows', None)
    dfs = pd.read_csv('dfs.csv')
    features = ['sybilSize', 'attackTopic', 'distribution', 'percentEvil']
    #default values for all the features
    defaults = {'sybilSize':'5', 'attackTopic':'1', 'distribution':'uniform', 'percentEvil':'0.2'}
    for feature in features:
        defaults[feature] = dfs[feature].value_counts().idxmax()

    #x-axis
    for feature in features:
        #make sure we don't modify the initial df
        df = dfs.copy(deep=True)
        #filter the df so that we only have default values for non-primary features
        for secondary_feature in features:
            if(secondary_feature != feature):
                df = df[df[secondary_feature] == defaults[secondary_feature]]
        #y-axis
        for graph in ['PercentEvilDiscovered', 'PercentEclipsed']:
            fig, ax = plt.subplots()
            for protocol, group in df.groupby('protocol'):
                #NaN -> 0
                group = group.fillna(0)
                avg = group.groupby(feature)[graph].mean()
                std = group.groupby(feature)[graph].std()
                bx = avg.plot(x=feature, y=graph, yerr=std, ax=ax, legend=True, label=protocol)
                bx.set_xlabel(feature)
                bx.set_ylabel("Average " + graph)
                bx.set_title(graph)
                
            fig.savefig(OUTDIR + '/' + feature + "_" + graph)


