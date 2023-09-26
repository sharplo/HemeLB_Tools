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
    'Lambda':{'type':'float', 'min':0.0001, 'max':1, 'default':0.25},
    'E':{'type':'float', 'min':0.01, 'max':1e10, 'default':9000000},
    'F':{'type':'float', 'min':0, 'max':1, 'default':0.45},
    'Re':{'type':'float', 'min':1, 'max':778, 'default':600},
    'Wo':{'type':'float', 'min':0.1, 'max':15, 'default':11.2},
    'm':{'type':'float', 'min':0, 'max':10, 'default':2},
    'gamma_R':{'type':'float', 'min':0, 'max':1e10, 'default':2**10},
    'gamma_C':{'type':'float', 'min':0, 'max':1e10, 'default':2**(-2)},
    'shotShift':{'type':'float', 'min':0, 'max':1000, 'default':0}
}

# Set distributions
vary = {
    'Lambda': cp.Reciprocal(0.0036, 0.25),
    'E': cp.Uniform(3320000, 27570000),
    'F': cp.Uniform(0.32, 0.76),
    'Re': cp.Uniform(540, 660),
    'Wo': cp.Uniform(10.1, 12.3),
    'm': cp.Uniform(1, 4),
    'gamma_R': cp.Reciprocal(2**8, 2**12),
    'gamma_C': cp.Reciprocal(2**(-4), 2**0),
    'shotShift': cp.Uniform(0, 20)
}

# Create an encoder
copy_encoder1 = uq.encoders.CopyEncoder(
    'template_input.xml',
    'template_input.xml'
)
copy_encoder2 = uq.encoders.CopyEncoder(
    'INLET0_VELOCITY.txt.weights.txt',
    'INLET0_VELOCITY.txt.weights.txt'
)
copy_encoder3 = uq.encoders.CopyEncoder(
    'ESM_File2_Q_d4.txt',
    'ESM_File2_Q_d4.txt'
)
generic_encoder = uq.encoders.GenericEncoder(
    template_fname="template_model.py",
    delimiter="$",
    target_filename="simulationModel.py"
)
encoder = uq.encoders.MultiEncoder(copy_encoder1, copy_encoder2, copy_encoder3, generic_encoder)

# Define simulation model
numPeriods = 3
outDir = './periods_3/'
command = 'python simulationModel.py ' + str(numPeriods) + ' ' + outDir

# Create a decoder
decoder = uq.decoders.JSONDecoder(
    target_filename = outDir + 'qoi.json',
    output_columns=[
        'Qratios_Desired',
        'Qratios_Measured',
        'Qratios_RelErr',
        'TAWSS',
        'OSI',
        'ECAP',
        'RRT'
    ]
)

# Define actions
actions = Actions(CreateRunDirectory(root=os.path.join(cwd, 'run'), flatten=True),
                  Encode(encoder),
                  ExecuteLocal(command, stdout='stdout.log', stderr='stderr.log'),
                  Decode(decoder))

# Set campaign
campaign = uq.Campaign(name='UQAAA_order2', \
    db_location='sqlite:///' + os.path.join(cwd, 'run/campaign.db'), \
    work_dir=os.path.join(cwd, 'run'), params=params, actions=actions)
campaign.set_sampler(uq.sampling.PCESampler(vary=vary, polynomial_order=2, regression=True))
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
                #log_level='debug',
                #resources='128,128', # local mode
                reserve_core=False
            ),
            template=EasyVVUQParallelTemplate(),
            template_params={
                'numCores':128, # per node
                'numNodes':32, # default is 1
                'venv':'/mnt/lustre/a2fs-work3/work/e769/e769/sharplo4/venv'
            }
        ) as qcgpj:
        campaign.execute(pool=qcgpj).collate(progress_bar=True)

except Exception as inst:
    print(inst)
print('Finished campaign.')
