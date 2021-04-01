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
import math
import os

csv.field_size_limit(sys.maxsize)

def extractAlphanumeric(InputString):
    from string import ascii_letters, digits
    return "".join([ch for ch in InputString if ch in (ascii_letters + digits)])

def analyzeMessages(dirs):
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    i=0
    fig3, ax3 = plt.subplots()
    fig4, ax4 = plt.subplots()

    for log_dir in dirs:
        #print(log_dir)

        try:
            df = pd.read_csv(log_dir + '/messages.csv')
            df['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='Total')

            df2 = df.loc[(df['type'] == 'MSG_TICKET_REQUEST')]
            df2['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='MSG_TICKET_REQUEST')
            df2 = df.loc[(df['type'] == 'MSG_FIND')]
            df2['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='MSG_FIND')
            df2 = df.loc[(df['type'] == 'MSG_RESPONSE')]
            df2['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='MSG_RESPONSE')
            df2 = df.loc[(df['type'] == 'MSG_TICKET_RESPONSE')]
            df2['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='MSG_TICKET_RESPONSE')
            df2 = df.loc[(df['type'] == 'MSG_REGISTER')]
            df2['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='MSG_REGISTER')
            df2 = df.loc[(df['type'] == 'MSG_REGISTER_RESPONSE')]
            df2['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='MSG_REGISTER_RESPONSE')
            df2 = df.loc[(df['type'] == 'MSG_TOPIC_QUERY')]
            df2['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='MSG_TOPIC_QUERY')
            df2 = df.loc[(df['type'] == 'MSG_TOPIC_QUERY_REPLY')]
            df2['dst'].value_counts().plot(ax=ax1, kind='line', xticks=[], title="Message received by node", label='MSG_TOPIC_QUERY_REPLY')



            width=0.3
            margin=width*i
            #print(df['type'].value_counts().index)
            if not (df.type == 'MSG_FIND').any():
                new_row = { 'id':0, 'type':'MSG_FIND', 'src':0, 'dst':0, 'topic':'NaN', 'sent/received':'NaN'}
                df = df.append(new_row,ignore_index=True)
            if not (df.type == 'MSG_TICKET_REQUEST').any():
                new_row = { 'id':0, 'type':'MSG_TICKET_REQUEST', 'src':0, 'dst':0, 'topic':'NaN', 'sent/received':'NaN'}
                df = df.append(new_row,ignore_index=True)
            if not (df.type == 'MSG_RESPONSE').any():
                new_row = { 'id':0, 'type':'MSG_RESPONSE', 'src':0, 'dst':0, 'topic':'NaN', 'sent/received':'NaN'}
                df = df.append(new_row,ignore_index=True)
            if not (df.type == 'MSG_TICKET_RESPONSE').any():
                new_row = { 'id':0, 'type':'MSG_TICKET_RESPONSE', 'src':0, 'dst':0, 'topic':'NaN', 'sent/received':'NaN'}
                df = df.append(new_row,ignore_index=True)
            table = df['type'].value_counts().sort_index()

            ax2.bar(np.arange(len(table.index))+margin,table.values,width=width, label=log_dir)

            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & ((df['bucket'] == 254)| (df['bucket'] == 255)| (df['bucket'] == 256))]
            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='256-254')
            print(df3['dst'].value_counts())
            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & ((df['bucket'] == 251) | (df['bucket'] == 252)| (df['bucket'] == 253))]
            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='253-251')
            print(df3['dst'].value_counts())
            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & ((df['bucket'] == 248)| (df['bucket'] == 249)| (df['bucket'] == 250))]
            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='250-248')
            print(df3['dst'].value_counts())
            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & ((df['bucket'] == 245)| (df['bucket'] == 246)| (df['bucket'] == 247))]
            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='247-245')
            print(df3['dst'].value_counts())
            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & ((df['bucket'] == 242) | (df['bucket'] == 243) | (df['bucket'] == 244))]
            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='244-242')
            print(df3['dst'].value_counts())
            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & ((df['bucket'] == 239) | (df['bucket'] == 240) | (df['bucket'] == 241))]
            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='241-239')
            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 253) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='253')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 252) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='252')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 251) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='251')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 250) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='250')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 249) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='249')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 248) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='248')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 247) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='247')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 246) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='246')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 245) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='245')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 244) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='244')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 243) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='243')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 242) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='242')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 241) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='241')
