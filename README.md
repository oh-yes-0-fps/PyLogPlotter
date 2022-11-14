# PyLogPlotter
A tool to turn a .wpilog file into a series of html based graphs</br>
You can cofigure its behavior using the gui, you will have to run 1 log from the robot through first for the availibale configurtions to populate

## How to use
The program takes arguments
positional arguments:
  filename              The file to plot

options:
  -h, --help            show this help message and exit
  -p, --plot            The file to plot, needs -c aswell
  -g, --gui             Run the config helper gui, needs -c aswell
  -c CONFIG, --config   The json in resources to config the plots with
  -d DUMP, --dump DUMP  A preliminary dump of the log file for data to use in gui, feed in name of robot

example:
    () = optional
    [] = required
    PyPlotter.py filename.wpiLog \[-p|-g|-d robotname\] \[-c config.json\]

working one with given example files:
    PyPlotter.py FRC_20221022_150128_NYROC_Q17.wpilog -p -c plot_config_cruisee.json
