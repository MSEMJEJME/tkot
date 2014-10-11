## This file contains some of the options that can be changed to customize
## your Ren'Py game. It only contains the most common options... there
## is quite a bit more customization you can do.
##
## Lines beginning with two '#' marks are comments, and you shouldn't
## uncomment them. Lines beginning with a single '#' mark are
## commented-out code, and you may want to uncomment them when
## appropriate.

init -1 python hide:

    ## Should we enable the use of developer tools? This should be
    ## set to False before the game is released, so the user can't
    ## cheat using developer tools.

    config.developer = False

    ## These control the width and height of the screen.

    config.screen_width = 800
    config.screen_height = 600
    config.main_menu_music = "titlecard.ogg"

    ## This controls the title of the window, when Ren'Py is
    ## running in a window.

    config.window_title = u" .The Knife of the Traitor."

    # These control the name and version of the game, that are reported
    # with tracebacks and other debugging logs.
    config.name = "A Ren'Py Game"
    config.version = "0.0"

    #########################################
    # Themes
    
    ## We then want to call a theme function. themes.roundrect is
    ## a theme that features the use of rounded rectangles. It's
    ## the only theme we currently support.
    ##
    ## The theme function takes a number of parameters that can
    ## customize the color scheme.

    theme.tv(
        # Color scheme: City Lights
                                    
        ## The color of an idle widget face.
        widget = "#45ada8",

        ## The color of a focused widget face.
        widget_hover = "#2e5860",

        ## The color of the text in a widget.
        widget_text = "#9de0ad",

        ## The color of the text in a selected widget. (For
        ## example, the current value of a preference.)
        widget_selected = "#e5fcc2",

        ## The color of a disabled widget face. 
        disabled = "#638e89",

        ## The color of disabled widget text.
        disabled_text = "#594f4f",

        ## The color of informational labels.
        label = "#e5fcc2",

        ## The color of a frame containing widgets.
        frame = "#547980",

        ## The background of the main menu. This can be a color
        ## beginning with '#', or an image filename. The latter
        ## should take up the full height and width of the screen.
        mm_root = "#000000",

        ## The background of the game menu. This can be a color
        ## beginning with '#', or an image filename. The latter
        ## should take up the full height and width of the screen.
        gm_root = "go.png",

        ## If this is True, the in-game window is rounded. If False,
        ## the in-game window is square.
        rounded_window = False,

        ## And we're done with the theme. The theme will customize
        ## various styles, so if we want to change them, we should
        ## do so below.            
        )


    #########################################
    ## These settings let you customize the window containing the
    ## dialogue and narration, by replacing it with an image.

    ## The background of the window. In a Frame, the two numbers
    ## are the size of the left/right and top/bottom borders,
    ## respectively.

    style.window.background = Frame("frame.png", 12, 12)

    ## Margin is space surrounding the window, where the background
    ## is not drawn.

    # style.window.left_margin = 6
    # style.window.right_margin = 6
    # style.window.top_margin = 6
    # style.window.bottom_margin = 6

    ## Padding is space inside the window, where the background is
    ## drawn.

    # style.window.left_padding = 6
    # style.window.right_padding = 6
    # style.window.top_padding = 6
    # style.window.bottom_padding = 6

    ## This is the minimum height of the window, including the margins
    ## and padding.

    # style.window.yminimum = 250


    #########################################
    ## This lets you change the placement of the main menu.

    ## The way placement works is that we find an anchor point
    ## inside a displayable, and a position (pos) point on the
    ## screen. We then place the displayable so the two points are
    ## at the same place.

    ## An anchor/pos can be given as an integer or a floating point
    ## number. If an integer, the number is interpreted as a number
    ## of pixels from the upper-left corner. If a floating point,
    ## the number is interpreted as a fraction of the size of the
    ## displayable or screen.

    # style.mm_menu_frame.xpos = 0.5
    # style.mm_menu_frame.xanchor = 0.5
    # style.mm_menu_frame.ypos = 0.75
    # style.mm_menu_frame.yanchor = 0.5


    #########################################
    ## These let you customize the default font used for text in Ren'Py.

    ## The file containing the default font.

    style.default.font = "bluehigh.ttf"

    ## The default size of text.

    style.default.size = 22

    ## Note that these only change the size of some of the text. Other
    ## buttons have their own styles.


    #########################################
    ## These settings let you change some of the sounds that are used by
    ## Ren'Py.

    ## Set this to False if the game does not have any sound effects.
    config.window_icon = "icon.png"

    config.has_sound = True

    ## Set this to False if the game does not have any music.

    config.has_music = True

    ## Set this to False if the game does not have voicing.

    config.has_voice = True

    ## Sounds that are used when button and imagemaps are clickied.

    style.button.activate_sound = "click.ogg"
    style.imagemap.activate_sound = "click.ogg"

    ## Sounds that are used when entering and exiting the game menu.

    config.enter_sound = "click.ogg"
    config.exit_sound = "click.ogg"

    ## A sample sound that can be played to check the sound volume.

    config.sample_sound = "karasu1.mp3"

    ## Music that is played while the user is at the main menu.

    # config.main_menu_music = "main_menu_theme.ogg"


    #########################################
    ## Help.

    ## This lets you configure the help option on the Ren'Py menus.
    ## It may be:
    ## - A label in the script, in which case that label is called to
    ##   show help to the user.
    ## - A file name relative to the base directory, which is opened in a
    ##   web browser.
    ## - None, to disable help.   
    config.help = "README.html"


    #########################################
    ## Transitions.

    ## Used when entering the game menu from the game.
    config.enter_transition = dissolve

    ## Used when exiting the game menu to the game.
    config.exit_transition = dissolve

    ## Used between screens of the game menu.
    config.intra_transition = dissolve

    ## Used when entering the game menu from the main menu.
    config.main_game_transition = dissolve

    ## Used when returning to the main menu from the game.
    config.game_main_transition = dissolve

    ## Used when entering the main menu from the splashscreen.
    config.end_splash_transition = dissolve

    ## Used when entering the main menu after the game has ended.
    config.end_game_transition = dissolve

    ## Used when a game is loaded.
    config.after_load_transition = dissolve

    ## Used when the window is shown.
    config.window_show_transition = None

    ## Used when the window is hidden.
    config.window_hide_transition = None


    #########################################
    ## This is the name of the directory where the game's data is
    ## stored. (It needs to be set early, before any other init code
    ## is run, so the persisten information can be found by the init code.)
