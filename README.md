# Walter P. Reuther Library Digitization Client

This repository contains a Python GUI client to assist the Walter P. Reuther Library in its preservation digitization efforts. The GUI wraps functionality provided by the `reuther_digitization_utils` Python scripts in a desktop user interface and also adds support for tracking project status in a database.

## Requirements
- Python 3
- `reuther_digitization_utils` and its dependencies
- PyQt5

## Installation
- Ensure that the above requirements are installed
- `git clone` this repository
- `cd reuther_digitization_client`
- `pip install -r requirements.txt`

## Configuration

Make a copy of the configuration file at `reuther_digitization_client/conf/config.cfg.example` and name it `config.cfg`. Edit the `output_dir` and `scan_storage_location` to configure default filepaths for the application's output directory and remote storage locations.

## Use

Launch the application from the repository's root directory with: `python launcher.py`

The digitization client consists of two primary windows: Projects and Items.

### Projects

The application loads to the Projects window. The first time the application is loaded, this window will be empty. Click the `Add Projects` button to import a new digitization project. This requires a project CSV and a path to an output directory (see `reuther_digitization_utils` for further information).

If there are existing projects, they will be listed in a table view consisting of the project name, project directory, total number of items within the project, total number of completed items, and total number of scans associated with the project. Click the `Load Project` button next to each project to open the Items window for that project.

### Items

The Items window lists all items associated with a given project in a table view, displaying some basic metadata and a series of task buttons for each item. The tasks are configured in sequential order as follows:

- Rename: Renames scanned images in the item's `preservation` directory according to the Reuther's filenaming conventions
- Generate Derivatives: Generate derivative images and a PDF
- Copy to HOLD: Copies the item directory to the Reuther's remote storage location
- Complete: Marks the item's status as complete in the project database
