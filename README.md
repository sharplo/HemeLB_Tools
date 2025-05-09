# HemeLB_Tools
This repository provides preprocessing and postprocessing tools for simulations conducted with [HemeLB](https://github.com/hemelb-codes).

`MyModules` contains the core Python modules, designed to be imported and used by other scripts.

`submodules` includes a reference to [hemeXtract](https://github.com/UCL-CCS/hemeXtract/tree/c6d78874a724f3ee28888cb7fa3b86a3f6b21ee1), a utility for converting the binary output of HemeLB into human-readable text.

To output values in double precision, modify line 57 of the `print` function in `Snapshot.h` as follows:

`fprintf(outfile, "%.15e", records[index]);`

# Scripts for Verifying the Yang Pressure Boundary Condition
This repository includes scripts used to verify the pressure boundary condition proposed by [Yang 2010](https://doi.org/10.1016/j.camwa.2009.08.074), which is implemented in [HemePure](https://github.com/UCL-CCS/HemePure) (commit: ad16f548817c939e9a9e9412a6dd715309161e46) --- a modified version of HemeLB with improvements in memory efficiency, compilation time, and parallel scaling.
- `writeInput.py` generates the HemeLB input configuration file for each simulation case.
- `postprocess_essential.sh` translates the binary output of HemeLB into human-readable .txt files using `hemeXtract`.
- `postprocess_full.sh` extends `postprocess_essential.sh` by additionally separating output by time step for visualisation in ParaView.
- `verification.py` performs quantitative analysis of the simulation results, generating visualisations, plots, and tables reporting the global error norms of the simulation error.
