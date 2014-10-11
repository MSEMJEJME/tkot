# This file is in the public domain. Feel free to modify it as a basis
# for your own screens.

##############################################################################
# Say
#
# Screen that's used to display adv-mode dialogue.
# http://www.renpy.org/doc/html/screen_special.html#say
screen say:

    # Defaults for side_image and two_window
    default side_image = None
    default two_window = False

    # Decide if we want to use the one-window or two-window varaint.
    if not two_window:

        # The one window variant.        
        window:
            id "window"

            has vbox:
                style "say_vbox"

            if who:
                text who id "who"

            text what id "what"

    else:

        # The two window variant.
        vbox:
            style "say_two_window_vbox"

            if who:            
                window:
                    style "say_who_window"

                    text who:
                        id "who"
                        
            window:
                id "window"

                has vbox:
                    style "say_vbox"

                text what id "what"
              
    # If there's a side image, display it above the text.
    if side_image:
        add side_image
    else:
        add SideImage() xalign 0.0 yalign 1.0

    # Use the quick menu.
    use quick_menu


##############################################################################
# Choice
#
# Screen that's used to display in-game menus.
# http://www.renpy.org/doc/html/screen_special.html#choice

screen choice:

    window: 
        style "menu_window"        
        xalign 0.5
        yalign 0.5
        
        vbox:
            style "menu"
            spacing 2
            
            for caption, action, chosen in items:
                
                if action:  
                    
                    button:
                        action action
                        style "menu_choice_button"                        

                        text caption style "menu_choice"
                    
                else:
                    text caption style "menu_caption"

init -2 python:
    config.narrator_menu = True
    
    style.menu_window.set_parent(style.default)
    style.menu_choice.set_parent(style.button_text)
    style.menu_choice.clear()
    style.menu_choice_button.set_parent(style.button)
    style.menu_choice_button.xminimum = int(config.screen_width * 0.75)
    style.menu_choice_button.xmaximum = int(config.screen_width * 0.75)


##############################################################################
# Input
#
# Screen that's used to display renpy.input()
# http://www.renpy.org/doc/html/screen_special.html#input

screen input:

    window:
        has vbox

        text prompt
        input id "input"

    use quick_menu
        
##############################################################################
# Nvl
#
# Screen used for nvl-mode dialogue and menus.
# http://www.renpy.org/doc/html/screen_special.html#nvl

screen nvl:

    window:
        style "nvl_window"

        has vbox:
            style "nvl_vbox"

        # Display dialogue.
        for who, what, who_id, what_id, window_id in dialogue:
            window:
                id window_id

                has hbox:
                    spacing 10

                if who is not None:
                    text who id who_id

                text what id what_id

        # Display a menu, if given.
        if items:

            vbox:
                id "menu"

                for caption, action, chosen in items:

                    if action:

                        button:
                            style "nvl_menu_choice_button"
                            action action

                            text caption style "nvl_menu_choice"

                    else:

                        text caption style "nvl_dialogue"

    add SideImage() xalign 0.0 yalign 1.0
    
    use quick_menu
        
##############################################################################
# Main Menu 
#
# Screen that's used to display the main menu, when Ren'Py first starts
# http://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu:

    # This ensures that any other menu screen is replaced.
    tag menu
    if persistent.ending == "Ending 1":
        use main_menu_1
    elif persistent.ending == "Ending 2":
        use main_menu_2
    elif persistent.ending == "Ending 3":
        use main_menu_3
    elif persistent.ending == "Ending 4":
        use main_menu_4
    else:
        use main_menu_default
        
screen main_menu_default:
        
    imagemap:
        ground "main_menu_idle.jpg"
        hover "main_menu_hover.png"
        
        hotspot (31,539,107,44) action Start()
        hotspot (150,539,122,44) action ShowMenu("load")
        #hotspot (291,539,107,44) action ShowMenu("gallery")
        #hotspot (418,539,107,44) action ShowMenu("MusicRoom")
        hotspot (552,539,107,44) action ShowMenu("preferences")
        hotspot (671,539,107,44) action Quit(confirm=False)
        
screen main_menu_1:
    tag menu
    window:
        style "mm_root"

    imagemap:
        ground 'main_menu_v_idle.jpg'
        hover 'main_menu_v_hover.png'
       
        hotspot (31,539,107,44) action Start()
        hotspot (150,539,122,44) action ShowMenu("load")
        hotspot (291,539,107,44) action ShowMenu("gallery")
        hotspot (418,539,107,44) action ShowMenu("music_room")
        hotspot (552,539,107,44) action ShowMenu("preferences")
        hotspot (671,539,107,44) action Quit(confirm=False)   
