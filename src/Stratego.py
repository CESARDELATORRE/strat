'''
(CDLTLL) Updated code for Python 3.11
'''

# Standard Python modules
from math import sin, pi
import webbrowser
import os
import pickle
import datetime
from textwrap import fill, dedent, TextWrapper
from random import randint, choice, random
import platform as pf
# (CDLTLL) OLD Python 2.7 import pkgutil
import importlib
import time
import pygame

# Tkinter and PIL for GUI and graphics
from tkinter import *  
from tkinter import messagebox as tkMessageBox
from tkinter import filedialog as tkFileDialog
from PIL import Image, ImageTk

# Modules that are part of the game
from Army import Army, Icons
import explosion
from constants import *

# (CDLTLL)
# from brains import *  

import sys
sys.path.append('..')

from src.brains.Brain import Brain as Brain
from src.brains.CarefulBrain import Brain as CarefulBrain
from src.brains.SmartBrain import Brain as SmartBrain
from src.brains.randomBrain import Brain as randomBrain
from src.brains.SurpriseBrain import Brain as SurpriseBrain

import importlib.util
import os
import pkgutil
import sys

#(CDLTLL) BRAINLIST = [module[1] for module in pkgutil.iter_modules(['brains']) if not module[1] == "Brain"]

brain_modules = [name for _, name, _ in pkgutil.iter_modules(['brains']) if not name == "Brain"]

BRAINLIST = [module_name for module_name in brain_modules]

# (CDLTLL) This is storing the objects, I think we just need the names
# BRAINLIST = []
# for module_name in brain_modules:
#     spec = importlib.util.spec_from_file_location(module_name, os.path.join('brains', module_name + '.py'))
#     module = importlib.util.module_from_spec(spec)
#     spec.loader.exec_module(module)
#     BRAINLIST.append(module)

# (CDLTLL)
print("BRAINLIST",BRAINLIST)

# Some system dependent imports
platform = pf.system()
if not platform in ["Windows", "Linux", "Darwin"]:
    platform = "Other"

# (CDLTLL-DELETE)
py26 = False

# (CDLTLL-DELETE)
# if sys.version_info[:2] == (2, 7):
#     pyVersion = False

print("Python version:", sys.version_info[:2])

from tkinter.ttk import Combobox, Notebook

def setIcon(window, icon):
    """Set the icon of a Tk root or toplevel window to a given .ico or .xbm file, 
    depending on the operating system"""
    # (CDLTLL-CHECK)
    # TODO: Mac
    if not platform == "Linux":
        window.wm_iconbitmap("%s/%s.ico" % (ICON_DIR, icon))
    else:
        window.wm_iconbitmap("@%s/%s.xbm" % (ICON_DIR, icon))

