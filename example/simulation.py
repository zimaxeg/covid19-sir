#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path
import numpy as np
import pandas as pd
from covsirphy import ODESimulator, Estimator, SIRF, line_plot


def main():
    # Create output directory in example directory
    code_path = Path(__file__)
    output_dir = code_path.with_name("output").joinpath(code_path.stem)
    output_dir.mkdir(exist_ok=True, parents=True)
    # Simulation
    eg_population = 1_000_000
    eg_tau = 1440
    setted_param_dict = {
        "theta": 0.002, "kappa": 0.005, "rho": 0.2, "sigma": 0.075
    }
    simulator = ODESimulator(country="Example", province="Example-1")
    simulator.add(
        model=SIRF, step_n=180, population=eg_population,
        param_dict=setted_param_dict,
        y0_dict={"x": 0.999, "y": 0.001, "z": 0, "w": 0}
    )
    simulator.run()
    # Non-dimensional
    nondim_df = simulator.non_dim()
    nondim_df.to_csv(output_dir.joinpath("non_dim.csv"), index=False)
    # Dimensional
    dim_df = simulator.dim(tau=eg_tau, start_date="22Jan2020")
    dim_df.to_csv(output_dir.joinpath("dim.csv"), index=False)
    line_plot(
        dim_df.set_index("Date")[["Infected", "Recovered", "Fatal"]],
        title="Example data",
        filename=output_dir.joinpath("dim.png")
    )
    # Hyperparameter estimation of example data
    estimator = Estimator(
        clean_df=dim_df, model=SIRF, population=eg_population,
        country="Example", province="Example-1", tau=eg_tau
    )
    estimator.run()
    estimated_df = estimator.summary(name="SIR-F")
    estimated_df.loc["Setted"] = pd.Series(
        {**setted_param_dict, "tau": eg_tau}
    )
    estimated_df["tau"] = estimated_df["tau"].astype(np.int64)
    estimated_df.to_csv(
        output_dir.joinpath("estimate_parameter.csv"), index=True
    )
    # Show the history of optimization
    estimator.history(filename=output_dir.joinpath("estimate_history.png"))
    # Show the accuracy as a figure
    estimator.accuracy(filename=output_dir.joinpath("estimate_accuracy.png"))


if __name__ == "__main__":
    main()
