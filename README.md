This is a script for batch rendering some ranges of frames in Blender with different settings. It allows setting up multiple ranges (start,end) which Blender will render in sequence. It is useful if you have a situation where you need, for example, frames 1-10 and 30-50 rendered, and rendering takes a very long time. You would otherwise have to return later to the computer to see if the rendering of the first set was finished so you could manually set Blender to work on the second set.

To use, add the script to blenderdir/2.65/scripts/addons/ and go to user preferences -> addons -> render -> and enable the script, click save default. The plugin is now visible at the bottom of the render panel.

Read more at http://jessekaukonen.blogspot.fi/2013/02/batch-rendering-in-blender.html
Or in the BlenderArtists thread: http://blenderartists.org/forum/showthread.php?281647-Setting-up-batch-render-tasks-(multiple-sequential-renders)
