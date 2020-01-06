PlayStation All-Stars Battle Royale (PS Vita) - Noesis Plugin
=======
This is a plugin for Noesis created to handle the models from PSASBR (PS Vita). The importer is ready for displaying models and textures. The exporter is still a WiP.
This is a NEW version that takes the work of the old PSASBR script and improves/fixes it. It can open ALL THE MODELS. Keep reading for more details.

How to use
============
In order to use this you need [Noesis by Rich Whitehouse](https://richwhitehouse.com/index.php?content=inc_projects.php&showproject=91). After that, just copy the script file in the folder in this path: YourNoesisFolder/plugins/python
Open Noesis and the script will be automatically loaded, allowing you to open PSASBR assets using Noesis.

Assets that you can open:

* CMDL and CSKN models. All of them.

* CTXR textures. However, not all of them are supported. Normal maps, UI and generally small textures won't be displayed correctly. 
	* If you want to extract textures from the game please refer to the [PSASBR Tool](https://github.com/Cri4Key/PSASBR-Tool) instead, which supports all the formats. The reason why this script has texture support is due to the code from the old script for handling textures which I decided to not delete.
	
The script also adds the PSASBR model format as a format you can convert your models into so to allow game modding, but avoid doing that as the part of the script which handles this (exporter) is still a work in progress and will output broken models that won't work.

Improvements and fixes from the chrrox script
=====
-- Models --

* Added support for normal and tangent vertex
* Added support for vertex color
* Added support for emissive materials
* Added support for normal, specular, emissive and opacity textures
* Fixed "Tried to set offset beyond buffer size.", the most frequent error preventing the vast majority of the models from being displayed or extracted
* Fixed "KeyError: 3", thrown by unhandled vertex data for a modest amount of models
* Fixed another couple of errors thrown by few models, dealing with texture naming and more unhandled data

Acknowledgements
================
* __The improvements and fixes brought to this new version should let you open ALL THE MODELS from the game, with no exception. If for some reason you find some model not working, please open an issue or contact me.__
* Original old script written by chrrox. Without his original work, I wouldn't have something to work on right now.
* Special thanks to the XeNTaX discord community for their help with some importer stuff and the exporter so far.
