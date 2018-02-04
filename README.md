### Simple little roleplaying game (Hack'n Slash)

This is a simple little game where I wanted to recreate an old school RPG game I had fun playing on C64 called "Halls of Death" (made in Commodore Basic) by Stewart Sargaison.

You run the game by running (python 3.6 is required):

`python3.6 rpg.py`

You have to have my utility [rwutility.py](https://github.com/westerlin/rwutility) installed to play.

You walk from room to room (currently all the same) arranged and connected as a 10x10 maze. You meet orcs underway - and get their treasures when you kill them - but unfortunately you cannot exit the dungeon to buy new equipment or healing potions (and you wont find any in the dungeon yet) - so at some point you will die rich in the darkness - at the claws of yet another an Orc. Game has no memory - so Orcs revive etc.

Some feature I like personally is the scrolling messages in the console, which I think mimics the feel of old school storytelling.

Obviously, a lot more needs to be added and the code is rather clutty as interface, game and gameobjects are one big mesh.

I am using a simple Recursive Backtracking algorithm for maze generation which I found on [here](http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking). Thanks to Jamis Buck for sharing all these wierd maze algorithms at his website and explaining in details how they work. You can find my python implementation of maze object with autogenerating recursive backtracking algorithm in the module __labyrinth.py__ and implement in you own applications.

I have also included __dungeon.py__ which is basically my attempt on a python implementation of DonJon's dungeon generation algoritm (originally coded in [perl](https://donjon.bin.sh/code/dungeon/dungeon.pl). Thanks to DonJon for sharing this. If you are RPG interested I would recommend to visit DonJon's great [website](https://donjon.bin.sh/) hosting a lot of cool generators for adventures etc. Please note, that DonJon's algoritm (as far as I understand) may end up generate "islands" - that is unconnected sets of connected rooms and corridors. So basically the dungeon is not complete in the sense that you are guaranteed that you reach any point in the dungeon from any other point.  
