# BLENDER NSBMD
## FOR BLENDER 4.1
Tool for exporting Nintendo DS .nsbmd model files from blender.

Before exporting, enter the "shading" tab in blender and set up NSBMD nodes for materials. A default set up will be provided using the materials texture if you click add->NSBMD->Setup Nodes. A material *must* have a texture, or export will fail.

You also have to assign a .nsbtx file to the model using the NSBMD tab in the side panel in blender's 3D view which you can open with the n key on your keyboard. The names of the textures inside the nsbtx should match the texture names in blender.

## KNOWN ISSUES
Position UV transforms are untested, use at your own peril

Billboarding is not yet implemented; the option in the material nodes will not have any effect on exported files
Not an issue, but an individual vertex only supports up to 4 weights applied to it. Any more will be removed on export.

## FUTURE PLANS
.nsbca animation exporting

## CREDITS
Yacker - primary conversion work and some reverse engineering
Arg - primary blender interface work
Apicula - useful reference
Gbatek - useful reference
