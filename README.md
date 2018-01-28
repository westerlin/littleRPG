### Simple little roleplaying game (Hack'n Slash)

This is a simple little game where I wanted to try out creating an old style RPG game I had fun playing on C64 called Halls of Death.

You run the game by running:

`python3.6 rpg.py`

You walk from room to room (currently all the same) arranged and connected as a 10x10 maze. You meet orcs underway - and get their treasures when you kill them - but unfortunately you cannot exit the dungeon to buy new equipment or healing potions - so at some point you will die rich in the darkness - at the hands of an Orc, who have drained the last of your health from yet another blow.

I am using a simple Recursive Backtracking algorithm which I found on [here](http://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking). Thanks to Jamis Buck for sharing all these wierd maze algorithms and explaining in details how they work. You can find my python implementation of maze object with autogenerating recursive backtracking algorithm in the module __labyrinth.py__.

I have also included __dungeon.py__ which is basically my attempt on a python implementation of DonJon's dungeon generation algoritm (originally coded in [perl](https://donjon.bin.sh/code/dungeon/dungeon.pl). Thanks to DonJon for sharing this. If you are RPG interested I would recommend to visit DonJon's great [website](https://donjon.bin.sh/) hosting a lot of cool generators for adventures etc.
