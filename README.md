# QuOC implementation to experiment control

This repository contains a web server that runs the [Quantum Optimal Control Suite (QuOCS)](https://github.com/Quantum-OCS/QuOCS) and makes it accessible to LabView through a network connection.

## Usage

 - To run the optimizer, specify the LabView parameters to optimize and the optimizer settings in the `parameter_search_settings.json` file.
 - Set the type of Figure of Merit you want to optimize in the `optimize.py` file.
 - Start the server by executing the `optimize.py` file.


## HQA specific usage

Follow the general instructions on running the optimizer in the [HQA Howto page](https://www-intern.physi.uni-heidelberg.de/Wikis/ultracold_wiki/index.php/How_to_...)

### mloop_mot_hodt_handover

- enable HODT and put release recapture 2 after HODT end.
- In ODT Prep, diable first three analouge channels (9 coil l2 + r1)
- diable VODT and tweezer and all modules after.
- disable evaporation in HODT, ensure sufficient holdtime in HDOT to not recapture atoms from cMOT. (at least 200 ms)#

### mloop_hodt_vodt_handover

- enable HODT, HODT evap and VODT and put release recapture 2 after VODT end.
- diable tweezer and all modules after.
- disable evaporation in VODT, ensure sufficient holdtime in VODT to not recapture atoms from HODT. (at least 200 ms)

### mloop_vodt_tweezer_handover

- enable HODT, HODT evap, VODT, VODT evap and Tweezer and put release recapture 2 after Tweezer end.
- diable tweezer spilling and all modules after.
- disable evaporation in tweezer, ensure sufficient holdtime in tweezer to not recapture atoms from VODT. (at least 200 ms)

