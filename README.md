# HemeLB_Tools
This repository contains preprocessing and postprocessing tools for simulations using [HemeLB](https://github.com/hemelb-codes).

`MyModules` contains the main tools. They are inteneded to be invoked by other scripts.

`submodules` contains the link to [hemeXtract](https://github.com/UCL-CCS/hemeXtract/tree/c6d78874a724f3ee28888cb7fa3b86a3f6b21ee1) which is used to translate the binary output of HemeLB to human-readable output.

The scripts in the root directory are intended to be used directly.
- `analysis.py` is used for parametry analysis of the two-element Windkessel model only
- `paraviewPreprocess.sh` is used to translate the binary output of HemeLB to human-readable output and divide the results according to the time steps
- `verification.py` is used to verify and analyse the simulation results in general
- `writeInput.py` is used to generate an array of input files of HemeLB
