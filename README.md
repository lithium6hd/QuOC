# QuOC implementation to experiment control

This repository contains a web server that runs the [Quantum Optimal Control Suite (QuOCS)](https://github.com/Quantum-OCS/QuOCS) and makes it accessible to LabView through a network connection.

## Usage

 - To run the optimizer, specify the LabView parameters to optimize and the optimizer settings in the `parameter_search_settings.json` file.
 - Set the type of Figure of Merit you want to optimize in the `optimize.py` file.
 - Start the server by executing the `optimize.py` file.