#            print(df3['dst'].value_counts())
#            df3 = df.loc[(df['type'] == 'MSG_REGISTER') & (df['bucket'] == 240) ]
#            df3['dst'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message received by node", label='240')

            df3 = df.loc[(df['type'] == 'MSG_REGISTER_RESPONSE') & (df['waiting_time'] != -1)]
            df3['waiting_time'].value_counts().plot(ax=ax4, kind='line', xticks=[], title="Register responses waiting times", label='Total')
            print(df3['waiting_time'].value_counts())

            i = i+1
        except pd.errors.EmptyDataError:
            print("messages file empty")
            return
        except FileNotFoundError:
            print("messages file not found")
            return
        #df['src'].value_counts().plot(ax=ax3, kind='line', xticks=[], title="Message sent by node", label=log_dir)


    ticks = table.index
    ax2.set_xticks(range(len(ticks)))
    ax2.set_xticklabels(ticks)

    ax1.legend()
    ax3.legend()
    #add line showing how the result should be
    ax1.plot([ax1.get_xlim()[0], ax1.get_xlim()[1]], [(ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2, (ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2], 'k-', lw=2, color='r')
    ax1.text(ax1.get_xlim()[1]*0.8, (ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2, "optimal", size=8)
    ax1.set_xlabel("Nodes")
    ax1.set_ylabel("#Messages")
    fig1.savefig(OUTDIR + '/messages_received.png')

#    ax3.plot([ax3.get_xlim()[0], ax3.get_xlim()[1]], [(ax3.get_ylim()[1] - ax3.get_ylim()[0]) / 2, (ax3.get_ylim()[1] - ax3.get_ylim()[0]) / 2], 'k-', lw=2, color='r')
#    ax3.text(ax3.get_xlim()[1]*0.8, (ax3.get_ylim()[1] - ax3.get_ylim()[0]) / 2, "optimal", size=8)
    ax3.set_xlabel("Nodes")
    ax3.set_ylabel("#Messages")
    fig3.savefig(OUTDIR + '/messages_received_bucket.png')

    ax4.set_xlabel("Messages")
    ax4.set_ylabel("Waiting times")
    fig4.savefig(OUTDIR + '/messages_waiting_times.png')


    ax2.legend()
    fig2.savefig(OUTDIR + '/messages_types.png')



    #ax3.legend()
    #add line showing how the result should be
    #ax3.plot([ax3.get_xlim()[0], ax3.get_xlim()[1]], [(ax3.get_ylim()[1] - ax3.get_ylim()[0]) / 2, (ax3.get_ylim()[1] - ax3.get_ylim()[0]) / 2], 'k-', lw=2, color='r')
    #ax3.text(ax3.get_xlim()[1]*0.8, (ax3.get_ylim()[1] - ax3.get_ylim()[0]) / 2, "optimal", size=12)
    #fig3.savefig('messages_sent.png')


def analyzeActiveRegistrations(dirs):
    """ Plot a bar chart showing the number of registrations by malicious and good nodes.
    """

    fig1, ax1 = plt.subplots()

    topics = []
    i=0
    for log_dir in dirs:
        normal_registration_count_per_topic = {}
        with open(log_dir + '/registration_stats.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            ncol = len(next(reader)) # Read first line and count columns
            numOfTopics = int((ncol-1)/2)
            #print('Number of topics: ', numOfTopics)
            topics = ['t'+str(x) for x in range(1, numOfTopics+1)]
            for topic in topics:
                normal_registration_count_per_topic[topic] = 0
        with open(log_dir + '/registration_stats.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            nrows = 0
            for row in reader:
                for topic in topics:
                    normal = int(row[topic + '-normal'])
                    normal_registration_count_per_topic[topic] += normal
                nrows += 1

        normal_counts = [normal_registration_count_per_topic[topic]/nrows for topic in topics]
        width=0.3
        margin=width*i
        i=i+1
    #    print(np.arange(len(topics)))
    #    print(normal_counts)
        ax1.bar(np.arange(len(topics))+margin, normal_counts, width,label=log_dir)

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax1.set_ylabel('Number of registrations')
    ax1.set_xlabel('Topics')
    ax1.set_title('Active Registrations')
    ax1.set_xticks(np.arange(len(topics)))
    ax1.set_xticklabels(topics)
    ax1.legend()

    plt.savefig(OUTDIR + '/registration_origin.png')

def analyzeActiveRegistrationsMalicious(dirs):
    """ Plot a bar chart showing the number of registrations by malicious and good nodes.
    """

    topics = []
    evil_registration_count_per_topic = {}
    normal_registration_count_per_topic = {}
    for log_dir in dirs:
        evil_registration_count_per_topic = {}
        normal_registration_count_per_topic = {}
        with open(log_dir + '/registration_stats.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            ncol = len(next(reader)) # Read first line and count columns
            numOfTopics = int((ncol-1)/2)
            #print('Number of topics: ', numOfTopics)
            topics = ['t'+str(x) for x in range(1, numOfTopics+1)]
            for topic in topics:
                normal_registration_count_per_topic[topic] = 0
                evil_registration_count_per_topic[topic] = 0
        with open(log_dir + '/registration_stats.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            nrows = 0
            for row in reader:
                for topic in topics:
                    normal = int(row[topic + '-normal'])
                    evil = int(row[topic + '-evil'])
                    normal_registration_count_per_topic[topic] += normal
                    evil_registration_count_per_topic[topic] += evil
                nrows += 1
        normal_counts = [normal_registration_count_per_topic[topic]/nrows for topic in topics]
        evil_counts = [evil_registration_count_per_topic[topic]/nrows for topic in topics]
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        x_values = [x-width/2 for x in range(1, numOfTopics+1)]
        rects1 = ax.bar(x_values, normal_counts, width,
                label='Good registrations')
        x_values = [x+width/2 for x in range(1, numOfTopics+1)]
        rects2 = ax.bar(x_values, evil_counts, width,
                label='Malicious registrations')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Number of registrations')
        ax.set_xlabel('Topics')
        ax.set_title('Active Registrations ' + log_dir)
        ax.set_xticks(x_values)
        ax.set_xticklabels(topics)
        ax.legend()

        plt.savefig(OUTDIR + '/registration_origin_withmalicious.png')

def analyzeRegistrations(dirs):

    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    #fig3, ax3 = plt.subplots()

    for log_dir in dirs:
        df = pd.read_csv(log_dir + '/registeredRegistrant.csv')
        df2 = pd.read_csv(log_dir + '/registeredRegistrar.csv')

        if len(df['topic'].unique()) > 1:

            data={}
            data2={}
    #        print(df)
            for index, row in df.iterrows():
                #print(index,row['topic'],row['nodeId'],row['count'])
                if row['nodeId'] in data:
                    count = data[row['nodeId']] + row ['count']
                    #print(count)
                    data[row['nodeId']] = count
                else :
                    data[row['nodeId']] = row['count']
                #print(index, ': ', row['topic'], 'has', row['nodeid'], 'calories',row['count'])
            #for item in data.items():
            #    print(item)
            for index, row in df2.iterrows():
                #print(index,row['topic'],row['nodeId'],row['count'])
                if row['nodeId'] in data2:
                    count = data2[row['nodeId']] + row ['count']
                    #print(count)
                    data2[row['nodeId']] = count
                else :
                    data2[row['nodeId']] = row['count']

    #print(data.values())
        ax1.plot(sorted(data.values(),reverse=True),label=log_dir)
        ax2.plot(sorted(data2.values(),reverse=True),label=log_dir)

    ax1.set_title('Registrations by registrant')
    #add line showing how the result should be
    #ax1.plot([ax1.get_xlim()[0], ax1.get_xlim()[1]], [(ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2, (ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2], 'k-', lw=2, color='r')
    #ax1.text(ax1.get_xlim()[1]*0.8, (ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2, "optimal", size=12)
    ax1.set_ylim(bottom=0)
    ax1.set_xlabel("Nodes")
    ax1.set_ylabel("#placed registrations")
    ax2.set_xlabel("Nodes")
    ax2.set_ylabel("#Accepted registrations")
    ax1.legend()
    ax2.legend()
    #ax3.legend()
    fig1.savefig(OUTDIR + '/registrations_registrant_total.png')

    ax2.set_title('Registrations by registrar')
    #ax2.plot([ax2.get_xlim()[0], ax2.get_xlim()[1]], [(ax2.get_ylim()[1] - ax2.get_ylim()[0]) / 2, (ax2.get_ylim()[1] - ax2.get_ylim()[0]) / 2], 'k-', lw=2, color='r')
    #ax2.text(ax2.get_xlim()[1]*0.8, (ax2.get_ylim()[1] - ax2.get_ylim()[0]) / 2, "optimal", size=12)
    ax2.set_ylim(bottom=0)
    ax1.set_xlabel("Nodes")
    ax1.set_ylabel("#accepted registrations")
    fig2.savefig(OUTDIR + '/registrations_registrar_total.png')

    #    ax3.set_title('Registrations by topics (average)')
    #    ticks = sorted_table['topic'].values
    #    ax3.set_xticks(range(len(ticks)))
    #    ax3.set_xticklabels(ticks)


    #    fig3.savefig(OUTDIR + '/registrations_topic.png')

def analyzeRegistrarDistribution(dirs):
    fig, ax1 = plt.subplots()
    ax1.tick_params(bottom=False,
                labelbottom=False)
    topics = set()

    colors = ['red', 'green', 'blue', 'orange']
    x = []
    y = []
    topics = []
    dir_nums = []
    c = []

    try:
        for log_dir in dirs:
            stats = {}
    #        print(log_dir)
            dir_num = dirs.index(log_dir)
            with open(log_dir + '/1000000_registrations.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    node = row['host']
                    topic = row['topic']
                    topics.append(topic)
                    dir_nums.append(dir_num)
                    x.append(int(node))
                    c.append(colors[dir_num])

        counter = 0
        topics_set = set(topics)
        for topic in topics:
            topic_index = sorted(topics_set).index(topic)
            dir_offset = dir_nums[counter]*0.3
            y.append(topic_index + dir_offset)
            counter += 1

        scatter = ax1.scatter(x, y, c=c)
        legend_elements = []
        for log_dir in dirs:
            dir_num = dirs.index(log_dir)
            color = colors[dir_num]
            legend_elements.append(Line2D([0], [0], marker='o', color=color, label=log_dir,
                              markerfacecolor=color, markersize=15))
        print(legend_elements)
        ax1.legend(handles=legend_elements)
        ax1.set_title("Registrars")
        fig.savefig(OUTDIR + '/registrar_distribution.png')
    except FileNotFoundError:
        print("file not found")
        return



def analyzeRegistrantDistribution(dirs):
    fig, ax1 = plt.subplots()
    ax1.tick_params(bottom=False,
                labelbottom=False)
    topics = set()
    topicIDs = {}

    colors = ['sandybrown', 'green', 'blue', 'orange', 'darkviolet']
    x = []
    y = []
    s = []
    c = []

    x_nondiscovered = []
    y_nondiscovered = []
    s_nondiscovered = []
    c_nondiscovered = []
    registrants_per_topic = {}
    discovered_per_topic = {}

    global_max = 0
    for log_dir in dirs:
        stats = {}
        #print(log_dir)
        dir_num = dirs.index(log_dir)
        print("dir_num", dir_num)
        with open(log_dir + '/registeredRegistrant.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                topic = row['topic']
                node = row['nodeId']
                if topic not in registrants_per_topic:
                    registrants_per_topic[topic] = set()
                registrants_per_topic[topic].add(node)

                if node not in stats:
                    stats[node] = {}
                if topic not in stats[node]:
                    stats[node][topic] = 0

        with open(log_dir + '/operations.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            max_size = 0
            for row in reader:
                if row['type'] == 'LookupOperation' or row['type'] == 'LookupTicketOperation':
                    assert (row['topic'] != '')
                    discovered = row['discovered_list'].split()
                    topic = row['topic']
                    topicID = row['topicID']
                    if(topic not in topicIDs):
                        topicIDs[topic] = topicID
                    topics.add(topic)
                    for node in discovered:
                        if node not in stats:
                            stats[node] = {}
                        if topic not in stats[node]:
                            stats[node][topic] = 0
                        stats[node][topic] += 1
                        if(stats[node][topic] > max_size):
                            max_size = stats[node][topic]
                        if(stats[node][topic] > global_max):
                            global_max = stats[node][topic]

            for node in stats:
                for topic in stats[node]:
                    topic_index = sorted(topics).index(topic)
                    if(stats[node][topic] == 0):
                        x_nondiscovered.append(int(node))
                        y_nondiscovered.append(topic_index + dir_num*0.3)
                        c_nondiscovered.append('red')
                        s_nondiscovered.append(max_size*3)
                    else:
                        x.append(int(node))
                        y.append(topic_index + dir_num*0.3)
                        c.append(colors[topic_index])
                        s.append(stats[node][topic])
                        if topic not in discovered_per_topic:
                            discovered_per_topic[topic] = set()
                        discovered_per_topic[topic].add(node)
    #mark topic hashes
    for topic in topicIDs:
        topicID = int(topicIDs[topic])
        topic_index = sorted(topics).index(topic)
        ax1.scatter(topicID,topic_index, s=global_max*2, marker='X',color='black',linewidths=1)
        all = registrants_per_topic[topic].union(discovered_per_topic[topic])
        #print("Topic ", topic, "has", len(registrants_per_topic[topic]), "reported registrants.")
        print("Topic ", topic, "has", len(all), "all registrants.")
        #print("Topic ", topic, "has", len(discovered_per_topic[topic]), "discovered registrants.")
        print("Topic ", topic, "has", len(discovered_per_topic[topic])/len(all), "ratio discovered/all.")
        ax1.annotate(str("%.2f" % (100*len(discovered_per_topic[topic])/len(all))) + "% registrants discovered", xy=(1000, topic_index+0.1), xytext=(10001, topic_index+0.11), fontsize=12)

    ax1.scatter(x, y, c=c, s=s)
    ax1.set_yticks(np.arange(len(topics)))
    ax1.set_yticklabels(sorted(topics))
    #ax1.scatter(x_nondiscovered, y_nondiscovered, c=c_nondiscovered, s=s_nondiscovered, marker = '|')
    legend_elements = []
    for log_dir in dirs:
        dir_num = dirs.index(log_dir)
        color = colors[dir_num]
        legend_elements.append(Line2D([0], [0], marker='o', color=color, label="Discovered registrants",
                          markerfacecolor=color, markersize=10))

    legend_elements.append(Line2D([0], [0], marker='|', color='red', label='Non-discovered registrants',
                          markerfacecolor='black', markersize=10))
    legend_elements.append(Line2D([0], [0], marker='X', color='black', label='Topic hash',
                          markerfacecolor='black', markersize=10))
    #print(legend_elements)
    ax1.legend(handles=legend_elements)
    ax1.set_title("Discovered Registrants ID Distribution - NoSpam/Random")
    fig.savefig(OUTDIR + '/registrant_distribution.png')

def analyzeOperations(dirs):
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    fig2, ax2 = plt.subplots()
    #fig3, ax3 = plt.subplots()

    x = ['RegisterOperation','LookupOperation']
    x_val = 1
    x_vals = []
    total_malicious_list = []
    total_discovered_list = []

    i=0
    labels=['ClosestDiscance','RandomBucket','AllBuckets']
    for log_dir in dirs:
        #print(log_dir)
        df = pd.read_csv(log_dir + '/operations.csv')
        #print(df)

        meantimes={}
        errtimes={}
        for topic in df['topic'].unique():
            meantimes[topic] = df[df.topic == topic]['returned_hops'].mean()
            errtimes[topic] = df[df.topic == topic]['returned_hops'].std()

        mean={}
        err={}
        for key in sorted(meantimes.keys()) :
            mean[key] = meantimes[key]
        for key in sorted(errtimes.keys()) :
            err[key] = errtimes[key]

        width=0.3
        margin=width*i

        #print(np.arange(len(mean.keys())))
        #print(mean.values())
        ax2.bar(np.arange(len(mean.keys()))+margin, mean.values(),yerr=err.values(),width=width,label=labels[i])
        i = i+1
        #print(df['returned_hops'].mean())
        #ax2.bar(log_dir, df['returned_hops'].mean(), yerr=df['returned_hops'].std(), capsize=10)
        ax2.set_title("Avg Lookup Hop Count Spam")
        ax2.set_xticks(range(len(mean.keys())))
        ax2.set_xticklabels(mean.keys())
        print(df.query("type == 'LookupOperation' or type == 'LookupTicketOperation'")['malicious'].sum())
        print(df.query("type == 'LookupOperation' or type == 'LookupTicketOperation'")['discovered'].sum())
        total_malicious = df.query("type == 'LookupOperation' or type == 'LookupTicketOperation'")['malicious'].sum()
        total_discovered = df.query("type == 'LookupOperation' or type == 'LookupTicketOperation'")['discovered'].sum()
        total_malicious_list.append(total_malicious)
        total_discovered_list.append(total_discovered)
        x_vals.append(x_val)
        x_val += 3

    #print('x_vals: ', x_vals)
    width = 1.0  # the width of the bars
    x_values = [x-width/2 for x in x_vals]
    #ax3.bar(x_values, total_malicious_list, width, label='Malicious')
    #x_values = [x+width/2 for x in x_vals]
    #ax3.bar(x_values, total_discovered_list, width, label='All')
    #ax3.set_title("Malicious nodes out of all lookup results")
    #ax3.set_xticks(x_vals)
    #ax3.set_xticklabels(dirs)

    ax2.legend()
    #ax3.legend()
    fig2.savefig(OUTDIR + '/lookup_hopcount.png')
    #fig3.savefig('malicious_discovered.png')

def analyzeEclipsedNodesOverTime(dirs):
    #print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    fig, ax1 = plt.subplots()
    colors = ['red', 'green', 'blue']

    for log_dir in dirs:
    #print(log_dir)
        df = pd.read_csv(log_dir + '/eclipse_counts.csv')
        ax1.set_title("Number of eclipsed nodes over time")
        ax1.plot(df['time'], df['numberOfNodes'], label=log_dir)

    ax1.legend()
    plt.savefig(OUTDIR + '/eclipsed_node_over_time.png')

def analyzeEclipsedNodeDistribution(dirs):

    fig, ax1 = plt.subplots()
    ax1.tick_params(bottom=False,
                labelbottom=False)
    colors = ['red', 'green', 'blue', 'black']
    markers = ["o" , "v" , "^" , "<", ">"]
    topics = set()
    for log_dir in dirs:
        x = []
        y = []
        m = []
        c = []
        # get only the columns you want from the csv file
        df1 = pd.read_csv(log_dir + '/node_information.csv', usecols=['nodeID', 'topicID'])
        node_to_topicID = df1.set_index('nodeID')['topicID'].to_dict()
        df2 = pd.read_csv(log_dir + '/node_information.csv', usecols=['nodeID', 'is_evil?'])
        is_evil_node = df2.set_index('nodeID')['is_evil?'].to_dict()

        uneclipsed_nodes_set = None
        eclipsed_nodes_set = None
        evil_nodes_set = None
        with open(log_dir + '/eclipse_counts.csv', newline='') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                if row['time'] != '3500000':
                    continue

                eclipsed_nodes = row['eclipsedNodes'].split()
                eclipsed_nodes_set = set(eclipsed_nodes)
                uneclipsed_nodes = row['UnEclipsedNodes'].split()
                uneclipsed_nodes_set = set(uneclipsed_nodes)
                evil_nodes = row['EvilNodes'].split()
                evil_nodes_set = set(evil_nodes)

        for topic in node_to_topicID.values():
            topics.add(topic)


        IDs = []
        id_to_short = {}
        for node in is_evil_node.keys():
            IDs.append(node)
        for topic in topics:
            IDs.append(topic)

        IDs = sorted(IDs)
        short_num = 0
        for identifier in IDs:
            id_to_short[identifier] = short_num
            short_num += 1

        x,y = [],[]
        for topic in topics:
            y.append(id_to_short[topic])
            x.append(id_to_short[topic])

        ax1.scatter(x,y, s=100,marker='|',color='black',linewidths=1)

        x,y = [],[]
        for node in eclipsed_nodes_set:
            y.append(id_to_short[node_to_topicID[node]])
            x.append(id_to_short[node])

        ax1.scatter(x,y, s=10,marker='|',color='red',linewidths=1)

        x,y = [],[]
        for node in uneclipsed_nodes_set:
            y.append(id_to_short[node_to_topicID[node]])
            x.append(id_to_short[node])

        ax1.scatter(x,y, s=10,marker='|',color='green',linewidths=1)

        x,y = [],[]
        for node in evil_nodes_set:
            y.append(id_to_short[node_to_topicID[node]])
            x.append(id_to_short[node])
        ax1.scatter(x,y, s=10,marker='|',color='orange',linewidths=1)

    #ax1.set_yticks([])
    topics_list = [id_to_short[x] for x in topics]
    tick_labels = ['topic'+str(x) for x in range(1, len(topics_list)+1)]
    #print('Tick labels: ', tick_labels)
    #print('topics_list: ', topics_list)
    ax1.set_yticks(sorted(topics_list))
    ax1.set_yticklabels(tick_labels)
    ax1.scatter(x, y, color=c, marker='o')
    legend_elements = []
    legend_elements = [Line2D([0], [0], marker='|',  color='red', label='Eclipsed Node'),
                    Line2D([0], [0], marker='|', color='green', label='Non-Eclipsed Node'),
                    Line2D([0], [0], marker='|', color='orange', label='Malicious Node'),
                    Line2D([0], [0], marker='|', color='black', label='Topic ID')]

    ax1.legend(handles=legend_elements, bbox_to_anchor=(0,1.02,1,0.2), loc="lower left",
                mode="expand", borderaxespad=0, ncol=4)
    #ax1.legend(handles=legend_elements, loc='upper center')
    ax1.set_ylabel('Topics')
    ax1.set_xlabel('Node status')

    plt.savefig(OUTDIR + '/node_type_dist.png')


def analyzeStorageUtilisation(dirs):

    for log_dir in dirs:
        fig, ax = plt.subplots()
        df = pd.read_csv(log_dir + '/storage_utilisation.csv')
        topics = []
        for column_name in df.columns:
            if column_name == "time":
                continue
            topics.append(column_name)
        log_dir1 = extractAlphanumeric(log_dir)
        ax.set_title("Storage utilisation over time in " + log_dir1)
        for topic in topics:
            ax.plot(df['time']/1000, df[topic], label=topic)

        ax.legend()
        #ax.set_xlim([10000,None])

        ax.set_ylabel('Average utilisation of storage space')
        ax.set_xlabel('time (sec)')
        plt.savefig(OUTDIR + '/storage_utilisation_' + log_dir1 + '.png')

# plot per-topic, average waiting times and number of rejected
def analyzeWaitingTimes(dirs):

    for log_dir in dirs:
        fig, ax1 = plt.subplots()
        df = pd.read_csv(log_dir + '/waiting_times.csv')
        topics = set()
        for column_name in df.columns:
            if column_name == "time":
                continue
            if 'wait' in column_name:
                parts = column_name.split('_')
                topics.add(parts[0])
        log_dir1 = extractAlphanumeric(log_dir)
        ax1.set_title("Average waiting times over time for " + log_dir1)
        for topic in topics:
            ax1.plot(df['time']/1000, df[topic+'_wait'], label=topic)

        ax1.legend()
        ax1.set_ylabel('Waiting time in msec')
        ax1.set_xlabel('time (sec)')
        plt.savefig(OUTDIR + '/waiting_times_' + log_dir1 + '.png')

        fig, ax2 = plt.subplots()
        ax2.set_title("Average cumulative waiting times over time for " + log_dir1)
        for topic in topics:
            ax2.plot(df['time']/1000, df[topic+'_cumWait'], label=topic)
        ax2.legend()
        ax2.set_ylabel('Cumulative waiting time in msec')
        ax2.set_xlabel('time (sec)')
        plt.savefig(OUTDIR + '/cumulative_waiting_times_' + log_dir1 + '.png')

        fig, ax3 = plt.subplots()
        ax3.set_title("Quantity of rejected ticket requests (already registered) over time for " + log_dir1)
        for topic in topics:
            ax3.plot(df['time']/1000, df[topic+'_reject'], label=topic)
        ax3.legend()
        ax3.set_ylabel('Number of ticket requests')
        ax3.set_xlabel('time (sec)')
        plt.savefig(OUTDIR + '/rejected_tickets_' + log_dir1 + '.png')

# plot per-topic, average waiting times and number of rejected
def analyzeWaitingTimesBucket(dirs):

    for log_dir in dirs:
        fig, ax1 = plt.subplots()
        df = pd.read_csv(log_dir + '/waiting_times_bucket.csv')
        topics = set()
        for column_name in df.columns:
            #print(column_name)
            if column_name == "time":
                continue
            if 't1' in column_name:
                parts = column_name
                topics.add(parts)
        ax1.set_title("Average waiting times over time")
        for topic in topics:
            df2 = df[df[topic] > 0.0]
            ax1.plot(df2['time']/1000, df2[topic], label=topic)

        ax1.legend()
        ax1.set_ylabel('Waiting time in msec')
        ax1.set_xlabel('time (sec)')
        plt.savefig(OUTDIR + '/waiting_times_bucket.png')

        fig, ax2 = plt.subplots()
        df = pd.read_csv(log_dir + '/waiting_cumulative_times_bucket.csv')
        topics = set()
        for column_name in df.columns:
            if column_name == "time":
                continue
            if 't1' in column_name:
                parts = column_name
                topics.add(parts)
        ax2.set_title("Average cumulative waiting times over time")
        for topic in topics:
            df2 = df[df[topic] > 0.0]
            ax2.plot(df2['time']/1000, df2[topic]/1000, label=topic)
        ax2.legend()
        ax2.set_ylabel('Cumulative waiting time in msec')
        ax2.set_xlabel('time (sec)')
        plt.savefig(OUTDIR + '/waiting_times_cumulative_bucket.png')

        fig, ax3 = plt.subplots()
        ax3.set_title("Average cumulative waiting times per topic")
        topics = set()
        buckets = set()
        for column_name in df.columns:
            if column_name == "time":
                continue
            parts = column_name.split('-')
            topics.add(parts[0])
            buckets.add(parts[1])

        topics = sorted(topics)
        buckets = sorted(buckets)
        width=0.15
        i=0
        #print(buckets)
        for topic in topics:
            mean={}
            margin=width*i
            for bucket in buckets:
                df2 = df[df[topic+"-"+bucket] > 0.0]
                mean[bucket] = df2[topic+"-"+bucket].mean()

            #print(np.arange(len(mean.keys()))+margin)
            ax3.bar(np.arange(len(mean.keys()))+margin, mean.values(),width=width,label=topic)

            i=i+1


        ax3.legend()
        ax3.set_ylabel('Cumulative waiting time in msec')
        ax3.set_xlabel('time (sec)')
        ax3.set_xticks(np.arange(len(buckets)))
        ax3.set_xticklabels(buckets)
        plt.savefig(OUTDIR + '/waiting_times_cumulative_bucket_avg.png')



def analyzeNumberOfMessages(dirs):

    for log_dir in dirs:
        fig, ax = plt.subplots()
        df = pd.read_csv(log_dir + '/msg_stats.csv')
        log_dir1 = extractAlphanumeric(log_dir)
        ax.set_title("Exchanged messages over time for  " + log_dir1)
        ax.plot(df['time']/1000, df['MSG_REGISTER'], label='reg')
        ax.plot(df['time']/1000, df['MSG_REGISTER_RESPONSE'], label='reg_response')
        ax.plot(df['time']/1000, df['MSG_TICKET_REQUEST'], label='ticket_req')
        ax.plot(df['time']/1000, df['MSG_TICKET_RESPONSE'], label='ticket_response')
        ax.plot(df['time']/1000, df['MSG_TOPIC_QUERY'], label='query')
        ax.plot(df['time']/1000, df['MSG_TOPIC_QUERY_REPLY'], label='query_reply')

        ax.legend()
        ax.set_xlabel('time (sec)')
        ax.set_ylabel('Number of exchanged regiser/response messages')
        plt.savefig(OUTDIR + '/message_quantity_' + log_dir1 + '.png')

def analyzeRegistrations2(dirs):

    for log_dir in dirs:
        df = pd.read_csv(log_dir + '/registeredRegistrant.csv')
        if len(df['topic'].unique()) == 1:
            fig1, ax1 = plt.subplots()
            fig2, ax2 = plt.subplots()
        else:
            fig1, ax1 = plt.subplots(len(df['topic'].unique()))
            fig2, ax2 = plt.subplots(len(df['topic'].unique()))
            fig3, ax3 = plt.subplots()
            fig4, ax4 = plt.subplots()

    j=0
    for log_dir in dirs:
        df = pd.read_csv(log_dir + '/registeredRegistrant.csv')
        df2 = pd.read_csv(log_dir + '/registeredRegistrar.csv')

        #print(sorted(df['count'].values,reverse=True))
        if len(df['topic'].unique()) == 1:

            ax1.plot(sorted(df['count'].values,reverse=True))
            ax2.plot(sorted(df2['count'].values,reverse=True))

            ax1.set_title('Registrations by registrant')
            #ax1.plot([ax1.get_xlim()[0], ax1.get_xlim()[1]], [(ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2, (ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2], 'k-', lw=2, color='r')
    #        ax1.axhline(y = 16, color = 'r', linestyle = '-')
        #    ax1.text(ax1.get_xlim()[1]*0.8, (ax1.get_ylim()[1] - ax1.get_ylim()[0]) / 2, "optimal", size=12)
            ax1.set_ylim(bottom=0)
            ax1.set_xlabel("Nodes")
            ax1.set_ylabel("#placed registrations")
            fig1.savefig(OUTDIR + '/registrations_registrant.png')

            ax2.set_title('Registrations by registrar')
    #        ax2.axhline(y = 16, color = 'r', linestyle = '-')

        #    ax2.plot([ax2.get_xlim()[0], ax2.get_xlim()[1]], [(ax2.get_ylim()[1] - ax2.get_ylim()[0]) / 2, (ax2.get_ylim()[1] - ax2.get_ylim()[0]) / 2], 'k-', lw=2, color='r')
        #    ax2.text(ax2.get_xlim()[1]*0.8, (ax2.get_ylim()[1] - ax2.get_ylim()[0]) / 2, "optimal", size=12)
            ax2.set_ylim(bottom=0)
            ax2.set_xlabel("Nodes")
            ax2.set_ylabel("#Accepted registrations")
            fig2.savefig(OUTDIR + '/registrations_registrar.png')

        else:
            plt.figure(figsize=(100,100))
            plt.figure(figsize=(100,100))

            ax3.set_title('Registrations by registrant')
            ax3.set_ylabel("#placed registrations")

            ax4.set_title('Registrations by registrar')
            ax4.set_ylabel("#Received registrations")

            i=0
            for topic in sorted(df['topic'].unique()):
                print(topic)
                fig1.suptitle('Registrations by registrant')
                fig2.suptitle('Registrations by registrar')
                ax1[i].plot(sorted(df[df.topic == topic]['count'].values,reverse=True),label=log_dir)
                ax2[i].plot(sorted(df2[df2.topic == topic]['count'].values,reverse=True),label=log_dir)
                ax1[i].set(ylabel=topic)
                ax1[i].set_ylim([0,None])
                ax2[i].set(ylabel=topic)
                ax2[i].set_ylim([0,None])
                i=i+1
                if i !=len(df['topic'].unique()):
                    ax1[i-1].set_xticklabels([])
                    ax2[i-1].set_xticklabels([])
                else:
                    ax1[i-1].set_xlabel('Nodes')
                    ax2[i-1].set_xlabel('Nodes')

            ax1[0].legend()
            ax1[0].legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=2)
            ax2[0].legend()
            ax2[0].legend(bbox_to_anchor=(0, 1, 1, 0), loc="lower left", mode="expand", ncol=2)
            meanregistrant={}
            errregistrant={}
            meanregistrar={}
            errregistrar={}
            for topic in df['topic'].unique():
                meanregistrant[topic] = df[df.topic == topic]['count'].mean()
                errregistrant[topic] = df[df.topic == topic]['count'].std()
                meanregistrar[topic] = df2[df2.topic == topic]['count'].mean()
                errregistrar[topic] = df2[df2.topic == topic]['count'].std()
                #meanavgdisc[topic] = df[df.topic == topic]['average_discovery_time'].mean()
                #erravgdisc[topic] = df[df.topic == topic]['average_discovery_time'].std()
                #print(meantimes)
            mean={}
            err={}
            width=0.3
            margin=width*j
            j=j+1
            for key in sorted(meanregistrant.keys()) :
                mean[key] = meanregistrant[key]
            for key in sorted(errregistrant.keys()) :
                err[key] = errregistrant[key]
            ax3.bar(np.arange(len(mean.keys()))+margin, mean.values(),yerr=err.values(),width=width,label=log_dir)
            for key in sorted(meanregistrar.keys()) :
                mean[key] = meanregistrar[key]
            for key in sorted(errregistrar.keys()) :
                err[key] = errregistrar[key]

            ax4.bar(np.arange(len(mean.keys()))+margin, mean.values(),yerr=err.values(),width=width,label=log_dir)

    ax3.legend()
    ax3.set_xticks(np.arange(len(mean.keys())))
    ax3.set_xticklabels(mean.keys())
    ax3.set_xlabel("Nodes")
    ax4.legend()
    ax4.set_xticks(np.arange(len(mean.keys())))
    ax4.set_xticklabels(mean.keys())
    ax4.set_xlabel("Nodes")

    fig5, ax5 = plt.subplots()
    table = pd.read_csv(log_dir + '/registeredTopics.csv')
    sorted_table = table.sort_values(by='count',ascending=False)
    ax5.bar(np.arange(len(sorted_table['count'].values)),sorted_table['count'].values, label=log_dir)
    ax5.set_title('Registrations by topics (average)')
    ticks = sorted_table['topic'].values
    ax5.set_xticks(range(len(ticks)))
    ax5.set_xticklabels(ticks)

    fig1.savefig(OUTDIR + '/registrations_registrant.png')
    fig2.savefig(OUTDIR + '/registrations_registrar.png')
    fig3.savefig(OUTDIR + '/registrations_registrant_bar.png')
    fig4.savefig(OUTDIR + '/registrations_registrar_bar.png')
    fig5.savefig(OUTDIR + '/registrations_topic.png')

def analyzeRegistrationTime(dirs):
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    fig1, ax1 = plt.subplots()
    fig2, ax2 = plt.subplots()
    fig3, ax3 = plt.subplots()
    fig4, ax4 = plt.subplots()
    fig5, ax5 = plt.subplots()

    i=0
    width=0.3
    labels = ['NoSpam','Spam']
    for log_dir in dirs:
        #print(log_dir)
        df = pd.read_csv(log_dir + '/registeredTopicsTime.csv')

        if len(df['topic'].unique()) == 1:
            ax1.plot(sorted(df['times_registered'].values,reverse=True))
            ax2.plot(sorted(df['min_registration_time'].values,reverse=True))
            ax3.plot(sorted(df['average_registration_time'].values,reverse=True))
            ax4.plot(sorted(df['min_discovery_time'].values,reverse=True))
            #ax5.plot(sorted(df['average_discovery_time'].values,reverse=True))

        else:
            meantimes = {}
            errtimes = {}
            meanminreg = {}
            errminreg = {}
            meanavgreg = {}
            erravgreg = {}
            meanmindisc = {}
            errmindisc = {}
            registrations = {}
            #meanavgdisc = {}
            #erravgdisc = {}
            for topic in df['topic'].unique():
                meantimes[topic] = df[df.topic == topic]['times_registered'].mean()/1000
                errtimes[topic] = df[df.topic == topic]['times_registered'].std()/1000
                meanminreg[topic] = df[df.topic == topic]['min_registration_time'].mean()/1000
                errminreg[topic] = df[df.topic == topic]['min_registration_time'].std()/1000
                meanavgreg[topic] = df[df.topic == topic]['average_registration_time'].mean()/1000
                erravgreg[topic] = df[df.topic == topic]['average_registration_time'].std()/1000
                meanmindisc[topic] = df[df.topic == topic]['min_discovery_time'].mean()/1000
                errmindisc[topic] = df[df.topic == topic]['min_discovery_time'].std()/1000
                registrations[topic] = df[df.topic == topic]['registrant'].value_counts()
                #meanavgdisc[topic] = df[df.topic == topic]['average_discovery_time'].mean()
                #erravgdisc[topic] = df[df.topic == topic]['average_discovery_time'].std()
                #print(meantimes)
            mean={}
            err={}
            margin=width*i
            for key in sorted(meantimes.keys()) :
                mean[key] = meantimes[key]
            for key in sorted(errtimes.keys()) :
                err[key] = errtimes[key]
            ax1.bar(np.arange(len(mean.keys()))+margin, mean.values(),yerr=err.values(),width=width,label=labels[i])
            for key in sorted(meanminreg.keys()) :
                mean[key] = meanminreg[key]
            for key in sorted(errminreg.keys()) :
                err[key] = errminreg[key]
            ax2.bar(np.arange(len(mean.keys()))+margin, mean.values(),yerr=err.values(),width=width,label=labels[i])
            for key in sorted(meanavgreg.keys()) :
                mean[key] = meanavgreg[key]
            for key in sorted(erravgreg.keys()) :
                err[key] = erravgreg[key]
            ax3.bar(np.arange(len(mean.keys()))+margin, mean.values(),yerr=err.values(),width=width,label=labels[i])
            for key in sorted(meanmindisc.keys()) :
                mean[key] = meanmindisc[key]
            for key in sorted(errmindisc.keys()) :
                err[key] = errmindisc[key]
            ax4.bar(np.arange(len(mean.keys()))+margin, mean.values(),yerr=err.values(),width=width,label=labels[i])
            for key in sorted(registrations.keys()) :
                mean[key] = registrations[key]
#            ax5.bar(np.arange(len(mean.keys()))+margin, mean.values(),width=width,label=labels[i])
            i=i+1
            #ax5.bar(df['topic'].unique(), meanavgdisc.values(),yerr=erravgdisc.values())
            ax1.legend()
            ax2.legend()
            ax3.legend()
            ax4.legend()
#            ax5.legend()

    ax1.set_title('Total # registrations by registrant')
    ax2.set_title('Time required for the first registration')
    ax3.set_title('Average registration time per node')
    ax4.set_title('Time between registration to first time discovery')
#    ax5.set_title('Registrants per topic')
    ax1.set_xticks(np.arange(len(mean.keys())))
    ax1.set_xticklabels(mean.keys())
    ax2.set_xticks(np.arange(len(mean.keys())))
    ax2.set_xticklabels(mean.keys())
    ax3.set_xticks(np.arange(len(mean.keys())))
    ax3.set_xticklabels(mean.keys())
    ax4.set_xticks(np.arange(len(mean.keys())))
    ax4.set_xticklabels(mean.keys())
#    ax5.set_xticks(np.arange(len(mean.keys())))
#    ax5.set_xticklabels(mean.keys())
    ax1.set_ylim([0,None])
    ax2.set_ylim([0,None])
    ax3.set_ylim([0,None])
    ax4.set_ylim([0,None])
#    ax5.set_ylim([0,None])
    ax1.set_xlabel("Topics")
    ax2.set_xlabel("Topics")
    ax3.set_xlabel("Topics")
    ax4.set_xlabel("Topics")
#    ax5.set_xlabel("Topics")
    ax1.set_ylabel("Time (sec)")
    ax2.set_ylabel("Time (sec)")
    ax3.set_ylabel("Time (sec)")
    ax4.set_ylabel("Time (sec)")
#    ax5.set_ylabel("Time (sec)")
    #ax5.legend()
    fig1.savefig(OUTDIR + '/total_reg_by_registrant.png')
    fig2.savefig(OUTDIR + '/min_time_register.png')
    fig3.savefig(OUTDIR + '/avg_time_register.png')
    fig4.savefig(OUTDIR + '/min_time_discovery.png')
#    fig5.savefig(OUTDIR + '/registrants_topic.png')


def analyzeMessageReceivedByNodes(dirs):

    try:
        fig, ax = plt.subplots()
        i=0
        labels=['NoSpam','Spam']
        for log_dir in dirs:
            me = extractAlphanumeric(log_dir)
            x_vals = []
            y_vals = []
            topics = {}

            logdirname = extractAlphanumeric(log_dir)
            with open(log_dir + '/msg_received.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if 't' in row['numMsg']:
                        topics[row['Node']] = row['numMsg']
                    else:
                        y_vals.append(int(row['numMsg'])/36000)
                        x_vals.append(row['Node'])

                sorted_y_vals = sorted(y_vals)
                ax.plot(range(1,len(y_vals)+1), sorted_y_vals, label=labels[i])
                i=i+1
                #for topic in topics:
                #    plt.axvline(x=topic, color='b', label=topics[topic])
        ax.legend()
        ax.set_xticks([])
        #ax.set_yticks(ax.get_yticks()[::100])
        ax.set_xticklabels([])
        ax.set_ylabel('Number of received messages/sec')
        ax.set_xlabel('Nodes')

        ax.set_title('Message received by node')

        plt.savefig(OUTDIR + '/messages_received2')
    except FileNotFoundError:
        print("file not found")
        return

def analyzeRegistrationOverhead(dirs):
    try:
        fig, ax = plt.subplots()
        num_xvalues = len(dirs)
        width = 0.3
        i = 0
        ncol = 0
        numOfTopics = 0
        topics = []
        labels=['NoSpam','Spam']
        for log_dir in dirs:
            logdirname = extractAlphanumeric(log_dir)
    #        print(logdirname)
            with open(log_dir + '/register_overhead.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                ncols = len(next(reader)) # Read first line and count columns
                numOfTopics = int(ncols-1)
                topics = ['t'+str(x) for x in range(1, numOfTopics+1)]
                topics.append('overall')

            x_values = [x for x in range(5, ncols*5+1, 5)]
            y_values = []
            with open(log_dir + '/register_overhead.csv', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    for topic in topics:
                        y_values.append(float(row[topic]))
                        xs = [x-width*i for x in x_values]
    #        print('y_values: ', y_values)
    #        print('x_values: ', xs)
            #ax.legend()
            margin=width*i
            print(np.arange(len(topics)))
            ax.bar(np.arange(len(topics))+margin, y_values, width, label=labels[i])
            i = i + 1

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Number of Ticket/Register Requests until Registration')
        ax.set_title('Overhead of registrations')
        ax.set_xticks(np.arange(len(topics)))
        ax.set_xticklabels(topics)
        ax.legend()
        plt.savefig(OUTDIR + '/registration_overhead.png')
    except FileNotFoundError:
        print("file not found")
        return

if (len(sys.argv) < 2):
    print("Provide at least one directory with log files (messages.csv and 3500000_registrations.csv")
    exit(1)

OUTDIR = './'
if not os.path.exists(OUTDIR):
    os.makedirs(OUTDIR)

print('Will read logs from', sys.argv[1:])
print('Plots will be saved in ', OUTDIR);

analyzeMessages(sys.argv[1:])
analyzeRegistrations(sys.argv[1:])
analyzeRegistrations2(sys.argv[1:])
analyzeOperations(sys.argv[1:])
analyzeRegistrantDistribution(sys.argv[1:])
analyzeRegistrarDistribution(sys.argv[1:])
analyzeEclipsedNodesOverTime(sys.argv[1:])
analyzeActiveRegistrations(sys.argv[1:])
analyzeActiveRegistrationsMalicious(sys.argv[1:])
analyzeRegistrationTime(sys.argv[1:])
analyzeStorageUtilisation(sys.argv[1:])
analyzeWaitingTimes(sys.argv[1:])
analyzeWaitingTimesBucket(sys.argv[1:])

analyzeNumberOfMessages(sys.argv[1:])

analyzeRegistrationOverhead(sys.argv[1:]) # G5 (overhead of registrations)
analyzeMessageReceivedByNodes(sys.argv[1:]) # message received by nodes
#plt.show()
#analyzeEclipsedNodeDistribution(sys.argv[1:])
