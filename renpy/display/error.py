# Copyright 2004-2012 Tom Rothamel <pytom@bishoujo.us>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# This file contains code to handle GUI-based error reporting.

import renpy.display
import os

##############################################################################
# Initialized approach.

def call_exception_screen(screen_name, **kwargs):
    try:

        old_quit = renpy.config.quit_action
        renpy.config.quit_action = renpy.exports.quit

        for i in renpy.config.layers:
            renpy.game.context().scene_lists.clear(i)
    
        renpy.exports.show_screen(screen_name, _transient=True, **kwargs)
        return renpy.ui.interact(mouse="screen", type="screen", suppress_overlay=True, suppress_underlay=True)

    finally:
        renpy.config.quit_action = old_quit

def rollback_action():
    renpy.exports.rollback(force=True)
    
def init_display():
    """
    The minimum amount of code required to init the display.
    """

    if not renpy.game.interface:
        renpy.display.core.Interface()
        renpy.style.build_styles()
        renpy.loader.index_archives()
        renpy.display.im.cache.init()

    renpy.ui.reset()
        
def report_exception(short, full):
    """
    Reports an exception to the user. Returns True if the exception should
    be raised by the normal reporting mechanisms. Otherwise, should raise
    the appropriate exception to cause a reload or quit or rollback.
    """

    if "RENPY_SIMPLE_EXCEPTIONS" in os.environ:
        return True
       
    if not renpy.exports.has_screen("_exception"):
        return True
    
    try:
        init_display()    
    except:
        return True
    
    if renpy.display.draw is None:
        return True
    
    ignore_action = None
    rollback_action = None
    reload_action = None

    try:    
        if not renpy.game.context().init_phase:
            rollback_action = renpy.display.error.rollback_action
            reload_action = renpy.exports.curried_call_in_new_context("_save_reload_game")

        if renpy.game.context(-1).next_node is not None:
            ignore_action = renpy.ui.returns(False)
    except:
        pass     
     
    renpy.game.invoke_in_new_context(
        call_exception_screen,
        "_exception", 
        short=short, full=full, 
        rollback_action=rollback_action,
        reload_action=reload_action,
        ignore_action=ignore_action,
        )
        

def report_parse_errors(errors):
    """
    Reports an exception to the user. Returns True if the exception should
    be raised by the normal reporting mechanisms. Otherwise, should raise
    the appropriate exception.
    """

    if "RENPY_SIMPLE_EXCEPTIONS" in os.environ:
        return True
       
    if not renpy.exports.has_screen("_parse_errors"):
        return True
    
    init_display()    
          
    reload_action = renpy.exports.utter_restart
     
    renpy.game.invoke_in_new_context(
        call_exception_screen,
        "_parse_errors",
        reload_action=reload_action,
        errors=errors,
        )