screen main_menu_2:
    tag menu
    window:
        style "mm_root"

    imagemap:
        ground 'main_menu_g_idle.jpg'
        hover 'main_menu_g_hover.png'
       
        hotspot (31,539,107,44) action Start()
        hotspot (150,539,122,44) action ShowMenu("load")
        hotspot (291,539,107,44) action ShowMenu("gallery")
        hotspot (418,539,107,44) action ShowMenu("music_room")
        hotspot (552,539,107,44) action ShowMenu("preferences")
        hotspot (671,539,107,44) action Quit(confirm=False)
        
screen main_menu_3:
    tag menu
    window:
        style "mm_root"

    imagemap:
        ground 'main_menu_l_idle.jpg'
        hover 'main_menu_l_hover.png'
       
        hotspot (31,539,107,44) action Start()
        hotspot (150,539,122,44) action ShowMenu("load")
        hotspot (291,539,107,44) action ShowMenu("gallery")
        hotspot (418,539,107,44) action ShowMenu("music_room")
        hotspot (552,539,107,44) action ShowMenu("preferences")
        hotspot (671,539,107,44) action Quit(confirm=False)

screen main_menu_4:
    tag menu
    window:
        style "mm_root"

    imagemap:
        ground 'main_menu_c_idle.jpg'
        hover 'main_menu_c_hover.png'
       
        hotspot (31,539,107,44) action Start()
        hotspot (150,539,122,44) action ShowMenu("load")
        hotspot (291,539,107,44) action ShowMenu("gallery")
        hotspot (418,539,107,44) action ShowMenu("music_room")
        hotspot (552,539,107,44) action ShowMenu("preferences")
        hotspot (671,539,107,44) action Quit(confirm=False)

init -2 python:

    # Make all the main menu buttons be the same size.
    style.mm_button.size_group = "mm"


##############################################################################
# Navigation
#
# Screen that's included in other screens to display the game menu
# navigation and background.
# http://www.renpy.org/doc/html/screen_special.html#navigation
screen navigation:

    # The background of the game menu.
    window:
        style "gm_root"

    # The various buttons.
    imagemap:
        auto "menu/navigation_%s.png"
        # ground "menu/navigation_ground.png"
        # idle "menu/navigation_idle.png"
        # hover "menu/navigation_selected.png"
        # selected_idle "menu/navigation_selected_idle.png"
        # selected_hover "menu/navigation_selected_hover.png"
        
        hotspot (31,555,119,34) action Return()
        hotspot (155,555,119,34) action ShowMenu("save")
        hotspot (279,555,119,34) action ShowMenu("load")
        hotspot (403,555,119,34) action ShowMenu("preferences")
        hotspot (527,555,119,34) action MainMenu()
        hotspot (651,555,119,34) action Quit()

init -2 python:
    style.gm_nav_button.size_group = "gm_nav"
    
    

##############################################################################
# Save, Load
#
# Screens that allow the user to save and load the game.
# http://www.renpy.org/doc/html/screen_special.html#save
# http://www.renpy.org/doc/html/screen_special.html#load

# Since saving and loading are so similar, we combine them into
# a single screen, file_picker. We then use the file_picker screen
# from simple load and save screens.
    
screen file_picker:

    frame:
        style "file_picker_frame"

        has vbox

        # The buttons at the top allow the user to pick a
        # page of files.
        hbox:
            style_group "file_picker_nav"
            
            textbutton _("Previous"):
                action FilePagePrevious()

            textbutton _("Auto"):
                action FilePage("auto")

            textbutton _("Quick"):
                action FilePage("quick")

            for i in range(1, 9):
                textbutton str(i):
                    action FilePage(i)
                    
            textbutton _("Next"):
                action FilePageNext()

        $ columns = 2
        $ rows = 5
                
        # Display a grid of file slots.
        grid columns rows:
            transpose True
            xfill True
            style_group "file_picker"
            
            # Display ten file slots, numbered 1 - 10.
            for i in range(1, columns * rows + 1):

                # Each file slot is a button.
                button:
                    action FileAction(i)
                    xfill True

                    has hbox

                    # Add the screenshot.
                    add FileScreenshot(i)
                    
                    # Format the description, and add it as text.
                    $ description = "% 2s. %s\n%s" % (
                        FileSlotName(i, columns * rows),
                        FileTime(i, empty=_("Empty Slot.")),
                        FileSaveName(i))

                    text description

                    key "save_delete" action FileDelete(i)
                    
                    
