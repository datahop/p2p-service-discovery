import matplotlib
import matplotlib.pyplot as plt

#label font
font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

#color palette
plt.style.use('seaborn-colorblind')

#figure size
default_figsize = (10,4)
matplotlib.rcParams["figure.figsize"] = default_figsize