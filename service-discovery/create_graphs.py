import sys
from python.nsdi_plots import *
from python.header import *

OUTDIR_BASE = './plots/'

INDIR_BASE = os.path.abspath(result_dir)
OUTDIR_BASE = os.path.abspath(OUTDIR_BASE)
#if len(sys.argv) < 2:
#    print('Usage: ', sys.argv[0], ' <Path_to_Log_files> <OPTIONAL: Path_to_output_dir>' )
#    sys.exit(1) 

#LOGDIR = sys.argv[1]
#if len(sys.argv) > 2:
#    OUTDIR = sys.argv[2]



#createPerLookupOperationStats(LOGDIR)
#plotPerLookupOperation()
for simulation_type in ['benign']:
#for simulation_type in ['attack']:
    INDIR = INDIR_BASE + "/" + simulation_type + "/"
    OUTDIR = OUTDIR_BASE + "/" + simulation_type + "/"
    
    print("#######################" + simulation_type + "#######################")
    print('Will read logs from', INDIR)
    print('Plots will be saved in ', OUTDIR)

    if not os.path.exists(OUTDIR):
        os.makedirs(OUTDIR)

    os.chdir(INDIR)
    
    createPerNodeStats(INDIR)
   # showAverage(OUTDIR, simulation_type)
    plotPerNodeStats(OUTDIR, simulation_type)
    
#plotPerNodeStatsSplit(INDIR_BASE,OUTDIR_BASE+"/split/")
#plotRegistrationStatsSybil(INDIR_BASE,OUTDIR_BASE,0)
#plotRegistrationStatsPercent(INDIR_BASE,OUTDIR_BASE,0)
#plotRegistrationStatsSybil(INDIR_BASE,OUTDIR_BASE,149)
#plotRegistrationStatsPercent(INDIR_BASE,OUTDIR_BASE,149)