screen save:

    # This ensures that any other menu screen is replaced.
    tag menu

    use navigation
    use file_picker

screen load:

    # This ensures that any other menu screen is replaced.
    tag menu

    use navigation
    use file_picker

init -2 python:
    style.file_picker_frame = Style(style.menu_frame)

    style.file_picker_nav_button = Style(style.small_button)
    style.file_picker_nav_button_text = Style(style.small_button_text)

    style.file_picker_button = Style(style.large_button)
    style.file_picker_text = Style(style.large_button_text)

    

##############################################################################
# Preferences
#
# Screen that allows the user to change the preferences.
# http://www.renpy.org/doc/html/screen_special.html#prefereces
    
screen preferences:

    tag menu

      # Include the navigation.
    use navigation

    # Put the navigation columns in a three-wide grid.
    grid 3 1:
        style_group "prefs"
        xfill True

        # The left column.
        vbox:
            frame:
                style_group "pref"
                has vbox

                label _("Display")
                textbutton _("Window") action Preference("display", "window")
                textbutton _("Fullscreen") action Preference("display", "fullscreen")

            frame:
                style_group "pref"
                has vbox

                label _("Transitions")
                textbutton _("All") action Preference("transitions", "all")
                textbutton _("None") action Preference("transitions", "none")

            frame:
                style_group "pref"
                has vbox

                label _("Text Speed")
                bar value Preference("text speed")

            frame:
                style_group "pref"
                has vbox

                textbutton _("Joystick...") action ShowMenu("joystick_preferences")

        vbox:
            frame:
                style_group "pref"
                has vbox

                label _("Skip")
                textbutton _("Seen Messages") action Preference("skip", "seen")
                textbutton _("All Messages") action Preference("skip", "all")

            frame:
                style_group "pref"
                has vbox

                textbutton _("Begin Skipping") action Skip()

            frame:
                style_group "pref"
                has vbox

                label _("After Choices")
                textbutton _("Stop Skipping") action Preference("after choices", "stop")
                textbutton _("Keep Skipping") action Preference("after choices", "skip")

            frame:
                style_group "pref"
                has vbox

                label _("Auto-Forward Time")
                bar value Preference("auto-forward time")

        vbox:
            frame:
                style_group "pref"
                has vbox

                label _("Music Volume")
                bar value Preference("music volume")

            frame:
                style_group "pref"
                has vbox

                label _("Sound Volume")
                bar value Preference("sound volume")

                if config.sample_sound:
                    textbutton "Test":
                        action Play("sound", config.sample_sound)
                        style "soundtest_button"

            frame:
                style_group "pref"
                has vbox

                label _("Voice Volume")
                bar value Preference("voice volume")

                if config.sample_voice:
                    textbutton "Test":
                        action Play("voice", config.sample_voice)
                        style "soundtest_button"

init -2 python:
    style.pref_frame.xfill = True
    style.pref_frame.xmargin = 5
    style.pref_frame.top_margin = 5

    style.pref_vbox.xfill = True

    style.pref_button.size_group = "pref"
    style.pref_button.xalign = 0.5

    style.pref_slider.xmaximum = 192
    style.pref_slider.xalign = 0.5

    style.soundtest_button.xalign = 1.0
    
    style.pref_button.background = Frame("menu/button_idle.png",10,10)
    style.pref_button.hover_background = Frame("menu/button_hover.png",40,10)
    style.pref_button.selected_background = Frame("menu/button_selected.png",10,10)
    style.pref_button.selected_hover_background = Frame("menu/button_hover.png",10,10)
    style.pref_button.yminimum = 40
    
    style.pref_button_text.color = "#fff"
    style.pref_button_text.size = 14
    style.pref_button_text.font = "bluehigh.ttf"
    style.pref_button_text.outlines = [(2, "#3f603e", 0, 0)]
    style.pref_button_text.hover_outlines = [(2, "#6a6b03", 0, 0)]
    style.pref_button_text.selected_outlines = [(2, "#742567", 0, 0)]
    style.pref_button_text.selected_hover_outlines = [(2, "#6a6b03", 0, 0)]
    
    style.pref_label.xalign = 0.5
    style.pref_label_text.color = "#fff"
    style.pref_label_text.outlines = [(2, "#742567", 0, 0)]
    
    style.pref_frame.background = Frame("menu/frame.png",10,10)
    
    style.pref_slider.left_bar = "menu/bar_full.png"
    style.pref_slider.right_bar = "menu/bar_empty.png"
    style.pref_slider.hover_left_bar = "menu/bar_hover.png"
    style.pref_slider.ymaximum = 29
    style.pref_slider.xmaximum = 197
    
    style.pref_slider.thumb = "menu/thumb.png"
    style.pref_slider.thumb_offset = 6
    style.pref_slider.thumb_shadow = None