python early:
    config.save_directory = "nanoos-1330649449"

init -1 python hide:
    #########################################
    ## Default values of Preferences.

    ## Note: These options are only evaluated the first time a
    ## game is run. To have them run a second time, delete
    ## game/saves/persistent

    ## Should we start in fullscreen mode?

    config.default_fullscreen = False

    ## The default text speed in characters per second. 0 is infinite.

    config.default_text_cps = 0

    #########################################
    ## More customizations can go here.
init python:
    
   # Step 1. Create a MusicRoom instance.
   mr = MusicRoom(fadeout=1.0)
    
    # Step 2. Add music files.
   mr.add("titlecard.ogg", always_unlocked=True)
   mr.add("vosges_theme.ogg", always_unlocked=True)
   mr.add("gervase_theme.ogg", always_unlocked=True)
   mr.add("lilja_theme.ogg", always_unlocked=True)
   mr.add("intro_theme.ogg", always_unlocked=True)
   mr.add("oscorvus_theme.ogg", always_unlocked=True)
   mr.add("v_end.ogg", always_unlocked=True)
   mr.add("ger_end.ogg", always_unlocked=True)
   mr.add("cor_theme.ogg", always_unlocked=True)
   mr.add("g_end.ogg", always_unlocked=True)
   mr.add("b_end.ogg", always_unlocked=True)
   mr.add("ecc_theme.ogg", always_unlocked=True)
   
   
   config.main_menu = [
        (u"New Game", "start", "True"),
        (u"Continue", _intra_jumps("load_screen", "main_game_transition"), "True"),
        (u"Options", _intra_jumps("preferences_screen", "main_game_transition"), "True"),
        (u"Quit", ui.jumps("_quit"), "True")
        ]
    
   style.hotspot.activate_sound = "click.ogg"
    
   config.imagemap_cache = False
    
   ##Modifies the Menu Choice's BG
   style.menu_choice_button.background = Frame("choice_bg_idle.png",28,9)
   style.menu_choice_button.hover_background = Frame("choice_bg_hover.png",28,9)
   # style.name_button.selected_background = Frame("choice_bg_idle.jpg",28,9)
   # style.name_button.selected_hover_background = Frame("choice_bg_idle.jpg",28,9)
   # style.name_button.insensitive_background = Frame("choice_bg_idle.jpg",28,9)
   style.menu_choice_button.yminimum = 60
   style.menu_choice_button.xminimum = 400
    
   ##Modifies the Menu Choice's Text
   style.menu_choice.color = "#fff"
   style.menu_choice.size = 18
   style.menu_choice.outlines = [(2, "#1e8797", 0, 0)]
   style.menu_choice.hover_color = "#fff"
   style.menu_choice.hover_outlines = [(2, "#0cc7bc", 0, 0)]
    
   style.file_picker_button.color = "#9bdf31"
    
    ###Modifies the Universal styles
    ####I did not edit the Save/Load menu, but notice what does changes if I set the parent style, and what doesn't change because the child style is defined elsewhere.
    
    #All frames
   style.frame.background = Frame("menu/frame.png",10,10)
    
    #All buttons
   style.button.background = Frame("menu/button_idle.png",10,10)
   style.button.hover_background = Frame("menu/button_hover.png",10,10)
   style.button.selected_background = Frame("menu/button_selected.png",10,10)
   style.button.selected_hover_background = Frame("menu/button_hover.png",10,10)
   style.button.yminimum = 40
    
   style.button_text.color = "#fff"
   style.button_text.size = 14

    #All text
   style.default.color = "#f1f5ee"
   style.default.size = 20
   style.default.font = "bluehigh.ttf"
   style.default.outlines = [(2, "#1f1e26", 0, 0)]
   style.default.hover_outlines = [(2, "#548000", 0, 0)]
   style.default.selected_outlines = [(2, "#1e8797", 0, 0)]
   style.default.selected_hover_outlines = [(2, "#0cc7bc", 0, 0)]

    ##This will change the save/load slots.
   style.large_button.background = Frame("menu/button_idle.png",10,10)
   style.large_button.hover_background = Frame("menu/button_hover.png",10,10)
   style.large_button.selected_background = Frame("menu/button_selected.png",10,10)
   style.large_button.selected_hover_background = Frame("menu/button_hover.png",10,10)
   style.large_button.yminimum = 65
   style.large_button.ypadding = 10
    
    #Change the screenshot for saves
   config.thumbnail_width = 68
   config.thumbnail_height = 51
    
