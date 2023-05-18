#!/usr/bin/python3.8
import os
import shutil
import chaospy as cp
import easyvvuq as uq
from easyvvuq.actions import Actions, CreateRunDirectory, Encode, Decode, ExecuteLocal

# Get the current working directory
cwd = os.getcwd()

# Reset the run directory
if os.path.isdir('run'):
    shutil.rmtree('run')
os.mkdir('run')

# Define parameter space
params = {
    'DoS_0':{'type':'float', 'min':0, 'max':0.99, 'default':0},
    'DoS_1':{'type':'float', 'min':0, 'max':0.99, 'default':0},
    'DoS_2':{'type':'float', 'min':0, 'max':0.99, 'default':0},
    'DoS_3':{'type':'float', 'min':0, 'max':0.99, 'default':0},
    'DoS_4':{'type':'float', 'min':0, 'max':0.99, 'default':0}
}

# Set distributions
vary = {
    'DoS_0': cp.Normal(0.6, 0.1)
}

# Create an encoder
copy_encoder = uq.encoders.CopyEncoder(
    'template_input.xml',
    'template_input.xml'
)
generic_encoder = uq.encoders.GenericEncoder(
    template_fname="template_job.py",
    delimiter="$",
    target_filename="simulationModel.py"
)
encoder = uq.encoders.MultiEncoder(copy_encoder, generic_encoder)

# Create a decoder
decoder = uq.decoders.SimpleCSV(
    target_filename='riskFactors.csv',
    output_columns=['ECAP', 'RRT']
)

# Define simulation model
command = 'python simulationModel.py'

# Define actions
actions = Actions(CreateRunDirectory(root=os.path.join(cwd, 'run'), flatten=True),
                  Encode(encoder),
                  ExecuteLocal(command, stdout='stdout.log', stderr='stderr.log'),
                  Decode(decoder))

# Set campaign
campaign = uq.Campaign(name='UQ_DegreeOfStenosis', \
    db_location='sqlite:///' + os.path.join(cwd, 'run/campaign.db'), \
    work_dir=os.path.join(cwd, 'run'), params=params, actions=actions)
campaign.set_sampler(uq.sampling.PCESampler(vary=vary, polynomial_order=3, regression=True))
campaign.draw_samples(mark_invalid=True)
print('Number of samples = %d' %(campaign.get_active_sampler().n_samples))

# Execute campaign
print('Starting campaign...')
try:
    from easyvvuq.actions import QCGPJPool
    from easyvvuq.actions.execute_qcgpj import EasyVVUQParallelTemplate
    from qcg.pilotjob.executor_api.qcgpj_executor import QCGPJExecutor
    with QCGPJPool(
            qcgpj_executor=QCGPJExecutor(
                #resources='128,128', # local mode
                reserve_core=False,
                log_level='debug'
            ),
            template=EasyVVUQParallelTemplate(),
            template_params={
                'numCores':3, # per node
                'numNodes':1, # default is 1
                'venv':'/mnt/lustre/a2fs-work3/work/d137/d137/sharplo3/venv'
            }
        ) as qcgpj:
        campaign.execute(pool=qcgpj).collate(progress_bar=True)

except Exception as inst:
    print(inst)
print('Finished campaign.')