##############################################################################
# Yes/No Prompt
#
# Screen that asks the user a yes or no question.
# http://www.renpy.org/doc/html/screen_special.html#yesno-prompt
    
screen yesno_prompt:

    modal True

    window:
        style "gm_root"

    frame:
        style_group "yesno"

        xfill True
        xmargin .05
        ypos .1
        yanchor 0
        ypadding .05
        
        has vbox:
            xalign .5
            yalign .5
            spacing 30
            
        label _(message):
            xalign 0.5

        hbox:
            xalign 0.5
            spacing 100
            
            textbutton _("Yes") action yes_action
            textbutton _("No") action no_action


init -2 python:    
    style.yesno_button.size_group = "yesno"
    style.yesno_label_text.text_align = 0.5


##############################################################################
# Quick Menu
#
# A screen that's included by the default say screen, and adds quick access to
# several useful functions.
screen quick_menu:

    # Add an in-game quick menu.
    hbox:
        style_group "quick"
    
        xalign 1.0
        yalign 1.0

        textbutton _("Q.Save") action QuickSave()
        textbutton _("Q.Load") action QuickLoad()
        textbutton _("Save") action ShowMenu('save')
        textbutton _("Skip") action Skip()
        textbutton _("Auto") action Preference("auto-forward", "toggle")
        textbutton _("Prefs") action ShowMenu('preferences')
        
init -2 python:
    style.quick_button.set_parent('default')
    style.quick_button.background = None
    style.quick_button.xpadding = 5

    style.quick_button_text.set_parent('default')
    style.quick_button_text.size = 12
    style.quick_button_text.idle_color = "#8888"
    style.quick_button_text.hover_color = "#ccc"
    style.quick_button_text.selected_idle_color = "#cc08"
    style.quick_button_text.selected_hover_color = "#cc0"
    style.quick_button_text.insensitive_color = "#4448"
    
    # Set a default value for the auto-forward time, and note that AFM is
    # turned off by default.
    config.default_afm_time = 10
    config.default_afm_enable = False
    
    
    
    
screen music_room:

    tag menu
    window:
        background "cgmenu02.png"

    imagebutton: #I need a way to get back to the main menu
        action Return()
        idle "11.png"
        hover "22.png"
        xanchor 195 yanchor 0
        xpos 400 ypos 0               
                        
    frame: #these positioning changes depending on your layout
        xpos 444
        ypos 0
        has vbox:
            xalign 0.5 
            yalign 0.5

        # The buttons that play each track.
        textbutton "(Titlecard bgm) 'Two warriors' by Coova and little scale" action mr.Play("titlecard.ogg")
        textbutton "(Vosges Theme) 'Standing Alone' by Coova and little scale" action mr.Play("vosges_theme.ogg")
        textbutton "(Gervase Theme) 'Autumn' by Coova and little scale" action mr.Play("gervase_theme.ogg")
        textbutton "(Lilja Theme) 'Time is running 'by Coova and little scale" action mr.Play("lilja_theme.ogg")
        textbutton "(Fooling Around) 'Cyboshellfish' by Animal Style" action mr.Play("intro_theme.ogg")
        textbutton "(Confessions) 'Tension' by Rushjet1" action mr.Play("oscorvus_theme.ogg")
        textbutton "(Vosges End Theme) 'Story of the constellations' by Rushjet1" action mr.Play("v_end.ogg")
        textbutton "(Gervase End Theme) 'Try' by Virt" action mr.Play("ger_end.ogg")
        textbutton "(Corvus End Theme) 'Unknown sector' by Rushjet1" action mr.Play("cor_theme.ogg")
        textbutton "(Good Ending) 'zzzzz' by Kplecraft" action mr.Play("g_end.ogg")
        textbutton "(Bad Ending) 'Warming up' by Saskrotch" action mr.Play("b_end.ogg")
        textbutton "(Ecchin Theme) 'Antibiotics Bitch' by Animal Style" action mr.Play("ecc_theme.ogg")

        null height 20

        # Buttons that let us advance tracks.
        textbutton "Next" action mr.Next()
        textbutton "Previous" action mr.Previous()

        null height 20

        # The button that lets the user exit the music room.
        textbutton "Main Menu" action ShowMenu("main_menu")

    # Start the music playing on entry to the music room.
    on "replace" action mr.Play()

    # Restore the main menu music upon leaving.
    on "replaced" action Play("music", "track1.ogg")
    