class Application:
    """Main game and UI class"""
    def __init__(self, root, brain="SmartBrain", difficulty="Normal", size="Normal", diagonal=False):
    
        self.root = root

        self.difficulty = difficulty
        self.diagonal = (diagonal == "Yes")
        self.debug = False

        self.boardWidth = SIZE_DICT[size][0]
        self.pools = SIZE_DICT[size][1]
        self.tilePix = SIZE_DICT[size][2]

        self.unitIcons = Icons(self.tilePix)

        # (CDLTLL)
        print('brain:', brain)

        # Create an object of the selected brain class
        # (CDLTLL)
        self.blueBrain = eval(brain)

        #(CDLTLL) Explicit object creation
        # blue_brain_module = importlib.import_module("brains." + brain)
        # self.blueBrain = blue_brain_module.Brain(self, self.blueArmy, difficulty)
        # self.blueBrainName = brain
    
        self.redBrain = 0
        self.redBrainName = "Human"

        # Define the braintypes attribute        
        self.braintypes = {"Blue": self.blueBrain,
                           "Red": self.redBrain}

        # Create menu bar
        menuBar = Menu(root)

        fileMenu = Menu(menuBar, tearoff=0)
        fileMenu.add_command(label="New Game", command=self.confirmNewGame, underline=0, accelerator="Ctrl+N")
        fileMenu.add_command(label="Load Game", command=self.loadGame, underline=0, accelerator="Ctrl+L")
        fileMenu.add_command(label="Save Game", command=self.saveGame, underline=0, accelerator="Ctrl+S")
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.exit, underline=1, accelerator="Esc")
        menuBar.add_cascade(label="File", menu=fileMenu)

        optionMenu = Menu(menuBar, tearoff=0)
        optionMenu.add_command(label="Settings", command=self.settings, underline=6)
        optionMenu.add_command(label="Statistics", command=self.showStats, underline=1)
        self.animationsOn = BooleanVar()
        optionMenu.add_checkbutton(label="Animations", onvalue=True, offvalue=False,
                                   variable=self.animationsOn, underline=0)
        self.animationsOn.set(True)

        self.soundOn = BooleanVar()
        optionMenu.add_checkbutton(label="Sound effects", onvalue=True, offvalue=False,
                                   variable=self.soundOn, underline=7)
        # No sound by default
        self.soundOn.set(False)

        toolsMenu = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label="Options", menu=optionMenu)
        toolsMenu.add_command(label="Auto-place", command=self.quickplace, underline=0, accelerator="P")
        toolsMenu.add_command(label="Random move", command=self.randomMove, underline=0, accelerator="R")
        menuBar.add_cascade(label="Tools", menu=toolsMenu)

        helpmenu = Menu(menuBar, tearoff=0)
        helpmenu.add_command(label="Help", command=self.helpMe, accelerator="F1", underline=0)
        helpmenu.add_command(label="Visit Website", command=self.visitWebsite, underline=0)
        helpmenu.add_command(label="About", command=self.about, underline=0)
        menuBar.add_cascade(label="Help", menu=helpmenu)

        root.config(menu=menuBar)

        # Create toolbar
        toolbar = Frame(root)
        Button(toolbar, text="New", width=6, command=self.confirmNewGame).pack(side=LEFT, padx=2, pady=2)
        Button(toolbar, text="Load", width=6, command=self.loadGame).pack(side=LEFT, padx=2, pady=2)
        Button(toolbar, text="Save", width=6, command=self.saveGame).pack(side=LEFT, padx=2, pady=2)
        Button(toolbar, text="Settings", width=6, command=self.settings).pack(side=LEFT, padx=2, pady=2)
        Button(toolbar, text="Stats", width=6, command=self.showStats).pack(side=LEFT, padx=2, pady=2)
        toolbar.pack(side=TOP, fill=X)

        # Create status bar
        self.statusBar = Label(root, text="", bd=1, relief=SUNKEN, anchor=W)
        self.statusBar.pack(side=BOTTOM, fill=X)
        self.setStatusBar("Welcome!")

        # Create side panel
        self.sidePanel = Frame(root, relief=SUNKEN, bd=2)

        Label(self.sidePanel, width=20, text="Blue").pack(side=TOP, pady=3)
        self.blueUnitPanel = Canvas(self.sidePanel, height=4 * self.tilePix, width=10 * self.tilePix)
        self.blueUnitPanel.pack(side=TOP)

        Label(self.sidePanel, width=20, text="Red").pack(side=BOTTOM, pady=4)
        self.redUnitPanel = Canvas(self.sidePanel, height=4 * self.tilePix, width=10 * self.tilePix)
        self.redUnitPanel.pack(side=BOTTOM)

        self.sidePanel.pack(side=RIGHT, fill=Y)
        self.sidePanel.bind("<Button-1>", self.panelClick)
        for child in self.sidePanel.winfo_children():
            child.bind("<Button-1>", self.panelClick)

        # Create map
        self.boardsize = self.boardWidth * self.tilePix
        grassImage = Image.open("%s/%s" % (TERRAIN_DIR, LAND_TEXTURE))
        grassImage = grassImage.resize((self.boardWidth * self.tilePix, self.boardWidth * self.tilePix), Image.BICUBIC)
        self.grassImage = ImageTk.PhotoImage(grassImage)
        waterImage = Image.open("%s/%s" % (TERRAIN_DIR, WATER_TEXTURE))
        waterImage = waterImage.resize((self.tilePix, self.tilePix), Image.BICUBIC)
        self.waterImage = ImageTk.PhotoImage(waterImage)
        self.mapFrame = Frame(root, relief=SUNKEN, bd=2)
        self.mapFrame.pack(side=RIGHT, fill=BOTH, expand=1)
        self.map = Canvas(self.mapFrame, width=self.boardsize, height=self.boardsize)
        self.map.pack(side=RIGHT, fill=BOTH, expand=1)

        # Key bindings
        root.bind("<Escape>", self.exit)
        self.map.bind("<Button-1>", self.mapClick)
        self.root.bind("<Button-3>", self.rightClick)
        self.root.bind("p", self.quickplace)
        self.root.bind("r", self.randomMove)
        self.root.bind("<Control-d>", self.toggleDebug)
        self.root.bind("<Control-n>", self.confirmNewGame)
        self.root.bind("<Control-l>", self.loadGame)
        self.root.bind("<Control-s>", self.saveGame)
        self.root.bind("<F1>", self.helpMe)
        self.root.protocol("WM_DELETE_WINDOW", self.exit)

        self.firstMove = "Red"
        self.loadStats()
        self.newGame()

    def confirmNewGame(self, event=None):
        """Ask user to confirm that they want to start a new game and lose their current one"""
        if self.started and (not self.won) and tkMessageBox.askyesno("Confirm new game",
            "If you start a new game, your current game will be lost. Are you sure?"):
                self.newGame()

        if self.won or not self.started:
            self.newGame()

    def newGame(self, event=None):
        """Reset a bunch of variables in order to start a new game"""

        # interaction vars
        self.clickedUnit = None
        self.placingUnit = False
        self.movingUnit = False
        self.turn = self.firstMove
        self.turnNr = 1
        self.won = False
        self.started = False

        # Initialize armies and brains
        self.armyHeight = min(4, (self.boardWidth - 2) / 2)
                
        self.blueArmy = Army("classical", "Blue", self.boardWidth * self.armyHeight)
        self.redArmy = Army("classical", "Red", self.boardWidth * self.armyHeight)
        
        print('** CONTENT OF self.braintypes["Blue"] IS ** : ', self.braintypes["Blue"])

        self.brains = {"Blue": self.braintypes["Blue"](self, self.blueArmy, self.boardWidth) if self.braintypes["Blue"] else 0,
                       "Red": self.braintypes["Red"](self, self.redArmy, self.boardWidth) if self.braintypes["Red"] else 0}

        # (CDLTLL) - Removed .Brain() constructor because it's part of the class name
        # self.brains = {"Blue": self.braintypes["Blue"].Brain(self, self.blueArmy, self.boardWidth) if self.braintypes["Blue"] else 0,
        #                "Red": self.braintypes["Red"].Brain(self, self.redArmy, self.boardWidth) if self.braintypes["Red"] else 0}

        if self.brains["Blue"]:
            self.brains["Blue"].placeArmy(self.armyHeight)

        if self.brains["Red"]:
            self.brains["Red"].placeArmy(self.armyHeight)
            self.started = True
        else:
            self.unitsPlaced = 0

        self.drawSidePanels()
        self.drawMap()
        self.setStatusBar("Place your army, or press 'p' for random placement")

    def loadGame(self, event=None):
        """Open a load dialog, and then load the selected save file and continue playing that game"""

        loadFilename = tkFileDialog.askopenfilename(defaultextension=".sav",
                                                    filetypes=[('%s saves' % GAME_NAME, '.sav')],
                                                      initialdir=os.getcwd())
        if loadFilename:
            with open(loadFilename, 'rU') as f:
                save = pickle.load(f)
                self.boardWidth = save['self.boardWidth']
                self.blueArmy = save['self.blueArmy']
                self.redArmy = save['self.redArmy']
                self.blueBrainName = save['self.blueBrainName']
                self.blueBrain = eval(self.blueBrainName)
                self.braintypes["Blue"] = self.blueBrain
                self.turn = save['self.turn']
                self.won = save['self.won']
                self.started = save['self.started']

                self.brains = {"Blue": self.braintypes["Blue"].Brain(self, self.blueArmy, self.boardWidth) if self.braintypes["Blue"] else 0,
                               "Red": self.braintypes["Red"].Brain(self, self.redArmy, self.boardWidth) if self.braintypes["Red"] else 0}
                self.drawMap()
                self.drawSidePanels()
                self.setStatusBar("Game loaded!")

    def saveGame(self, event=None):
        """Open a save dialog and save the current game to the selected file"""

        saveFilename = tkFileDialog.asksaveasfilename(defaultextension=".sav",
                                                      filetypes=[('%s saves' % GAME_NAME, '.sav')],
                                                      initialdir=os.getcwd())
        if saveFilename:
            with open(saveFilename, 'w') as f:
                pickle.dump({'self.boardWidth': self.boardWidth,
                             'self.blueArmy': self.blueArmy,
                             'self.redArmy': self.redArmy,
                             'self.blueBrainName': self.blueBrainName,
                             'self.turn': self.turn,
                             'self.won': self.won,
                             'self.started': self.started
                             },
                             f)
            self.setStatusBar("Game saved")

    def settings(self):
        """Show a window that allows the user to change several game settings"""

        self.settingsWindow = Toplevel(width=300)
        setIcon(self.settingsWindow, "flag")

        # OPPONENT
        lblBrain = Label(self.settingsWindow, text="Opponent Brain")
        self.blueBrainVar = StringVar(self.settingsWindow)
        if py26:
            mnuBrain = OptionMenu(self.settingsWindow, self.blueBrainVar, *BRAINLIST)
            mnuBrain.config(width=20)
        else:
            mnuBrain = Combobox(self.settingsWindow, textvariable=self.blueBrainVar, state="readonly",
                            justify="center", width=20)
            mnuBrain['values'] = BRAINLIST
        self.blueBrainVar.set(self.blueBrainName)
        lblBrain.grid(column=0, row=0, sticky="ew", ipadx=10, ipady=10)
        mnuBrain.grid(column=1, row=0, sticky="ew", padx=10)

        lblDifficulty = Label(self.settingsWindow, text="Difficulty")
        self.difficultyVar = StringVar(self.settingsWindow)
        if py26:
            mnuDifficulty = OptionMenu(self.settingsWindow, self.difficultyVar, "Normal")
            mnuDifficulty.config(width=20)
        else:
            mnuDifficulty = Combobox(self.settingsWindow, textvariable=self.difficultyVar, state="readonly",
                            justify="center", width=20)
            mnuDifficulty['values'] = ("Normal")
        self.difficultyVar.set(self.difficulty)
        lblDifficulty.grid(column=0, row=1, sticky="ew", ipadx=10, ipady=10)
        mnuDifficulty.grid(column=1, row=1, sticky="ew", padx=10)

        # DEBUG
        lblDebug = Label(self.settingsWindow, text="Debug")
        self.debugVar = StringVar(self.settingsWindow)
        if py26:
            mnuDebug = OptionMenu(self.settingsWindow, self.debugVar, "True", "False")
            mnuDebug.config(width=20)
        else:
            mnuDebug = Combobox(self.settingsWindow, textvariable=self.debugVar, state="readonly",
                            justify="center", width=20)
            mnuDebug['values'] = ("True", "False")

        self.debugVar.set(str(self.debug))
        lblDebug.grid(column=0, row=2, sticky="ew", ipadx=10, ipady=10)
        mnuDebug.grid(column=1, row=2, sticky="ew", padx=10)

        btnOK = Button(self.settingsWindow, text="OK", command=self.updateSettings)
        btnOK.grid(column=0, row=3, columnspan=2, ipadx=15, pady=8)

    def updateSettings(self):
        """Change the internal variables when the user confirms his changes made in the settings window"""

        newBlueBrainName = self.blueBrainVar.get()
        self.debug = (self.debugVar.get() == "True")
        self.drawMap()

        if newBlueBrainName != self.blueBrainName:
            if tkMessageBox.askyesno("Changed settings",
                                 "To change the opponent type, you must start a new game \n" +
                                 "Are you sure?"):
                self.blueBrainName = newBlueBrainName
                self.blueBrain = eval(self.blueBrainName)
                self.newGame()
                self.setStatusBar("Selected " + self.blueBrainName)

        self.settingsWindow.destroy()

    def loadStats(self):
        """Load statistics of past games from the stats file"""

        if os.path.exists('stats.cfg'):
            # (CDLTLL Python 2.7)
            # statsfile = open('stats.cfg', 'rU')
            statsfile = open('stats.cfg', 'rb')

            self.stats = pickle.load(statsfile)
            self.stats.lastChecked = datetime.datetime.now()
            statsfile.close()
        else:
            self.stats = Stats(datetime.datetime.now())

    def showStats(self):
        """Show a window with statistics of past games"""

        self.stats.refresh()
        t = self.stats.totalRunTime
        hours = t.seconds / 3600
        minutes = (t.seconds % 3600) / 60
        seconds = t.seconds % 60
        timestr = '%s days, %i:%02i:%02i' % (t.days, hours, minutes, seconds)

        self.statsWindow = Toplevel(width=300)
        setIcon(self.statsWindow, "flag")
        lblNames = Label(self.statsWindow, justify=LEFT,
                         text=dedent("""
                         Games played:
                         Won:
                         Lost:
                         Win percentage:
                         
                         Longest winning streak:
                         Lowest casualties:
                         Least moves:
                         
                         Total time played:"""))
        lblNames.grid(column=0, row=0, sticky="ew", ipadx=35, ipady=10)

        lblStats = Label(self.statsWindow, justify=RIGHT,
                         text=""" 
                         %i
                         %i
                         %i
                         %.1f%%
                         
                         %i
                         %i
                         %i
                         
                         %s""" % (self.stats.gamesPlayed, self.stats.gamesWon, self.stats.gamesLost,
                                  100. * self.stats.gamesWon / max(1, self.stats.gamesPlayed),
                                  self.stats.longestStreak,
                                  self.stats.lowestCasualties,
                                  self.stats.leastMoves,
                                  timestr))
        lblStats.grid(column=1, row=0, sticky="ew", ipadx=35, ipady=10)

        btnOK = Button(self.statsWindow, text="OK", command=self.closeStats)
        btnOK.grid(column=0, row=1, columnspan=2, ipadx=15, pady=15)

    def closeStats(self):
        """Close the statistics window"""
        self.statsWindow.destroy()

    def helpMe(self, event=None):
        """Show a window with information about the game rules and the different pieces"""

        self.helpWindow = Toplevel(width=400, height=640)
        setIcon(self.helpWindow, "flag")

        # Python 2.6 doesn't have the fancy ttk notebook widget, so it
        # will have to make do with the plain old help
        if py26:
            f = self.helpUnits(Frame(self.helpWindow))
            f.grid()

        else:
            helpNB = Notebook(self.helpWindow)
            helpNB.enable_traversal()
            helpNB.grid(column=0, row=0, sticky=N + S + E + W)

            tabs = [(self.helpBasicRules, "Basic Rules"),
                    (self.helpUnits, "Units"),
                    (self.helpMore, "Optional Rules")]

            for f, title in tabs:
                frame = Frame(self.helpWindow)
                tab = f(frame)
                helpNB.add(tab, text=title)

        btnOK = Button(self.helpWindow, text="OK", command=self.closeHelp)
        btnOK.grid(column=0, row=1, columnspan=2, ipadx=15, pady=8)

        self.root.update_idletasks()
        w, h = self.helpWindow.geometry().split("+")[0].split("x")
        self.helpWindow.minsize(w, h)
        self.helpWindow.maxsize(w, h)

    def helpBasicRules(self, frame):
        """Show a text about the basic game rules in the help dialog"""

        paragraphs = [
        ("Introduction", """
        The goal of %s is to capture your enemy's flag while protecting your own. 
        If you take the enemy flag or if the enemy has no movable pieces left, you win.  
        To achieve this, you have a set of units with different strengths and abilities.
        For more details about the units, see the corresponding help page.""" % (GAME_NAME)),

        ("Army Placement", """
        The game starts with an empty board, and it is up to you to place your units in a strong formation.
        Put your flag in a safe place and use bombs for extra protection, but don't block your own troops.
        You can press 'p' to put your unplaced units on the board randomly. Once all pieces are placed,
        the real game begins."""),

        ("Movement", """
        A player can move one unit each turn. Most units can move a single tile per turn.
        The exceptions are scouts, who can move farther, and bombs and flags, which cannot move.
        You can never moved to a tile occupied by a friendly piece or by water."""),

        ("Battles", """
        When a player moves a unit to a tile occupied by a unit of the opposing army, there is a fight.
        Both players get to see the rank of the enemy piece, and the weaker piece dies.
        If the pieces are of equal rank, both die.""")]

        txt = Text(frame, height=40, background=HELP_BG, padx=20, pady=20)
        txt.tag_config("title", font=HELP_TITLE_FONT, underline=1)
        txt.tag_config("main", font=HELP_BODY_FONT)
        wrapper = TextWrapper(width=80)

        for p in paragraphs:
            txt.insert(END, p[0] + "\n\n", "title")
            wrappedText = wrapper.fill(dedent(p[1])) + "\n\n"
            txt.insert(END, wrappedText, "main")
        txt.grid(sticky=N + S + E + W)
        txt.config(state=DISABLED)
        return frame

    def helpUnits(self, frame):
        """Show help about units"""

        self.helpImage = Image.open("help.png")
        self.helpImage = ImageTk.PhotoImage(self.helpImage)
        lbl = Label(frame, image=self.helpImage)
        lbl.grid(column=0, row=0, sticky="ew")
        return frame

    def helpMore(self, frame):
        """Show help about special options and rules, different from classic Stratego"""

        paragraphs = [(
        "Special Rules", """
        %s includes several optional variations on the classic board game Stratego,
        and they are explained here.""" % (GAME_NAME)),

        ("Diagonal movement", """
        Enabling units to move diagonally, instead of only horizontally and vertically, 
        leads to important differences in strategy. You will have to rethink how to protect your flag
        or how to escort your spy."""),

        ("Board size", """
        Playing on a different board size automatically scales your army. You can play a game on a smaller board for 
        some quick fun, or accept the challenge of playing on an extra large board where it might to hundreds of turns
        to resolve the battle.
        
        :)  
        """)]

        txt = Text(frame, height=40, background=HELP_BG, padx=20, pady=20)
        txt.tag_config("title", font=HELP_TITLE_FONT, underline=1)
        txt.tag_config("main", font=HELP_BODY_FONT)
        wrapper = TextWrapper(width=80)

        for p in paragraphs:
            txt.insert(END, p[0] + "\n\n", "title")
            wrappedText = wrapper.fill(dedent(p[1])) + "\n\n"
            txt.insert(END, wrappedText, "main")
        txt.grid(sticky=N + S + E + W)
        txt.config(state=DISABLED)
        return frame

    def closeHelp(self):
        """Close the help window"""
        self.helpWindow.destroy()

    def visitWebsite(self):
        """Open the Google Code website in the default browser"""
        webbrowser.open(URL)

    def about(self):
        """Show a window with information about the game developers and credits for used content"""
        wrapper = TextWrapper(width=60)

        fulltext = """\

        This game is inspired by the classic board game Stratego (copyright Hasbro).

        CREDITS:

        Sound effects by pierrecartoons1979, steveygos93, Erdie and benboncan
        (Creative Commons at freesounds.org)

        Music by the United States Army Old Guard Fife And Drum Corps 
        (Public domain, available at freemusicarchive.org)

        Unit icons are borrowed from stratego-gui, another Stratego-inspired project 
        on Google Code (GPL)

        All the background images in the game launcher are in the public domain. 
        """ % (GAME_NAME, AUTHORS)

        paragraphs = fulltext.split("\n\n")
        windowtext = ""

        for p in paragraphs:
            windowtext += wrapper.fill(dedent(p)) + "\n\n"
        tkMessageBox.showinfo("%s %s" % (GAME_NAME, VERSION), windowtext)

    def setStatusBar(self, newText):
        """Change the text in the status bar."""

        self.statusBar.config(text=newText)

    def drawMap(self):
        """Draw the tiles and units on the map."""
        
        self.map.delete(ALL)
        self.map.create_image(0, 0, image=self.grassImage, anchor=NW)

        # draw water
        for x in range(self.boardWidth):
            for y in range(self.boardWidth):
                if self.isWater(x, y):
                    self.map.create_image(x * self.tilePix, y * self.tilePix, image=self.waterImage, anchor=NW)

        # draw lines
        for i in range(self.boardWidth - 1):
            x = self.tilePix * (i + 1)
            self.map.create_line(x, 0, x, self.boardsize, fill="black")
            self.map.create_line(0, x, self.boardsize, x, fill="black")

        for unit in self.redArmy.army:
            if unit.alive:
                (x, y) = unit.getPosition()
                self.drawUnit(self.map, unit, x, y)

        for unit in self.blueArmy.army:
            if unit.alive:
                (x, y) = unit.getPosition()
                self.drawUnit(self.map, unit, x, y)

    def drawTile(self, x, y, tileColor):
        """Fill a tile with its background color - Currently unused"""
        self.map.create_rectangle(x * self.tilePix, y * self.tilePix, (x + 1) * self.tilePix, (y + 1) * self.tilePix, fill=tileColor)

    def drawMoveArrow(self, old, new):
        """Draw an arrow indicating the opponent's move"""
        self.map.create_line(int((old[0] + 0.5) * self.tilePix), int((old[1] + 0.5) * self.tilePix),
                             int((new[0] + 0.5) * self.tilePix), int((new[1] + 0.5) * self.tilePix),
                             width=3, fill=MOVE_ARROW_COLOR, arrow=LAST, arrowshape="8 10 6",
                             tags="moveArrow")

    def clearMoveArrows(self):
        self.map.delete("moveArrow")

    def drawSidePanels(self):
        """Draw the unplaced units in the sidebar widget."""
        self.blueUnitPanel.delete(ALL)
        self.redUnitPanel.delete(ALL)

        self.blueUnitPanel.create_rectangle(0, 0, 10 * self.tilePix, 4 * self.tilePix, fill=UNIT_PANEL_COLOR)
        self.redUnitPanel.create_rectangle(0, 0, 10 * self.tilePix, 4 * self.tilePix, fill=UNIT_PANEL_COLOR)

        unplacedRed = 0
        for unit in sorted(self.redArmy.army, key=lambda x: x.sortOrder):
            if unit.isOffBoard():
                x = unplacedRed % 10
                y = unplacedRed / 10
                unit.setPosition(self.offBoard(x), self.offBoard(y))
                self.drawUnit(self.redUnitPanel, unit, x, y)
                unplacedRed += 1

        unplacedBlue = 0
        for unit in sorted(self.blueArmy.army, key=lambda x: x.sortOrder):
            if unit.isOffBoard():
                x = unplacedBlue % 10
                y = unplacedBlue / 10
                unit.setPosition(self.offBoard(x), self.offBoard(y))
                self.drawUnit(self.blueUnitPanel, unit, x, y)
                unplacedBlue += 1

    def drawUnit(self, canvas, unit, x, y, color=None):
        """Draw unit tile with correct color and image, 3d border etc"""
        if color == None:
            color = RED_PLAYER_COLOR if unit.color == "Red" else BLUE_PLAYER_COLOR

        hilight = SELECTED_RED_PLAYER_COLOR if unit.color == "Red" else SELECTED_BLUE_PLAYER_COLOR
        shadow = SHADOW_RED_COLOR if unit.color == "Red" else SHADOW_BLUE_COLOR

        # draw hilight
        canvas.create_rectangle(x * self.tilePix, y * self.tilePix,
                                (x + 1) * self.tilePix, (y + 1) * self.tilePix,
                                fill=hilight, outline=None, tags="u" + str(id(unit)))
        # draw shadow
        canvas.create_rectangle(x * self.tilePix + TILE_BORDER, y * self.tilePix + TILE_BORDER,
                                (x + 1) * self.tilePix, (y + 1) * self.tilePix,
                                fill=shadow, outline=None, width=0, tags="u" + str(id(unit)))
        # draw center
        canvas.create_rectangle(x * self.tilePix + TILE_BORDER, y * self.tilePix + TILE_BORDER,
                                (x + 1) * self.tilePix - TILE_BORDER, (y + 1) * self.tilePix - TILE_BORDER,
                                fill=color, outline=None, width=0, tags="u" + str(id(unit)))

        if unit.color == "Red" or self.debug or not unit.alive or self.won or unit.justAttacked:
            unit.justAttacked = False
            canvas.create_image(x * self.tilePix, y * self.tilePix,
                                image=self.unitIcons.getIcon(unit.name), anchor=NW, tags="u" + str(id(unit)))
            if unit.name != "Bomb" and unit.name != "Flag":
                canvas.create_text(((x + .2) * self.tilePix, (y + .8) * self.tilePix),
                                   text=unit.rank, fill=MOVE_ARROW_COLOR, tags="u" + str(id(unit)))

        if not unit.alive:
            canvas.create_line(x * self.tilePix, y * self.tilePix,
                               (x + 1) * self.tilePix, (y + 1) * self.tilePix,
                               tags="u" + str(id(unit)), width=3, fill=DEAD_COLOR, capstyle=ROUND)
            canvas.create_line(x * self.tilePix, (y + 1) * self.tilePix,
                               (x + 1) * self.tilePix, y * self.tilePix,
                               tags="u" + str(id(unit)), width=3, fill=DEAD_COLOR, capstyle=ROUND)

    def isWater(self, x, y):
        """Check whether there is a pool at tile (x,y)."""

        # uneven board size + middle row or even board size + middle 2 rows
        if  (self.boardWidth % 2 == 1 and y == self.boardWidth / 2) or \
            ((self.boardWidth % 2 == 0) and (y == self.boardWidth / 2 or y == (self.boardWidth / 2) - 1)):

            return sin(2 * pi * (x + .5) / BOARD_WIDTH * (POOLS + 0.5)) < 0

    def isWaterColumn(self, x):
        """Check whether there is a pool in column x"""
        return sin(2 * pi * (x + .5) / BOARD_WIDTH * (POOLS + 0.5)) < 0

    def rightClick(self, event):
        """Deal with right-click (i.e., deselect selected unit"""
        self.clickedUnit = None
        self.movingUnit = False
        self.drawMap()
        self.drawSidePanels()
        self.setStatusBar("")

    def mapClick(self, event):
        """Process clicks on the map widget."""

        print("** self.tilePix **:",self.tilePix)

        print("event.x: ", event.x)
        print("event.y: ", event.y)

        #(CDLTLL) round() or int()
        x = int(event.x / self.tilePix)
        y = int(event.y / self.tilePix)

        print("x: ", x)
        print("y: ", x)

        if self.isWater(x, y):
            terrain = 'water'
        else:
            terrain = 'land'

        if self.placingUnit:
            self.placeUnit(x, y)

        elif self.movingUnit and not self.won:
            self.moveUnit(x, y)

        else:
            # find clicked unit
            unit = self.getUnit(x, y)

            if unit:
                if unit.color == "Blue":
                    self.setStatusBar("You clicked an enemy unit at (%s, %s)" % (x, y))
                    return

                else:
                    if unit.isMovable() or not self.started:
                        self.movingUnit = True
                        self.clickedUnit = unit
                        self.drawUnit(self.map, unit, x, y, SELECTED_RED_PLAYER_COLOR)

            else:
                unit = "no unit at (%s, %s)" % (x, y)

            self.setStatusBar("You clicked a %s tile with %s" % (terrain, unit))

    def placeUnit(self, x, y):
        """Place a unit on the map at the first of the game"""
        if self.isWater(x, y):
            self.setStatusBar("You can't place units in the water!")
            return

        if self.getUnit(x, y):
            self.setStatusBar("Can't place %s there, spot already taken!" % self.clickedUnit.name)
            return

        if y < (self.boardWidth - self.armyHeight):
            self.setStatusBar("Must place unit in the first %i rows" % self.armyHeight)
            return

        if x < 0 or x >= self.boardWidth:
            self.setStatusBar("You can't place a unit off the edge of the board!")
            return

        self.clickedUnit.setPosition(x, y)
        self.setStatusBar("Placed %s" % self.clickedUnit)
        self.placingUnit = False
        self.clickedUnit = None
        self.unitsPlaced += 1
        if self.unitsPlaced == len(self.redArmy.army):
            self.started = True

        self.drawSidePanels()
        self.drawMap()

    def moveUnit(self, x, y):
        """Move a unit according to selected unit and clicked destination"""
        if not self.legalMove(self.clickedUnit, x, y):
            self.setStatusBar("You can't move there! If you want, you can right click to deselect the currently selected unit.")
            return

        if self.clickedUnit.color == "Red":
            thisArmy = self.redArmy
        else:
            thisArmy = self.blueArmy

        # Moving more than one tile will "expose" the unit as a scout
        (i, j) = self.clickedUnit.getPosition()
        if abs(i - x) > 1 or abs(j - y) > 1:
            self.clickedUnit.isKnown = True

        # Do move animation
        stepSize = self.tilePix / MOVE_ANIM_STEPS
        dx = x - i
        dy = y - j
        self.clearMoveArrows()

        if self.animationsOn.get():
            for _step in range(MOVE_ANIM_STEPS):
                self.root.after(MOVE_ANIM_FRAMERATE,
                    self.map.move("u" + str(id(self.clickedUnit)), stepSize * dx, stepSize * dy))
                self.root.update_idletasks()

        target = self.getUnit(x, y)
        if target:
            if target.color == self.clickedUnit.color and self.started:
                self.setStatusBar("You can't move there - tile already occupied!")

            elif target.color == self.clickedUnit.color and not self.started:  # switch units
                    (xold, yold) = self.clickedUnit.getPosition()
                    target.setPosition(xold, yold)
                    self.clickedUnit.setPosition(x, y)
                    self.clickedUnit = None
                    self.movingUnit = None

                    self.drawMap()
            else:
                self.attack(self.clickedUnit, target)
                if self.started:
                    self.endTurn()
            return

        else:
            self.setStatusBar("Moved %s to (%s, %s)" % (self.clickedUnit, x, y))
            if (abs(self.clickedUnit.position[0] - x) + abs(self.clickedUnit.position[1] - y)) > 1 and self.clickedUnit.hasMovedFar != True:
                if not self.clickedUnit.hasMoved:
                    thisArmy.nrOfKnownMovable += 1
                elif not self.clickedUnit.isKnown:
                    thisArmy.nrOfUnknownMoved -= 1
                    thisArmy.nrOfKnownMovable += 1
                self.clickedUnit.hasMovedFar = True
                for unit in thisArmy.army:
                    if self.clickedUnit == unit:
                        unit.isKnown = True
                        unit.possibleMovableRanks = ["Scout"]
                        unit.possibleUnmovableRanks = []
                    elif "Scout" in unit.possibleMovableRanks:unit.possibleMovableRanks.remove("Scout")
            elif self.clickedUnit.hasMoved != True:
                thisArmy.nrOfUnknownMoved += 1
                self.clickedUnit.hasMoved = True
                for unit in thisArmy.army:
                    if self.clickedUnit == unit:
                        unit.possibleUnmovableRanks = []

            self.clickedUnit.setPosition(x, y)
            self.clickedUnit.hasMoved = True

        self.clickedUnit = None
        self.movingUnit = False

        self.drawMap()

        if self.started:
            self.endTurn()

    def otherPlayer(self, color):
        """Return opposite color"""
        if color == "Red": return "Blue"
        return "Red"

    def otherArmy(self, color):
        """Return opposite army"""
        if color == "Red": return self.blueArmy
        return self.redArmy

    def endTurn(self):
        """Switch turn to other player and check for end of game conditions"""
        self.turn = self.otherPlayer(self.turn)
        self.turnNr += 1

        if self.brains[self.turn] and not self.won:  # computer player?
            (oldlocation, move) = self.brains[self.turn].findMove()

            # check if the opponent can move
            if move == None:
                self.victory(self.otherPlayer(self.turn), True)
                return

            unit = self.getUnit(oldlocation[0], oldlocation[1])
            unit.hasMoved = True

            # Do move animation
            stepSize = self.tilePix / MOVE_ANIM_STEPS
            dx = move[0] - oldlocation[0]
            dy = move[1] - oldlocation[1]

            if self.animationsOn.get():
                for _step in range(MOVE_ANIM_STEPS):
                    self.root.after(MOVE_ANIM_FRAMERATE,
                        self.map.move("u" + str(id(unit)), stepSize * dx, stepSize * dy))
                    self.root.update_idletasks()

            self.drawMoveArrow(oldlocation, move)
            enemy = self.getUnit(move[0], move[1])
            if enemy:
                self.attack(unit, enemy)
            else:
                unit.setPosition(move[0], move[1])

            # check if player can move
            tempBrain = randomBrain(self, self.redArmy, self.boardWidth)
            playerMove = tempBrain.findMove()
            if playerMove[0] == None:
                self.victory(self.turn, True)
                return

            if self.difficulty == "Easy":
                for unit in self.redArmy.army:
                    if unit.isKnown and random() <= FORGETCHANCEEASY:
                        unit.isKnown = False

            self.setStatusBar("%s moves unit at (%s,%s) to (%s,%s)" % (self.turn,
                                                                       oldlocation[0], oldlocation[1],
                                                                       move[0], move[1]))
            self.drawMap()
            if not enemy:
                self.drawMoveArrow(oldlocation, move)
            self.drawSidePanels()

        self.turn = self.otherPlayer(self.turn)

    def legalMove(self, unit, x, y):
        """Check whether a move:
            - does not end in the water
            - does not end off-board
            - is only in one direction
            - is not farther than one step, for non-scouts
            - does not jump over obstacles, for scouts
        """

        if self.isWater(x, y):
            return False

        (ux, uy) = unit.position
        dx = abs(ux - x)
        dy = abs(uy - y)

        if x >= self.boardWidth or y >= self.boardWidth or x < 0 or y < 0:
            return False

        if not self.started:
            if y < (self.boardWidth - 4):
                return False
            return True

        if unit.walkFar:
            if dx != 0 and dy != 0:
                if self.diagonal:
                    if dx != dy:
                        return False
                else:
                    return False

            if (dx + dy) == 0:
                return False

            if dx > 0 and dy == 0:
                x0 = min(x, ux)
                x1 = max(x, ux)
                for i in range(x0 + 1, x1):
                    if self.isWater(i, y) or self.getUnit(i, y):
                        return False

            elif dy > 0 and dx == 0:
                y0 = min(y, uy)
                y1 = max(y, uy)
                # (CDLTLL)
                # for i in range(y0 + 1, y1):
                for i in range(int(y0 + 1), int(y1)):
                    if self.isWater(x, i) or self.getUnit(x, i):
                        return False

            else:
                xdir = dx / (x - ux)
                ydir = dy / (y - uy)
                distance = abs(x - ux)
                for i in range(1, distance):
                    if self.isWater(ux + i * xdir, uy + i * ydir) or self.getUnit(ux + i * xdir, uy + i * ydir):
                        return False
        else:
            s = dx + dy
            if self.diagonal:
                if s == 0 or max(dx, dy) > 1:
                    return False
            elif s != 1:
                return False

        return True

    def attack(self, attacker, defender):
        """Show the outcome of an attack and remove defeated pieces from the board"""

        ########
        if attacker.color == "Red":
            attackerArmy = self.redArmy
            defenderArmy = self.blueArmy
        else:
            attackerArmy = self.blueArmy
            defenderArmy = self.redArmy

        # Only the first time a piece becomes known, the possible ranks are updated:
        if not attacker.isKnown:
            if attacker.hasMoved:
                attackerArmy.nrOfUnknownMoved -= 1
            attacker.hasMoved = True
            attackerArmy.nrOfKnownMovable += 1
            for unit in attackerArmy.army:
                if unit == attacker:
                    attacker.possibleMovableRanks = [attacker.name]
                    attacker.possibleUnmovableRanks = []
                elif attacker.name in unit.possibleMovableRanks: unit.possibleMovableRanks.remove(attacker.name)

        if defender.canMove and not defender.isKnown:
            if defender.hasMoved:
                defenderArmy.nrOfUnknownMoved -= 1
            defender.hasMoved = True  # Although it not moved, it is known and attacked, so..
            defenderArmy.nrOfKnownMovable += 1
            for unit in defenderArmy.army:
                if unit == defender:
                    defender.possibleMovableRanks = [defender.name]
                    defender.possibleUnmovableRanks = []
                elif defender.name in unit.possibleMovableRanks: unit.possibleMovableRanks.remove(defender.name)
        elif not defender.isKnown:
            defenderArmy.nrOfKnownUnmovable += 1
            for unit in defenderArmy.army:
                if unit == defender:
                    defender.possibleUnmovableRanks = [defender.name]
                    defender.possibleMovableRanks = []
                elif defender.name in unit.possibleUnmovableRanks: unit.possibleUnmovableRanks.remove(defender.name)


        ##########

        text = "A %s %s attacked a %s %s. " % (attacker.color, attacker.name, defender.color, defender.name)
        attacker.isKnown = True
        defender.isKnown = True

        if defender.name == "Flag":
            attacker.position = defender.position
            defender.die()
            self.victory(attacker.color)

        elif attacker.canDefuseBomb and defender.name == "Bomb":
            attacker.position = defender.position
            defender.die()
            defenderArmy.nrOfLiving -= 1
            defenderArmy.nrOfKnownUnmovable -= 1
            attacker.justAttacked = True
            text += "The mine was disabled."
            if (abs(attacker.position[0] - self.blueArmy.army[0].position[0]) + abs(attacker.position[1] - self.blueArmy.army[0].position[1]) == 1):
                self.blueArmy.flagIsBombProtected = False
            if (abs(attacker.position[0] - self.redArmy.army[0].position[0]) + abs(attacker.position[1] - self.redArmy.army[0].position[1]) == 1):
                self.redArmy.flagIsBombProtected = False

        elif defender.name == "Bomb":
            x, y = defender.getPosition()
            x = (x + .5) * self.tilePix
            y = (y + .5) * self.tilePix

            attackerTag = "u" + str(id(attacker))
            attacker.die()
            # print 'attacker:', attackerTag, self.map.find_withtag(attackerTag)

            self.root.after(200, lambda: self.map.delete(attackerTag))
            explosion.kaboom(x, y, 5, self.map, self.root)
            text += "\nThe %s was blown to pieces." % attacker.name

            attackerArmy.nrOfLiving -= 1
            attackerArmy.nrOfKnownMovable -= 1

        elif attacker.canKillMarshal and defender.name == "Marshal":
            attacker.position = defender.position
            defenderArmy.nrOfLiving -= 1
            defenderArmy.nrOfMoved -= 1
            defender.die()
            attacker.justAttacked = True
            text += "The marshal has been assassinated."

        elif attacker.rank > defender.rank:
            attacker.position = defender.position
            defenderArmy.nrOfLiving -= 1
            defenderArmy.nrOfMoved -= 1
            defender.die()
            attacker.justAttacked = True
            text += "The %s was defeated." % defender.name

        elif attacker.rank == defender.rank:
            defenderArmy.nrOfLiving -= 1
            defenderArmy.nrOfMoved -= 1
            attackerArmy.nrOfLiving -= 1
            attackerArmy.nrOfMoved -= 1
            attacker.die()
            defender.die()
            text += "Both units died."

        else:
            attackerArmy.nrOfLiving -= 1
            attackerArmy.nrOfMoved -= 1
            attacker.die()
            text += "The %s was defeated." % attacker.name

        if not self.won:
            text = fill(dedent(text), 60)

            self.battleResultDialog = Toplevel(width=300)
            self.battleResultDialog.title("Battle result")
            self.battleResultDialog.grab_set()
            self.battleResultDialog.bind("<Return>", self.closeBattleResultWindow)
            self.battleResultDialog.focus()
            setIcon(self.battleResultDialog, "flag")

            atkImg = ImageTk.PhotoImage(self.unitIcons.getImage(attacker.name, 120))
            atkLbl = Label(self.battleResultDialog, image=atkImg)
            atkLbl.image = atkImg
            atkLbl.grid(row=0, column=0, sticky=NW)

            defImg = ImageTk.PhotoImage(self.unitIcons.getImage(defender.name, 120))
            defLbl = Label(self.battleResultDialog, image=defImg)
            defLbl.image = defImg

            message = Label(self.battleResultDialog, text=text)
            message.grid(row=0, column=1, sticky=NE, ipadx=15, ipady=50)

            defLbl.grid(row=0, column=2, sticky=NE)

            ok = Button(self.battleResultDialog, text="OK", command=self.closeBattleResultWindow)
            ok.grid(row=1, column=1, ipadx=15, ipady=5, pady=5)

            # sound effects
            if defender.name == "Bomb":
                if attacker.canDefuseBomb:
                    self.playSound(SOUND_DEFUSE)
                else:
                    self.playSound(SOUND_BOMB)
            elif defender.name == "Marshal" and attacker.canKillMarshal:
                self.playSound(SOUND_ARGH)
            elif defender.name == "Marshal" and attacker.name == "Marshal":
                self.playSound(SOUND_OHNO)
            elif attacker.name == "Marshal":
                self.playSound(SOUND_LAUGH)
            else:
                self.playSound(SOUND_COMBAT)
            self.root.wait_window(self.battleResultDialog)

        self.clearMoveArrows()
        self.drawSidePanels()
        self.clickedUnit = None
        self.movingUnit = False

    def closeBattleResultWindow(self, event=None):
        """Called by key event to close the battle result window"""
        self.battleResultDialog.destroy()

    def trumps(self, unitA, unitB):
        """Check the (potential) outcome of a battle without changing the game state"""
        pass


    def getUnit(self, x, y):
        """Return unit at a certain position"""
        return self.redArmy.getUnit(x, y) or self.blueArmy.getUnit(x, y)

    def getAdjacent(self, x, y):
        """ Return a list of directly adjacent tile coordinates, considering the edge of the board
        and whether or not diagonal movement is enabled."""

        adjacent = []

        if x > 0:
            adjacent += [(x - 1, y)]  # West
            if self.diagonal:
                if y > 0:
                    adjacent += [(x - 1, y - 1)]  # Northwest
                elif y < self.boardWidth - 1:
                    adjacent += [(x - 1, y + 1)]  # Southwest
        if y > 0:
            adjacent += [(x, y - 1)]  # North
        if y < self.boardWidth - 1:
            adjacent += [(x, y + 1)]  # South
        if x < self.boardWidth - 1:
            adjacent += [(x + 1, y)]  # East
            if self.diagonal:
                if x > 0:
                    adjacent += [(x + 1, y - 1)]  # Southwest
                if x < self.boardWidth - 1:
                    adjacent += [(x + 1, y + 1)]  # Southeast

        return adjacent

    def toggleDebug(self, event):
        self.debug = not self.debug
        self.drawMap()

    def panelClick(self, event):
        """Process mouse clicks on the side panel widget."""
        #(CDLTLL) round() or int()
        x = int(event.x / self.tilePix)
        y = int(event.y / self.tilePix)

        if event.widget == self.redUnitPanel:
            panel = "red"
            army = self.redArmy
        elif event.widget == self.blueUnitPanel:
            panel = "blue"
            army = self.blueArmy
        else:
            panel = ""

        if panel:
            unit = army.getUnit(self.offBoard(x), self.offBoard(y))
            if unit and unit.alive:
                self.setStatusBar("You clicked on %s %s" % (panel, unit))

                if panel == "red":  # clicked player unit
                    self.clickedUnit = unit
                    self.placingUnit = True

                    # highlight unit
                    self.drawUnit(self.redUnitPanel, unit, x, y)

                    self.setStatusBar("Click the map to place this unit")

    def offBoard(self, x):
        """Return negative coordinates used to indicate off-board position. Avoid zero."""
        return -x - 1

    def victory(self, color, noMoves=False):
        """Show the victory/defeat screen"""
        self.won = True
        self.drawMap()
        top = Toplevel(width=300)
        setIcon(top, "flag")
        flagimg1 = Image.open("%s/%s.%s" % (ICON_DIR, "flag", ICON_TYPE))
        flagimg2 = ImageTk.PhotoImage(flagimg1)
        lbl = Label(top, image=flagimg2)
        lbl.image = flagimg2
        lbl.grid(row=0, column=1, sticky=NW)

        if color == "Red":
            top.title("Victory!")
            if noMoves:
                messageTxt = "The enemy army has been immobilized. Congratulations, you win!"
            else:
                messageTxt = "Congratulations! You've captured the enemy flag!"

        else:
            top.title("Defeat!")
            if noMoves:
                messageTxt = "There are no valid moves left. You lose."
            else:
                messageTxt = "Unfortunately, the enemy has captured your flag. You lose."

        casualties = len(self.redArmy.army) - self.redArmy.nrAlive()
        self.stats.addGame(color == "Red", casualties, self.turnNr)
        message = Label(top, text=messageTxt)
        message.grid(row=0, column=0, sticky=NE, ipadx=15, ipady=50)

        ok = Button(top, text="OK", command=top.destroy)
        ok.grid(row=1, column=0, columnspan=2, ipadx=15, ipady=5, pady=5)

        message.configure(width=40, justify=CENTER, wraplength=150)
        self.setStatusBar("%s has won the game in %i turns!" % (color, self.turnNr))
        if color == "Red":
            self.playSound(SOUND_WIN)
        else:
            self.playSound(SOUND_LOSE)

    def playSound(self, name):
        """Play a sound, if on Windows and if sound is enabled"""
        sound=pygame.mixer.Sound(os.path.join(SOUND_DIR, name))
        sound.play()
        time.sleep(sound.get_length())
        print("Playing sound {}".format(os.path.join(SOUND_DIR, name)))


    def quickplace(self, event=None):
        """Let the computer place human player's pieces randomly"""
        if not self.started:
            tempBrain = randomBrain(self, self.redArmy, self.boardWidth)
            tempBrain.placeArmy(self.armyHeight)

            self.drawMap()
            self.drawSidePanels()
            self.setStatusBar("Randomly placed your army!")
            self.started = True

    def randomMove(self, event=None):
        if not self.started: return
        tempBrain = randomBrain(self, self.redArmy, self.boardWidth)
        (oldlocation, move) = tempBrain.findMove()
        unit = self.getUnit(oldlocation[0], oldlocation[1])

        self.movingUnit = True
        self.clickedUnit = unit
        # self.drawUnit(self.map, unit, move[0], move[1], SELECTED_RED_PLAYER_COLOR)

        unit.hasMoved = True

        # Do move animation
        stepSize = self.tilePix / MOVE_ANIM_STEPS
        dx = move[0] - oldlocation[0]
        dy = move[1] - oldlocation[1]
        self.drawMoveArrow(oldlocation, move)

        if self.animationsOn.get():
            for _step in range(MOVE_ANIM_STEPS):
                self.root.after(MOVE_ANIM_FRAMERATE,
                    self.map.move("u" + str(id(unit)), stepSize * dx, stepSize * dy))
                self.root.update_idletasks()

        enemy = self.getUnit(move[0], move[1])
        if enemy:
            self.attack(unit, enemy)
        else:
            unit.setPosition(move[0], move[1])

        self.clickedUnit = None
        self.movingUnit = False
        self.drawMap()
        self.drawMoveArrow(oldlocation, move)
        time.sleep(.5)
        self.endTurn()

    def exit(self, event=None):
        """Quit program."""
        self.stats.save()
        self.root.quit()

