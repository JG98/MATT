# MATT - A FRAMEWORK FOR MODIFYING AND TESTING TOPOLOGIES

[![PyPI version](https://badge.fury.io/py/phylo-matt.svg)](https://pypi.org/project/phylo-matt/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![Github Build](https://github.com/BIONF/MATT/workflows/build/badge.svg)

![MATT](https://raw.githubusercontent.com/BIONF/MATT/master/matt/static/logo.png)

# Table of Contents
* [Installation](#installation)
* [Usage](#usage)
* [Contribution](#contribution)
* [License](#license)
* [Citation](#citation)
* [Contact](contact)

# Installation
*MATT* is distributed as a python package called *phylo-matt*. *MATT* requires a
[Python](https://www.python.org/downloads/) version of 3.8 or higher.

Once python and the included package manager are installed, *MATT* can be installed using the `pip` command in a
console:
```
pip install phylo-matt
```
If you run into errors, try:
```
pip install phylo-matt --user
```

# Usage
## Launch
After *MATT* has been installed it can be launched using the `matt` command in a console:
```
matt
```

This will start *MATT* and open `http://localhost:5000` in the preferred browser.

Once open *MATT* can be used via the GUI in the browser.

To close *MATT* after usage, simply kill the server by hitting <kbd>Ctrl</kbd> + <kbd>C</kbd> in the console.

## Import
Make sure to set all the needed options under the "Options" button in the top right corner first.
You will also find a reference to this file there.

Afterwards optionally set a session name and import your alignment and/or tree file.
Alternatively you can import the example files.
- If you do not name the session, default file names will be used and might override older files.
- If you only import an alignment file, you can let *MATT* generate the tree for you.
- If you only import a tree file, you will not be able to use all of *MATT's* features.

## Navigation

After the tree has been drawn, you can navigate through it:
- To zoom in, use either <kbd>ScrollUp</kbd> on your input device,
the "Zoom in" button in the top left corner
or the "Zoom in" in the context menu (<kbd>RightClick</kbd>).
- To zoom out, use either <kbd>ScrollDown</kbd> on your input device,
the "Zoom out" button in the top left corner
or the "Zoom out" in the context menu (<kbd>RightClick</kbd>).
- <kbd>Click & Drag</kbd> to move the tree around.

The minimap in the top right corner shows you the tree and the viewport.
<kbd>Click</kbd> somewhere inside to jump to that location.

To search for a specific entry, enter the name in the search in the top left corner and hit <kbd>Enter</kbd>
or <kbd>Click</kbd> the button next to the input field.

Use the buttons "Show/Hide branch lengths" and "Align/Attach labels" in the top right corner
or their versions in the context menu to toggle between the viewmodes for branch lenghts and labels.

## Changing topologies
<kbd>Click</kbd> on a branch to select it. After you have selected a branch you can swap it with another branch,
by <kbd>Clicking</kbd> that other branch.

After selecting a branch, the "Set Root" button appears. <kbd>Click</kbd> it to set the selected branch as a root.
Alternatively you can <kbd>Rightclick</kbd> a branch to select it and set the root directly in the context menu.

Once you have changed the initial topology, you can "Undo" and "Redo" your changes,
using the buttons in the top left corner or the context menu.

## Saving and testing topologies
If you want to save a topology, <kbd>Click</kbd> the "Save snapshot" button or the option in the context menu.
Optionally you can name the snapshot and then save it.

Once a snapshot is saved, you can find it under the "Snapshots" button or in the context menu.
In the snapshots menu you can jump to another snapshot directly, change its name or download it.
Here you can also select multiple snapshots and test them.
After the tests have run, a menu opens up, showing you the test results of the topology tests.

# Contribution
Any bug reports, comments and suggestions are highly appreciated. Please
[open an issue on GitHub](https://github.com/BIONF/MATT/issues/new) or contact us via [email](mailto:jeffgower98@gmail.com).

# License
*MATT* is licensed under the [GNU General Public License v3.0](https://github.com/BIONF/MATT/blob/mater/LICENSE).

# Citation
An Application Note is in the works. Stay tuned.

# Contact
For further support or bug reports please contact us via [email](mailto:jeffgower98@gmail.com).
