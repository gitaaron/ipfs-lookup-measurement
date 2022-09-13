# DHT Lookup Measurement Data

The analysis folder contains log files of an IPFS DHT lookup measurement and code to parse and analyse them.

## Running

### Prerequisites

Install [`poetry`](https://python-poetry.org/) for python dependency management and then install the dependencies:

```shell
poetry install
```

Then start a poetry shell to have all the dependencies available:

```shell
poetry shell
```

### Parsing

We recommend parsing the log files and saving a concise version of the information next to the log files. To do that run:

```shell
python3 log_parse.py
```

This command will take each log file in the `2022-01-16` directory, parse it and create a new file next to it called `<LOG_FILE_NAME>.p` (suffix `.p`). This file can be loaded later on way quicker.

### Analysis

The file `plot_retrievals.py` shows an example of how the files are loaded and analysed:

```shell
python3 plot_retrievals.py
```
