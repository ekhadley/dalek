## Dalek: the DRG Jetty Boot Bot!
Do you love cheating? Want to impress your friends? Well so do I! A recent update for the critically
acclaimed Deep Rock Galactic added Jetty Boot: a flappy-like which tracks high scores. Perfect for showing
off! But if you are, like me, somebody who needed a little help putting their money where their mouth is,
This is the tool for you.  
[WARNING: This is not meant to be an easy to use tool. It is a hacky weeekend project that just barely works. If you
try to actually use it, you will find yourself playing with dozens of parameters, color values and pixel settings
I did not bother to document or systematically tune. You have been warned.]

### The Script
This script uses python3. The screen is grabbed with dxcam and CV2 is used to detect the player's
(boot's) position in the playing area, based on just the image, along with all wall locations and dimensions.  
The organization of the code is simple, it doesn't take much to understand. the reader class is responsible for
getting screen images and raw object positions. A game class instance has a reader from which it gets this raw
data. The reader is prone to hallucination so improbable wall positions are discarded and only good positions are
taken to get accurate walls. Extra information is extrapolated about the boot, most importantly its velocity.  

The game playing rule is as simple as it gets: if you are below the next wall's bottom barrier: jump. The
specifics are tedious but no new concepts are used. We account for  the current velocity to jump earlier.
We also obviously give ourself some padding: we dont want to hit the bottom before we jump, we want to stay
above it. We always select the same shortest jump, and rely on steday and reliable taps to maintain an altitude.
The whole detection->refining->planning->controlling pipeline is littered with magic numbers which just work in
my testing. If you choose to try and actually use this, you'll likely have to adapt them based on your resolution/
aspect ratio/color settings.

### Performance
But who really cares about how this crappy code is hacked together? What you want to know is how many points
you can get. The answer is, easily triple digits, and the thousands are within reach. With my current parameter
settings I don't score below 400. Running it a few times and getting lucky gets me a top score of 640. The two
main causes of failure are failure in the wall detection, where it recognizes both the correct one and an
imaginary one, cause it to half of the time aim for the imaginary one and just die. The second is stutters:
having high frames (and particularly, consistent framerates, becuase some parameters are best chosen based on
the framerate) is important. Stutters occasionally cause the program to just not send a jump until it's too late.
Improving framerate (optimization), increasing frame stability (threading?) and some tweaks to the wall detection
pipeline could put you well into the thousands on every attempt if you have the time (not just to change the code;
this thing takes so long to test once you're getting into triple digit scores every time). 
