# inkscape-animation
Inkscape extension to automate animation work.
Please, refer to 'howto' files ( PDFs ) for help.

Installation:
copy all files into you Inkscape extension folder ( .config/inkscape/extensions for Linux ).

Known Issue:
- Animation names may not contain any underscores. Could be solved by either auto-replacing, not allowing to create an animation with such a name, or by fixing the code to not split on all, but only on the last underscore.
- Gif animations are rather large, could be made smaller using gifsicle (as an optional dependency)

Original author is github user ray-hplus, whose account seems to have been deactivated by end of June / start of July 2016.
In a comment on a question about licencing, ray-hplus answered that the licence of the extension is the same as Inkscape's, which is currently GPLv2. Unfortunately, that comment was lost due to the account inactivation, and a licence file has never been added.
