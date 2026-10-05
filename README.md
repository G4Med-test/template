# G4Med Test Template

This is the **Template Repository** for creating new Geant4 validation tests within the `G4Med-test`.

It comes pre-configured with:
* **Automatic CI/CD:** GitHub Actions to build and test your code.
* **Apptainer Integration:** Automatically builds a `.sif` container and pushes it to the GitHub Container Registry (GHCR).
* **Dynamic CMake:** Automatically adapts the project and executable name based on the repository name.
* **Validation export:** Runs the validation macros on the Padova runners and exports
  [Geant Validation Portal](https://github.com/G4Med-test/ci-workflows) JSON.

---

## 🚀 Quick Start: How to Create a New Test

### 1. Create the Repository
1.  Click the **[Use this template](https://github.com/G4Med-test/template/generate)** button at the top of this page.
2.  Select **Create a new repository**.
3.  **Owner:** Select `G4Med-test`.
4.  **Repository Name:** Choose a name (e.g., `HadronTest`, `ElectronScattering`).
    * *Note:* The name you choose here will automatically become the name of your executable and your container (e.g., `HadronTest.sif`).
5.  Click **Create repository**.

### 2. Fill in the repository

| Path | What to do |
| --- | --- |
| `main.cc`, `src/`, `include/` | Your Geant4 application. |
| `macro/unit.mac` | One-event smoke test, run on every push (this name is fixed). |
| `macro/*.mac` | Your validation macros, **with any name**. `example.mac` is only an example. |
| `validation/config.json` | Which of your macros are validation runs, e.g. `{"macros": ["proton_100MeV.mac", "carbon/c12_400MeV.mac"]}` (paths relative to `macro/`). |
| `validation/parser.py` | Reads the results of one run and turns them into portal plots: replace the `TODO`s. |

Don't forget to update this `README.md`.

`Apptainer.def` builds on `ghcr.io/g4med-test/geant4-alma9:<Geant4 tag>` (Geant4,
compilers, Python with NumPy/uproot, datasets mounted at `/g4data`) and normally
needs no changes.

### 3. How validation runs

You write the macros; nothing is generated from templates. `config.json` only says
which macros to run, and `parser.py` only *reads*: it never creates or modifies
macros or input files. For **each** macro listed in `config.json` the pipeline
starts a separate job that:

1. **reads the macro** and calls `metadata(commands)` in your parser, where
   `commands` is the macro as `[(command, value), ...]`. You return a dict
   describing the run, e.g. physics list, particle, energy, event count, names of
   the output files (`TEST` is required). This is the only place where settings
   are found: they are not repeated in `config.json`;
2. **runs the macro unchanged** in the container, inside an empty directory that is
   also the working directory. Files written with relative names (or under
   `/outputs/`) end up there, and stdout is saved as `test_stdout.txt`;
3. **calls `parse(job)`** in your parser. `job` is the dict from step 1 plus `path`
   (that directory) and `VERSION` (the Geant4 version of the image). You read your
   result files from `path` and yield one record per plot with `getJSON`;
4. checks the records (array lengths, no NaN/Infinity) and uploads them; a final
   job merges all macros into the `validation-json` artifact.

```text
config.json ─► proton_100MeV.mac ─┬─ metadata(commands) ─► job ─────────────────┐
                                  └─ Geant4 run ─► result.txt, test_stdout.txt ─┴─ parse(job) ─► plots JSON
```

Because the macro runs as written, it must be self-contained (no
`/control/execute`, loops or aliases). The helpers `getJSON`, `one_command`,
`single_run` and `energy_mev` come from
[`ci-workflows/validation/geantval.py`](https://github.com/G4Med-test/ci-workflows/blob/main/validation/geantval.py).

### 4. Geant4 versions and integration

Pushes build with the Geant4 version set by `TAG` in `Apptainer.def`. To run the
whole pipeline with another published version of
[`geant4-alma9`](https://github.com/G4Med-test/geant4-alma9), use *Actions → CI
Pipeline → Run workflow* with `geant4_tag`, or:

```bash
gh workflow run ci.yml -R G4Med-test/MyTest -f geant4_tag=v11.4.3
```

When the test is ready, add it to
[`ci-workflows/tests.json`](https://github.com/G4Med-test/ci-workflows/blob/main/tests.json)
with a pull request: ci-workflows then checks it on every change, and it is run
automatically with every new Geant4 version.

### 5. Run everything locally

You can test and run everything locally. To do so, You need [Apptainer](https://apptainer.org/docs/user/latest/quick_start.html)
≥ 1.5  and Python ≥ 3.9.
Work in a directory containing your repository and a checkout of `ci-workflows`; the commands below use
`MyTest` as the repository name:

```bash
git clone https://github.com/G4Med-test/MyTest.git
git clone https://github.com/G4Med-test/ci-workflows.git
```

**Get the container**, in one of two ways:

- download the image built by the CI. It is tagged with the full commit SHA (plus
  `-<geant4 tag>` for runs with a different Geant4 version, see below) and the
  package name is the lowercase repository name. 

  ```bash
  apptainer pull MyTest.sif oras://ghcr.io/g4med-test/mytest:<commit-sha>
  ```

- or build it from your working copy. `PROJECT_NAME` must be the repository name
  (it names the executable); `TAG` selects the Geant4 version of the base image.
  Depending on your installation you may need `--fakeroot` or `sudo`:

  ```bash
  apptainer build --build-arg PROJECT_NAME=MyTest --build-arg TAG=v11.3.2 \
    MyTest.sif MyTest/Apptainer.def
  ```

**Geant4 datasets** are not in the image and are mounted at `/g4data`. Use CVMFS if
available, otherwise download them once (about 2 GB) with the image itself:

```bash
G4DATA=/cvmfs/geant4.cern.ch/share/data          # or:
G4DATA=$PWD/g4data; mkdir -p "$G4DATA"
apptainer exec -B "$G4DATA:/g4data" MyTest.sif geant4-config --install-datasets
```

**Run the simulation.** The unit macro, as on every push:

```bash
apptainer run -B "$G4DATA:/g4data:ro" MyTest.sif MyTest/macro/unit.mac
```

A validation macro, exactly as the CI does: in a new, empty directory bound at
`/outputs` and used as working directory, with stdout saved for the parser:

```bash
mkdir run-dir
apptainer run -B "$G4DATA:/g4data:ro" -B "$PWD/run-dir:/outputs" --pwd /outputs \
  MyTest.sif "$PWD/MyTest/macro/example.mac" > run-dir/test_stdout.txt
```

**Check and export.** `matrix` checks `config.json` and runs `metadata()` on every
listed macro, without simulating; it needs only Python. `export` runs `parse()` on
the outputs of one macro inside the image (for uproot) and writes the portal JSON to
`--output`, which must not exist yet: `results.json`, one `plots/<md5>.json` per plot
and `job.json` with what the parser received. The Geant4 version is read from the
image with `geant4-config --version`:

```bash
python3 ci-workflows/validation/export.py matrix --repo MyTest
apptainer exec MyTest.sif python3 ci-workflows/validation/export.py export \
  --repo MyTest --macro example.mac --input run-dir --output json
```
