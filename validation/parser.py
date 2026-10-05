"""Turns the output of one validation run into plots for the Geant Validation Portal.

The CI imports this file and calls two functions, once for every macro listed in
validation/config.json:

1. metadata(commands)  BEFORE the simulation: describe the run from its macro.
2. parse(job)          AFTER the simulation: read the output files, return plots.

You only have to edit the lines marked TODO. Example with macro/example.mac:

    commands = [("/myapp/phys/addPhysics", "FTFP_BERT"), ("/run/initialize", ""),
                ("/gun/particle", "proton"), ("/gun/energy", "100 MeV"), ...]

    metadata(commands) -> {"TEST": "MyTest", "PHYSICS_LIST": "FTFP_BERT",
                           "PARTICLE": "proton", "ENERGY": 100.0}

    job = that dict + {"path": "<directory of the run>", "VERSION": "11.3.2"}
    parse(job) -> one plot per `yield`

The run directory contains the files your application wrote with relative names
(here result.txt) and the captured standard output (test_stdout.txt).

Helpers from ci-workflows/validation/geantval.py:
- one_command(commands, "/cmd"): value of a command that appears exactly once
  (error if missing or repeated, so the metadata always matches the macro);
- energy_mev("100 MeV"): energy in MeV;
- getJSON(job, ...): builds one plot in the portal format (see parse below).
"""
from pathlib import Path

from geantval import energy_mev, getJSON, one_command


def metadata(commands):
    """Describe one run, reading every setting from its macro.

    The returned dict must contain "TEST" (the test name shown on the portal);
    add whatever parse() needs. Raise an error if the macro is not suitable.
    """
    return {
        "TEST": "MyTest",  # TODO: your test name
        "PHYSICS_LIST": one_command(commands, "/myapp/phys/addPhysics"),  # TODO: your command
        "PARTICLE": one_command(commands, "/gun/particle"),
        "ENERGY": energy_mev(one_command(commands, "/gun/energy")),
    }


def parse(job):
    """Read the output of the run in job["path"] and yield one plot per `yield`."""
    # TODO: read your output file. This example expects two columns, x and y,
    # one point per line; lines starting with # are comments.
    x, y = [], []
    for line in (Path(job["path"]) / "result.txt").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            x_value, y_value = line.split()
            x.append(float(x_value))
            y.append(float(y_value))

    # "chart" is a set of points (x, y). For a histogram use "histogram" with
    # binEdgeLow, binEdgeHigh and binContent instead of xValues and yValues.
    # Optional uncertainties: yStatErrorsPlus/Minus, ySysErrorsPlus/Minus.
    yield getJSON(
        job, "chart",
        mctool_name="GEANT4",
        mctool_model=job["PHYSICS_LIST"],
        observableName="TODO observable",  # e.g. "attenuation coefficient"
        targetName="TODO target",          # e.g. "water"
        beamParticle=job["PARTICLE"],
        beamEnergies=[job["ENERGY"]],      # MeV
        title="TODO title",
        xAxisName="TODO x, unit",
        yAxisName="TODO y, unit",
        xValues=x,
        yValues=y,
    )