class Stats:
    """Class containing a number of statistics about previously played
        games, such as number of games played or win percentage."""
    def __init__(self, lastChecked):
        self.gamesPlayed = 0
        self.gamesWon = 0
        self.gamesLost = 0

        self.currentStreak = 0
        self.longestStreak = 0
        self.lowestCasualties = 999
        self.leastMoves = 999

        self.totalRunTime = datetime.timedelta(0)
        self.lastChecked = lastChecked

    def addGame(self, won, casualties, moves):
        """Update the statistics dependent on the number of games played, won or lost"""
        self.gamesPlayed += 1
        if won:
            self.gamesWon += 1
            self.currentStreak += 1
            self.longestStreak = max(self.longestStreak, self.currentStreak)
            self.lowestCasualties = min(self.lowestCasualties, casualties)
            self.leastMoves = min(self.leastMoves, moves)
        else:
            self.gamesLost += 1
            self.currentStreak = 0

    def refresh(self):
        """Update the total running time"""
        self.totalRunTime += (datetime.datetime.now() - self.lastChecked)
        self.lastChecked = datetime.datetime.now()

    def save(self):
        """Save the statistics to a file"""
        self.refresh()
        #(CDLTLL) Changed to binary mode
        # with open('stats.cfg', 'w') as f:
        with open('stats.cfg', 'wb') as f:
            pickle.dump(self, f)

