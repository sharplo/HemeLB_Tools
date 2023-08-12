#!/usr/bin/python3.8
import os
import easyvvuq as uq
from easyvvuq.constants import Status

# Get the current working directory
cwd = os.getcwd()

# Reload campaign
campaign = uq.Campaign(name='UQAAA_order2', \
    db_location='sqlite:///' + os.path.join(cwd, 'run/campaign.db'))
sampler = campaign.get_active_sampler()
campaign.set_sampler(sampler, update=True)
campaign.campaign_db.set_run_statuses(
    [str(i+1) for i in range(0, sampler.n_samples)], Status.NEW)

# Execute campaign
print('Restarting campaign...')
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
                'numCores':32, # per node
                'numNodes':1, # default is 1
                'venv':'/mnt/lustre/a2fs-work3/work/e769/e769/sharplo4/venv'
            }
        ) as qcgpj:
        campaign.execute(pool=qcgpj).collate(progress_bar=True)

except Exception as inst:
    print(inst)
print('Finished campaign.')
