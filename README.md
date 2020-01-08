PlayStation All-Stars Battle Royale (PS Vita) - Noesis Plugin
=======
This is a plugin for Noesis created to handle the models from PSASBR (PS Vita). The importer is ready for displaying models and textures. The exporter is still a work in progress, as this script will be updated more.
This is a NEW version that takes the work of the old PSASBR script and improves/fixes it. It can open ALL THE MODELS. Keep reading for more details.

How to use
============
In order to use this you need [Noesis by Rich Whitehouse](https://richwhitehouse.com/index.php?content=inc_projects.php&showproject=91). After that, just copy the script file in the folder in this path: YourNoesisFolder/plugins/python
Open Noesis and the script will be automatically loaded, allowing you to open PSASBR assets using Noesis.

Assets that you can open:

* CMDL and CSKN models. All of them.

* CTXR textures. However, not all of them are supported. Normal maps, UI and generally small textures won't be displayed correctly.
	* If you want to extract textures from the game please refer to the [PSASBR Tool](https://github.com/Cri4Key/PSASBR-Tool/releases/latest) instead, which supports all the formats. The reason why this script has texture support is due to the code from the old script for handling textures which I decided to not delete.

__If you want to get more info about the model, open the data viewer in Noesis (Tools -> Data Viewer) to get a look at stuff such as meshes, materials, and the textures for each material. This is useful when you are viewing a model and want to know which textures it uses from the game__

The exporter script is also in development, which will allow modding on the game. More updates will come in the future for this script. Eventually, the script may handle even animations in future.

Improvements and fixes from the old script
=====
-- Models --

* Added support for normal and tangent vertex
* Added support for vertex color
* Added support for emissive materials
* Added support for normal, specular, emissive and opacity textures for the materials
* Added support for CMDL files (static models)
* Fixed "Tried to set offset beyond buffer size.", the most frequent error preventing the vast majority of the models from being displayed or extracted
* Fixed "KeyError: 3", thrown by unhandled vertex data for a modest amount of models
* Fixed another couple of errors thrown by few models, dealing with texture naming and more unhandled data

Known issues
================
* Models such as PaRappa's 3rd costume may appear "broken" for a reason or another, such as holes or weird transparencies where there shouldn't be. This is caused by not setting the right blending options for rendering, but the model is still being loaded correctly: that means you can export it to another format and use it elsewhere as you please and depending your rendering options it will work perfectly. This problem only affects the viewer in Noesis.
	* The problem above also affects the emissive maps, such as in Ratchet's 2nd costume.

* A small number of models (e.g. Kratos, Fat Princess) may have bones not positioned properly. This is a problem that still needs to be figured out. However, despite the positioning issue, such bones are still being aligned correctly to the right parts and will affect the model's movements as intended.

* Sometimes the textures that a model uses from the game may not be matching: the game often uses the same texture with many different lightnings, and by default, a model could have different looking lightnings for the various texture it's using. One example I can think of is Kat's 3rd costume. It's quite normal and in such cases just swap for the same texture with a different lightning to make it look better. Everything you need is available from the game's assets.

* The script supports Diffuse, Normal, Specular, Environment, Opacity and Emission maps. That's enough for the vast majority of the models and their textures. However, some models make use of shaders in-game that drastically change their looks so you may not be able to get the look you are looking for out every single time. Polygon Man and generally boss arena models fall under this category, with the purple look not being a texture but some shader in-game, along using other textures that do not fall under the category of the ones supported by the script. To address this I need to know how the shaders work and that will take time. You will eventually need to apply other textures manually outside Noesis if you want to address this for now. Considering that UVs are all in place, it won't be something difficult to do anyway.

Acknowledgements
================
* __The improvements and fixes brought to this new version should let you open ALL THE MODELS from the game, with no exception. If for some reason you find some model not working, please open an issue or contact me.__
* Original old script written by chrrox. Without his original work, I wouldn't have something to work on right now.
* Special thanks to the XeNTaX discord community for their help with some importer stuff and the exporter so far.