class Launcher():
    """The launcher is the first window shown after starting the game, providing
        some fancy graphics and music, as well as some options to start a game"""

    menus = 0

    def __init__(self, root):
        self.root = root
        self.top = Toplevel(root, bd=0)
        self.top.minsize(900, 675)
        self.top.maxsize(900, 675)
        self.top.geometry("+50+50")
        self.top.title("%s v%s" % (GAME_NAME, VERSION))
        self.top.bind("<Escape>", self.exit)
        setIcon(self.top, "flag")
        self.top.protocol("WM_DELETE_WINDOW", self.exit)

        buttonpadx = 12

        Label(self.top).grid()

        self.bgid = 0
        self.textid = 0
        self.backgrounds = len([x for x in os.listdir("backgrounds") if "background" in x ])
        self.bgcanvas = Canvas(self.top, width=900, height=600, bd=0)
        self.bgcanvas.place(x=0, y=0)
        self.newBackground()

        # Disable music for now
        # self.playMusic()

        self.playbutton = Button(self.top, text="Play", width=10, padx=20, command=self.startGame)
        self.playbutton.grid(row=1, column=0, padx=buttonpadx, pady=5, sticky=W)

        self.loadButton = Button(self.top, text="Load", width=10, padx=20, command=self.loadGame)
        self.loadButton.grid(row=2, column=0, padx=buttonpadx, pady=5, sticky=W)

        self.exitbutton = Button(self.top, text="Exit", width=10, padx=20, command=self.exit)
        self.exitbutton.grid(row=2, column=5, padx=buttonpadx, pady=5, sticky=E)

        self.blueBrainVar = StringVar(self.top)
        self.addMenu("Opponent", self.blueBrainVar, BRAINLIST, DEFAULTBRAIN)

        self.difficultyVar = StringVar(self.top)
        self.addMenu("Difficulty", self.difficultyVar, ["Easy", "Normal"], "Normal")

        self.sizeVar = StringVar(self.top)
        self.addMenu("Board size", self.sizeVar, ["Small", "Normal", "Large", "Extra Large"], "Normal")

        self.diagonalVar = StringVar(self.top)
        self.addMenu("Diagonal moves", self.diagonalVar, ["Yes", "No"], "No")

        self.top.rowconfigure(0, weight=1)
        self.top.columnconfigure(5, weight=1)

    def startGame(self):
        """Start the main interface with the options chosen in the launcher, and close the launcher window"""
        pygame.mixer.music.stop()
        self.top.destroy()

        Application(self.root, self.blueBrainVar.get(), self.difficultyVar.get(),
                    self.sizeVar.get(), self.diagonalVar.get())
        self.root.update()
        self.root.deiconify()

    def loadGame(self):
        """Load a game and close the launcher"""
        pygame.mixer.music.stop()
        self.top.destroy()
        app = Application(self.root, self.blueBrainVar.get(), self.difficultyVar.get(),
                    self.sizeVar.get(), self.diagonalVar.get())
        app.loadGame()
        self.root.update()
        self.root.deiconify()

    def newBackground(self):
        """Keep replacing the background image randomly at a set interval, forever"""
        self.bgcanvas.delete(self.bgid)
        self.bgcanvas.delete(self.textid)
        i = str(randint(1, self.backgrounds))
        im = Image.open("backgrounds/background" + i + ".jpg").resize((900, 600))
        self.bgim = ImageTk.PhotoImage(im)
        self.bgid = self.bgcanvas.create_image(0, 0, image=self.bgim, anchor=NW)
        self.textid = self.bgcanvas.create_text((200, 80), text=GAME_NAME, font=LAUNCHER_TITLE_FONT, underline=9)
        self.bgcanvas.create_text((200, 142), text=AUTHORS, font=LAUNCHER_AUTHOR_FONT)
        self.top.after(10000, self.newBackground)

    def playMusic(self):
        """Play songs from the music directory"""
        tracks = [x for x in os.listdir(MUSIC_DIR) if "mp3" in x ]
        track = choice(tracks)
        pygame.mixer.music.load(os.path.join(MUSIC_DIR, track))
        pygame.mixer.music.play()
        print("Playing music {}".format(os.path.join(MUSIC_DIR, track)))

    def addMenu(self, labeltext, var, options, default):
        """Add an OptionMenu (in Python 2.6's Tkinter) or a ttk Combobox (in Python 2.7)
        to the launcher interface"""
        var.set(default)
        lbl = Label(self.top, text=labeltext, anchor=E, width=10)

        if py26:
            menu = OptionMenu(self.top, var, *options)
        else:
            menu = Combobox(self.top, textvariable=var, state="readonly")
            menu['values'] = options

        labelcolumn = 1 + 2 * (Launcher.menus / 2)
        lbl.grid(column=int(labelcolumn), row=1 + Launcher.menus % 2, ipadx=6, ipady=2)
        menu.grid(column=int(labelcolumn) + 1, row=1 + Launcher.menus % 2, padx=6)

        Launcher.menus += 1

    def exit(self, event=None):
        """End the program!"""
        self.root.quit()
        self.blueBrainVar.get()

if __name__ == "__main__":
    pygame.mixer.init(48000, -16, 1, 102400)
    root = Tk()
    root.withdraw()
    Launcher(root)
    root.title("%s %s" % (GAME_NAME, VERSION))
    setIcon(root, "flag")
    root.mainloop() 
    pygame.mixer.quit()
