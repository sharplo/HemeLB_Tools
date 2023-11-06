# HemeLB_Tools
This repository contains preprocessing and postprocessing tools for simulations using [HemeLB](https://github.com/hemelb-codes).

`MyModules` contains the main tools. They are inteneded to be invoked by other scripts.

`submodules` contains the link to [hemeXtract](https://github.com/UCL-CCS/hemeXtract/tree/c6d78874a724f3ee28888cb7fa3b86a3f6b21ee1) which is used to translate the binary output of HemeLB to human-readable output.

The scripts in the root directory are intended to be used directly.
- `analysis.py` is used for parametry analysis of the two-element Windkessel model only
- `paraviewPreprocess.sh` is used to translate the binary output of HemeLB to human-readable output and divide the results according to the time steps
- `verification.py` is used to verify and analyse the simulation results in general
- `writeInput.py` is used to generate an array of input files of HemeLB

# Supplementary Code
`UQ_campaigns/UQAAA` contains supplementary code of the paper titled "Uncertainty Quantification of the Impact of Peripheral Arterial Disease on Abdominal Aortic Aneurysms in Blood Flow Simulations" by Sharp C. Y. Lo, Jon W. S. McCullough, Xiao Xue, and Peter V. Coveney (2023). The corresponding author is Prof. Peter V. Coveney (p.v.coveney@ucl.ac.uk).

In this directory,
- `runCampaign.py` and `restartCampaign.py` are used to perform the campaigns of uncertainty quantification in the study.
- `analyseCampaign.ipynb` is used to analyse the results of the campaigns and produce the figures in the main text of the paper.
- `template_model.py` is the simulation model of the campaigns. It uses [HemePure](https://github.com/UCL-CCS/HemePure) to perform the blood flow simulations and the scripts in `MyModules` in the parent directory (see above) for preprocessing and postprocessing.
- `supplement/BoundaryVelocityRatio.py` is used to plot the boundary velocity ratio against percentage wall extension for different sets of Womersely number and vessel radii, i.e. Figure S1 in the paper.
- `supplement/INLET0_VELOCITY_mean.txt` is the time series of the mean profile of the flow velocity at the centre of the inlet, i.e. Figure 2 in the paper. It is produced by using `writeInput.py` in the parent directory (see above) with `template_input.xml` as the first argument.
