# HemeLB_Tools
This repository contains preprocessing and postprocessing tools for the fluid flow simulations using [HemeLB](https://github.com/hemelb-codes).

`MyModules` contains the main tools. They are intended to be invoked by other scripts.

`submodules` contains the link to [hemeXtract](https://github.com/UCL-CCS/hemeXtract/tree/c6d78874a724f3ee28888cb7fa3b86a3f6b21ee1) which is used to translate the binary output of HemeLB to human-readable output.

The scripts in the root directory are intended to be used directly.
- `analysis_WK.py` is used for parametric analysis of the two-element Windkessel model
- `paraviewPreprocess.sh` is used to translate the binary output of HemeLB to human-readable output and divide the results according to the time steps
- `verification.py` is used to verify and analyse the simulation results in general
- `writeInput.py` is used to generate an array of input files of HemeLB
- `plot_profile.py` is used to plot the time series of a variable deposited in a file

# Supplementary Code for "Uncertainty Quantification of the Impact of Peripheral Arterial Disease on Abdominal Aortic Aneurysms in Blood Flow Simulations"
`UQ_campaigns/UQAAA` contains supplementary code of the paper titled "Uncertainty Quantification of the Impact of Peripheral Arterial Disease on Abdominal Aortic Aneurysms in Blood Flow Simulations" by Sharp C. Y. Lo, Jon W. S. McCullough, Xiao Xue, and Peter V. Coveney (2024). The corresponding author is Prof. Peter V. Coveney (p.v.coveney@ucl.ac.uk).

In this directory,
- `runCampaign.py` and `restartCampaign.py` are used to perform the campaigns of uncertainty quantification described in the study;
- `analyseCampaign.ipynb` is used to analyse the results of the campaigns and produce the figures in the main text of the paper;
- `template_model.py` is the simulation model of the campaigns. It outlines the workflow of the preprocessing, execution, and postprocessing of one single simulation using [HemePure](https://github.com/UCL-CCS/HemePure) (git commit hash: 554e8bef2cd68). The scripts in `paraviewPreprocess.sh`, `submodules`, and `MyModules` in the parent directory (see above) are needed for preprocessing and postprocessing of the simulations;
- `supplement/BoundaryVelocityRatio.py` is used to plot the boundary velocity ratio against percentage wall extension for different sets of Womersely numbers and vessel radii, i.e. Figure S1 in the paper;
- `supplement/INLET0_VELOCITY_mean.txt` is the time series of the mean profile of the flow velocity at the centre of the inlet, i.e. Figure 2 in the paper. It is produced using `writeInput.py` in the parent directory (see above) with `template_input.xml` as the first argument;
- `venv.txt` is the list of Python packages installed in the virtual environment when the campaign was performed in the study.
