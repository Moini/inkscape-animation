# inkscape-animation
Inkscape extension to automate animation work.
Please, refer to 'howto' files ( PDFs ) for help.

Installation:
copy all files into you Inkscape extension folder ( .config/inkscape/extensions for Linux ).

Known Issue:
- Animation names may not contain any underscores. Could be solved by either auto-replacing, not allowing to create an animation with such a name, or by fixing the code to not split on all, but only on the last underscore.
- Gif animations are rather large, could be made smaller using gifsicle (as an optional dependency)

