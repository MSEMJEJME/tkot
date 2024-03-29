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

# This file contains code for initializing and managing the display
# window.

import renpy.display
import renpy.audio
import renpy.text

import pygame #@UnusedImport

import sys
import os
import time
import cStringIO
import threading

try:
    import pygame.macosx
except:
    pass

try:
    import android #@UnresolvedImport @UnusedImport
    import android.sound #@UnresolvedImport
except:
    android = None

# Is the cpu idle enough to do other things?
cpu_idle = threading.Event()
cpu_idle.clear()

# Need to be +4, so we don't interfere with FFMPEG's events.
TIMEEVENT = pygame.USEREVENT + 4
PERIODIC = pygame.USEREVENT + 5
JOYEVENT = pygame.USEREVENT + 6
REDRAW = pygame.USEREVENT + 7

# All events except for TIMEEVENT and REDRAW
ALL_EVENTS = [ i for i in range(0, REDRAW + 1) if i != TIMEEVENT and i != REDRAW ]

# The number of msec between periodic events.
PERIODIC_INTERVAL = 50

# Time management.
time_base = None

def init_time():
    global time_base
    time_base = time.time() - pygame.time.get_ticks() / 1000.0

def get_time():
    return time_base + pygame.time.get_ticks() / 1000.0


def displayable_by_tag(layer, tag):
    """
    Get the displayable on the given layer with the given tag.
    """

    return renpy.game.context().scene_lists.get_displayable_by_tag(layer, tag)
    
class IgnoreEvent(Exception):
    """
    Exception that is raised when we want to ignore an event, but
    also don't want to return anything.
    """

    pass

class absolute(float):
    """
    This represents an absolute float coordinate.
    """
    __slots__ = [ ]


class Displayable(renpy.object.Object):
    """
    The base class for every object in Ren'Py that can be
    displayed to the screen.

    Drawables will be serialized to a savegame file. Therefore, they
    shouldn't store non-serializable things (like pygame surfaces) in
    their fields.
    """

    # Some invariants about method call order:
    #
    # per_interact is called before render.
    # render is called before event.
    #
    # get_placement can be called at any time, so can't
    # assume anything.
    
    activated = False
    focusable = False
    full_focus_name = None
    role = ''

    # The event we'll pass on to our parent transform.
    transform_event = None

    # Can we change our look in response to transform_events?
    transform_event_responder = False
    
    def __init__(self, focus=None, default=False, style='default', **properties): # W0231
        self.style = renpy.style.Style(style, properties, heavy=True)
        self.focus_name = focus
        self.default = default

    def find_focusable(self, callback, focus_name):

        focus_name = self.focus_name or focus_name
        
        if self.focusable:
            callback(self, focus_name)

        for i in self.visit():
            if i is None:
                continue

            i.find_focusable(callback, focus_name)

            
    def focus(self, default=False):
        """
        Called to indicate that this widget has the focus.
        """

        if not self.activated:
            self.set_style_prefix(self.role + "hover_", True)
        
        if not default and not self.activated:
            if self.style.sound:
                renpy.audio.music.play(self.style.sound, channel="sound")

    def unfocus(self, default=False):
        """
        Called to indicate that this widget has become unfocused.
        """

        if not self.activated:
            self.set_style_prefix(self.role + "idle_", True)

    def is_focused(self):

        if renpy.display.focus.grab and renpy.display.focus.grab is not self:
            return

        return renpy.game.context().scene_lists.focused is self

    def set_style_prefix(self, prefix, root):
        """
        Called to set the style prefix of this widget and its child
        widgets, if any.

        `root` - True if this is the root of a style tree, False if this
        has been passed on to a child.
        """

        if prefix == self.style.prefix:
            return
        
        self.style.set_prefix(prefix)
        renpy.display.render.redraw(self, 0)

    def parameterize(self, name, parameters):
        """
        Called to parameterize this. By default, we don't take any
        parameters.
        """

        if parameters:
            raise Exception("Image '%s' can't take parameters '%s'. (Perhaps you got the name wrong?)" %
                            (' '.join(name), ' '.join(parameters)))

        return self

    def render(self, width, height, st, at):
        """
        Called to display this displayable. This is called with width
        and height parameters, which give the largest width and height
        that this drawable can be drawn to without overflowing some
        bounding box. It's also given two times. It returns a Surface
        that is the current image of this drawable. 
 
        @param st: The time since this widget was first shown, in seconds.
        @param at: The time since a similarly named widget was first shown,
        in seconds.        
        """

        assert False, "Draw not implemented."

    def event(self, ev, x, y, st):
        """
        Called to report than an event has occured. Ev is the raw
        pygame event object representing that event. If the event
        involves the mouse, x and y are the translation of the event
        into the coordinates of this displayable. st is the time this
        widget has been shown for.

        @returns A value that should be returned from Interact, or None if
        no value is appropriate.
        """

        return None

    def get_placement(self):
        """
        Returns a style object containing placement information for
        this Displayable. Children are expected to overload this
        to return something more sensible.
        """

        return self.style.get_placement()
    
    def visit_all(self, callback):
        """
        Calls the callback on this displayable and all children of this
        displayable.
        """

        for d in self.visit():
            if not d:
                continue
            d.visit_all(callback)

        callback(self)
        
    def visit(self):
        """
        Called to ask the displayable to return a list of its children
        (including children taken from styles). For convenience, this
        list may also include None values.
        """

        return [ ]

    def per_interact(self):
        """
        Called once per widget per interaction.
        """

        return None

    def predict_one(self):
        """
        Called to ask this displayable to call the callback with all
        the images it may want to load.
        """

        return

    def predict_one_action(self):
        """
        Called to ask this displayable to cause image prediction
        to occur for images that may be loaded by its actions.
        """

        return 
    
    def place(self, dest, x, y, width, height, surf, main=True):
        """
        This draws this Displayable onto a destination surface, using
        the placement style information returned by this object's
        get_placement() method.

        @param dest: The surface that this displayable will be drawn
        on.

        @param x: The minimum x coordinate on this surface that this
        Displayable will be drawn to.

        @param y: The minimum y coordinate on this surface that this
        displayable will be drawn to.

        @param width: The width of the area allocated to this
        Displayable.

        @param height: The height of the area allocated to this
        Displayable.

        @param surf: The surface returned by a previous call to
        self.render().
        """
        
        xpos, ypos, xanchor, yanchor, xoffset, yoffset, subpixel = self.get_placement()
        
        if xpos is None:
            xpos = 0
        if ypos is None:
            ypos = 0
        if xanchor is None:
            xanchor = 0
        if yanchor is None:
            yanchor = 0
        if xoffset is None:
            xoffset = 0
        if yoffset is None:
            yoffset = 0
            
        # We need to use type, since isinstance(absolute(0), float).
        if xpos.__class__ is float:
            xpos *= width

        if xanchor.__class__ is float:
            xanchor *= surf.width

        xpos += x + xoffset - xanchor
            
        # y

        if ypos.__class__ is float:
            ypos *= height
            
        if yanchor.__class__ is float:
            yanchor *= surf.height

        ypos += y + yoffset - yanchor

        if dest is not None:
            if subpixel:
                dest.subpixel_blit(surf, (xpos, ypos), main, main, None)
            else:
                dest.blit(surf, (xpos, ypos), main, main, None)
            
        return xpos, ypos

    def set_transform_event(self, event):
        """
        Sets the transform event of this displayable to event.
        """

        if event == self.transform_event:
            return

        self.transform_event = event
        if self.transform_event_responder:
            renpy.display.render.redraw(self, 0)

    def _hide(self, st, at, kind):
        """
        Returns None if this displayable is ready to be hidden, or
        a replacement displayable if it doesn't want to be hidden
        quite yet. Kind is either "hide" or "replaced".
        """
                
        return None

    def _show(self):
        """
        Called when the displayable is added to a scene list.
        """

    def _get_parameterized(self):
        """
        If this is a ImageReference to a parameterized image, return
        the get_parameterized() of the parameterized image. Otherwise,
        return this displayable.
        """

        return self

    def _change_transform_child(self, child):
        """
        If this is a transform, makes a copy of the transform and sets
        the child of the innermost transform to this. Otherwise,
        simply returns child.
        """

        return child

    

class SceneListEntry(renpy.object.Object):
    """
    Represents a scene list entry. Since this was replacing a tuple,
    it should be treated as immutable after its initial creation.
    """
    
    def __init__(self, tag, zorder, show_time, animation_time, displayable, name):
        self.tag = tag
        self.zorder = zorder
        self.show_time = show_time
        self.animation_time = animation_time
        self.displayable = displayable
        self.name = name
        
    def __iter__(self):
        return iter((self.tag, self.zorder, self.show_time, self.animation_time, self.displayable))

    def __getitem__(self, index):
        return (self.tag, self.zorder, self.show_time, self.animation_time, self.displayable)[index]
    
    def __repr__(self):
        return "<SLE: %r %r %r>" % (self.tag, self.name, self.displayable)
    
    def copy(self):
        return SceneListEntry(
            self.tag,
            self.zorder,
            self.show_time,
            self.animation_time,
            self.displayable,
            self.name)
            
    def update_time(self, time):

        rv = self
        
        if self.show_time is None or self.animation_time is None:
            rv = self.copy()
            rv.show_time = rv.show_time or time
            rv.animation_time = rv.animation_time or time

        return rv
    
    
class SceneLists(renpy.object.Object):
    """
    This stores the current scene lists that are being used to display
    things to the user. 
    """

    __version__ = 6
    
    def after_setstate(self):
        for i in renpy.config.layers + renpy.config.top_layers:
            if i not in self.layers:
                self.layers[i] = [ ]
                self.at_list[i] = { }
                self.layer_at_list[i] = (None, [ ])
                
    def after_upgrade(self, version):

        if version < 1:

            self.at_list = { }
            self.layer_at_list = { }

            for i in renpy.config.layers + renpy.config.top_layers:
                self.at_list[i] = { }
                self.layer_at_list[i] = (None, [ ])

        if version < 3:
            self.shown_window = False 

        if version < 4:
            for k in self.layers:
                self.layers[k] = [ SceneListEntry(*(i + (None,)) ) for i in self.layers[k] ]

            self.additional_transient = [ ]

        if version < 5:
            self.drag_group = None

        if version < 6:
            self.shown = self.image_predict_info 
            
    def __init__(self, oldsl, shown):

        super(SceneLists, self).__init__()
        
        # Has a window been shown as part of these scene lists?
        self.shown_window = False
        
        # A map from layer name -> list(SceneListEntry)
        self.layers = { }

        # A map from layer name -> tag -> at_list associated with that tag.
        self.at_list = { }

        # A map from layer to (star time, at_list), where the at list has
        # been applied to the layer as a whole.
        self.layer_at_list = { }

        # The current shown images,
        self.shown = shown

        # A list of (layer, tag) pairs that are considered to be
        # transient.
        self.additional_transient = [ ]

        # Either None, or a DragGroup that's used as the default for
        # drags with names.
        self.drag_group = None

        
        if oldsl:

            for i in renpy.config.layers + renpy.config.top_layers:

                try:
                    self.layers[i] = oldsl.layers[i][:]
                except KeyError:
                    self.layers[i] = [ ]
                
                if i in oldsl.at_list:
                    self.at_list[i] = oldsl.at_list[i].copy()
                    self.layer_at_list[i] = oldsl.layer_at_list[i]
                else:
                    self.at_list[i] = { }
                    self.layer_at_list[i] = (None, [ ])
                
            for i in renpy.config.overlay_layers:
                self.clear(i)

            self.replace_transient()

            self.focused = None

            self.drag_group = oldsl.drag_group
            
        else:
            for i in renpy.config.layers + renpy.config.top_layers:
                self.layers[i] = [ ]
                self.at_list[i] = { }
                self.layer_at_list[i] = (None, [ ])
                
            self.music = None
            self.focused = None

    def replace_transient(self):
        """
        Replaces the contents of the transient display list with
        a copy of the master display list. This is used after a
        scene is displayed to get rid of transitions and interface
        elements.
        """

        for i in renpy.config.transient_layers:
            self.clear(i, True)

        for layer, tag in self.additional_transient:
            self.remove(layer, tag)

        self.additional_transient = [ ]
            
    def transient_is_empty(self):
        """
        This returns True if all transient layers are empty. This is
        used by the rollback code, as we can't start a new rollback
        if there is something in a transient layer (as things in the
        transient layer may contain objects that cannot be pickled,
        like lambdas.)
        """

        for i in renpy.config.transient_layers:
            if self.layers[i]:
                return False

        return True

    def transform_state(self, old_thing, new_thing):
        """
        If the old thing is a transform, then move the state of that transform
        to the new thing.
        """

        if old_thing is None:
            return new_thing

        # Don't bother wrapping screens, as they can't be transformed.
        if isinstance(new_thing, renpy.display.screen.ScreenDisplayable):
            return new_thing
        
        old_transform = old_thing._get_parameterized()
        if not isinstance(old_transform, renpy.display.motion.Transform):
            return new_thing

        new_transform = new_thing._get_parameterized()
        if not isinstance(new_transform, renpy.display.motion.Transform):
            new_thing = new_transform = renpy.display.motion.Transform(child=new_thing)
        
        new_transform.take_state(old_transform)
        return new_thing


    def find_index(self, layer, tag, zorder, behind):
        """
        This finds the spot in the named layer where we should insert the
        displayable. It returns two things: an index at which the new thing
        should be added, and an index at which the old thing should be hidden.
        (Note that the indexes are relative to the current state of the list,
        which may change on an add or remove.)
        """

        add_index = None
        remove_index = None


        for i, sle in enumerate(self.layers[layer]):

            if add_index is None:
            
                if sle.zorder == zorder:
                    if sle.tag and (sle.tag == tag or sle.tag in behind):
                        add_index = i
                        
                elif sle.zorder > zorder:
                    add_index = i

                    
            if remove_index is None:
                if (sle.tag and sle.tag == tag) or sle.displayable == tag:
                    remove_index = i

            
        if add_index is None:
            add_index = len(self.layers[layer])
        
        return add_index, remove_index
    

    def add(self,
            layer,
            thing,
            key=None,
            zorder=0,
            behind=[ ],
            at_list=[ ],
            name=None,
            atl=None,
            default_transform=None,
            transient=False):
        """
        Adds something to this scene list. Some of these names are quite a bit
        out of date.

        `thing` - The displayable to add.

        `key` - A string giving the tag associated with this thing.

        `zorder` - Where to place this thing in the zorder, an integer
        A greater value means closer to the user.

        `behind` - A list of tags to place the thing behind.

        `at_list` - The at_list associated with this
        displayable. Counterintunitively, this is not actually
        applied, but merely stored for future use.

        `name` - The full name of the image being displayed. This is used for
        image lookup.

        `atl` - If not None, an atl block applied to the thing. (This actually is
        applied here.)

        `default_transform` - The default transform that is used to initialized
        the values in the other transforms.        
        """
        
        if not isinstance(thing, Displayable):
            raise Exception("Attempting to show something that isn't a displayable:" + repr(thing))
        
        if layer not in self.layers:
            raise Exception("Trying to add something to non-existent layer '%s'." % layer)

        if key:
            self.remove_hide_replaced(layer, key)
            self.at_list[layer][key] = at_list

        if key and name:
            self.shown.predict_show(layer, name)

        if transient:
            self.additional_transient.append((layer, key))
            
        l = self.layers[layer]
        
        if atl:
            thing = renpy.display.motion.ATLTransform(atl, child=thing)

        add_index, remove_index = self.find_index(layer, key, zorder, behind)

        at = None
        st = None

        if remove_index is not None:
            sle = l[remove_index]            
            at = sle.animation_time            
            old = sle.displayable
            
            if (not atl and
                not at_list and
                renpy.config.keep_running_transform and
                isinstance(old, renpy.display.motion.Transform)):

                thing = sle.displayable._change_transform_child(thing)
            else:
                thing = self.transform_state(l[remove_index].displayable, thing)

            thing.set_transform_event("replace")
            thing._show()
            
        else:            

            if not isinstance(thing, renpy.display.motion.Transform):
                thing = self.transform_state(default_transform, thing)
                
            thing.set_transform_event("show")
            thing._show()

        sle = SceneListEntry(key, zorder, st, at, thing, name)
        l.insert(add_index, sle)

        if remove_index is not None: 
            if add_index <= remove_index:
                remove_index += 1

            self.hide_or_replace(layer, remove_index, "replaced")

    def hide_or_replace(self, layer, index, prefix):
        """
        Hides or replaces the scene list entry at the given
        index. `prefix` is a prefix that is used if the entry
        decides it doesn't want to be hidden quite yet.
        """

        if index is None:
            return
        
        l = self.layers[layer]
        oldsle = l[index]

        now = get_time()

        st = oldsle.show_time or now
        at = oldsle.animation_time or now

        if oldsle.tag:
        
            d = oldsle.displayable._hide(now - st, now - at, prefix)
            
            if d is not None:
                
                sle = SceneListEntry(
                    prefix + "$" + oldsle.tag,
                    oldsle.zorder,
                    st,
                    at,
                    d,
                    None)

                l[index] = sle

                return

        l.pop(index)

    def get_all_displayables(self):
        """
        Gets all displayables reachable from this scene list.
        """
        
        rv = [ ]
        for l in self.layers.itervalues():
            for sle in l:
                rv.append(sle.displayable)
                
        return rv

    def remove_above(self, layer, thing):
        """
        Removes everything on the layer that is closer to the user
        than thing, which may be either a tag or a displayable. Thing must
        be displayed, or everything will be removed.
        """
        
        for i in reversed(xrange(len(self.layers[layer]))):

            sle = self.layers[layer][i]

            if thing:
                if sle.tag == thing or sle.displayable == thing:
                    break

            if sle.tag and "$" in sle.tag:
                continue

            self.hide_or_replace(layer, i, "hide")
            
    def remove(self, layer, thing):
        """
        Thing is either a key or a displayable. This iterates through the
        named layer, searching for entries matching the thing.
        When they are found, they are removed from the displaylist.

        It's not an error to remove something that isn't in the layer in
        the first place.
        """

        if layer not in self.layers:
            raise Exception("Trying to remove something from non-existent layer '%s'." % layer)

        _add_index, remove_index = self.find_index(layer, thing, 0, [ ])

        if remove_index is not None:
            tag = self.layers[layer][remove_index].tag

            if tag:
                self.shown.predict_hide(layer, (tag,))
                self.at_list[layer].pop(tag, None)
            
            self.hide_or_replace(layer, remove_index, "hide")

    def clear(self, layer, hide=False):
        """
        Clears the named layer, making it empty.

        If hide is True, then objects are hidden. Otherwise, they are
        totally wiped out.
        """

        if not hide:
            self.layers[layer] = [ ]

        else:

            # Have to iterate in reverse order, since otherwise
            # the indexes might change.
            for i in reversed(xrange(len(self.layers[layer]))):
                self.hide_or_replace(layer, i, hide)

        self.at_list[layer].clear()
        self.shown.predict_scene(layer)
        self.layer_at_list[layer] = (None, [ ])

    def set_layer_at_list(self, layer, at_list):
        self.layer_at_list[layer] = (None, list(at_list))
        
    def set_times(self, time):
        """
        This finds entries with a time of None, and replaces that
        time with the given time.
        """

        for l, (t, list) in self.layer_at_list.items(): #@ReservedAssignment
            self.layer_at_list[l] = (t or time, list)
        
        for l, ll in self.layers.iteritems():
            self.layers[l] = [ i.update_time(time) for i in ll ]
            
    def showing(self, layer, name):
        """
        Returns true if something with the prefix of the given name
        is found in the scene list.
        """

        return self.shown.showing(layer, name)

    def make_layer(self, layer, properties):
        """
        Creates a Fixed with the given layer name and scene_list.
        """

        rv = renpy.display.layout.MultiBox(layout='fixed', focus=layer, **properties)
        rv.append_scene_list(self.layers[layer])

        time, at_list = self.layer_at_list[layer]

        if at_list:
            for a in at_list:
                
                if isinstance(a, renpy.display.motion.Transform):
                    rv = a(child=rv)
                else:
                    rv = a(rv)

                f = renpy.display.layout.MultiBox(layout='fixed')
                f.add(rv, time, time)
                rv = f

        rv.layer_name = layer
        return rv

    def remove_hide_replaced(self, layer, tag):
        """
        Removes things that are hiding or replaced, that have the given
        tag.
        """

        hide_tag = "hide$" + tag
        replaced_tag = "replaced$" + tag

        l = self.layers[layer]
        self.layers[layer] = [ i for i in l if i.tag != hide_tag and i.tag != replaced_tag ]
        
    def remove_hidden(self):
        """
        Goes through all of the layers, and removes things that are
        hidden and are no longer being kept alive by their hide
        methods.
        """

        now = get_time()
        
        for l in self.layers:
            newl = [ ]

            for sle in self.layers[l]:

                if sle.tag:

                    if sle.tag.startswith("hide$"):
                        d = sle.displayable._hide(now - sle.show_time, now - sle.animation_time, "hide")
                        if not d:
                            continue

                    elif sle.tag.startswith("replaced$"):
                        d = sle.displayable._hide(now - sle.show_time, now - sle.animation_time, "replaced")
                        if not d:
                            continue
                        
                newl.append(sle)
                        
            self.layers[l] = newl  

    def get_displayable_by_tag(self, layer, tag):
        """
        Returns the displayable on the layer with the given tag, or None
        if no such displayable exists. Note that this will usually return
        a Transform.
        """

        if layer not in self.layers:
            raise Exception("Unknown layer %r." % layer)

        for sle in self.layers[layer]:
            if sle.tag == tag:
                return sle.displayable

        return None

    def get_displayable_by_name(self, layer, name):
        """
        Returns the displayable on the layer with the given tag, or None
        if no such displayable exists. Note that this will usually return
        a Transform.
        """

        if layer not in self.layers:
            raise Exception("Unknown layer %r." % layer)

        for sle in self.layers[layer]:

            if sle.name == name:
                return sle.displayable

        return None

    
def scene_lists(index=-1):
    """
    Returns either the current scenelists object, or the one for the
    context at the given index.
    """

    return renpy.game.context(index).scene_lists
   

class Interface(object):
    """
    This represents the user interface that interacts with the user.
    It manages the Display objects that display things to the user, and
    also handles accepting and responding to user input.

    @ivar display: The display that we used to display the screen.

    @ivar profile_time: The time of the last profiling.

    @ivar screenshot: A screenshot, or None if no screenshot has been
    taken.

    @ivar old_scene: The last thing that was displayed to the screen.

    @ivar transition: A map from layer name to the transition that will
    be applied the next time interact restarts.

    @ivar transition_time: A map from layer name to the time the transition
    involving that layer started.

    @ivar transition_from: A map from layer name to the scene that we're
    transitioning from on that layer.
    
    @ivar suppress_transition: If True, then the next transition will not
    happen.

    @ivar force_redraw: If True, a redraw is forced.

    @ivar restart_interaction: If True, the current interaction will
    be restarted.

    @ivar pushed_event: If not None, an event that was pushed back
    onto the stack.

    @ivar mouse: The name of the mouse cursor to use during the current
    interaction.

    @ivar ticks: The number of 20hz ticks.

    @ivar frame_time: The time at which we began drawing this frame.

    @ivar interact_time: The time of the start of the first frame of the current interact_core.

    @ivar time_event: A singleton ignored event.

    @ivar event_time: The time of the current event.

    @ivar timeout_time: The time at which the timeout will occur.
    """

    def __init__(self):
        self.screenshot = None
        self.old_scene = { }
        self.transition = { }
        self.ongoing_transition = { }
        self.transition_time = { }
        self.transition_from = { }
        self.suppress_transition = False
        self.quick_quit = False
        self.force_redraw = False
        self.restart_interaction = False
        self.pushed_event = None
        self.ticks = 0
        self.mouse = 'default'
        self.timeout_time = None
        self.last_event = None
        self.current_context = None
        self.roll_forward = None
        
        # Things to be preloaded.
        self.preloads = [ ]

        # The time at which this draw occurs.
        self.frame_time = 0

        # The time when this interaction occured.
        self.interact_time = None

        # The time we last tried to quit.
        self.quit_time = 0
        
        self.time_event = pygame.event.Event(TIMEEVENT)

        # Are we focused?
        self.focused = True
        
        # Properties for each layer.
        self.layer_properties = { }

        # Have we shown the window this interaction?
        self.shown_window = False
        
        for layer in renpy.config.layers + renpy.config.top_layers:
            if layer in renpy.config.layer_clipping:
                x, y, w, h = renpy.config.layer_clipping[layer]
                self.layer_properties[layer] = dict(
                    xpos = x,
                    xanchor = 0,
                    ypos = y,
                    yanchor = 0,
                    xmaximum = w,
                    ymaximum = h,
                    xminimum = w,
                    yminimum = h,
                    clipping = True,
                    )

            else:
                self.layer_properties[layer] = dict()
                

        # A stack giving the values of self.transition and self.transition_time
        # for contexts outside the current one. This is used to restore those
        # in the case where nothing has changed in the new context.
        self.transition_info_stack = [ ]

        # The time when the event was dispatched.
        self.event_time = 0

        # The time we saw the last mouse event.
        self.mouse_event_time = None

        # Should we show the mouse?
        self.show_mouse = True

        # Should we reset the display?
        self.display_reset = False
        
        # The last size we were resized to. This lets us debounce the 
        # VIDEORESIZE event.
        self.last_resize = None
        
        # Ensure that we kill off the presplash.
        renpy.display.presplash.end()

        # Initialize pygame.
        if pygame.version.vernum < (1, 8, 1):
            raise Exception("Ren'Py requires pygame 1.8.1 to run.")

        try:
            pygame.macosx.init() #@UndefinedVariable
        except:
            pass

        pygame.font.init()
        renpy.audio.audio.init()
        renpy.display.joystick.init()
        pygame.display.init()
        
        # Init timing.
        init_time()
        self.profile_time = get_time()
        self.mouse_event_time = get_time()
        
        # The current window caption.
        self.window_caption = None

        renpy.game.interface = self
        renpy.display.interface = self
        
        # Are we in safe mode, from holding down shift at start?
        self.safe_mode = False
        if renpy.first_utter_start and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
            self.safe_mode = True

        # Setup the video mode.
        self.set_mode()

        # Load the image fonts.
        renpy.text.font.load_image_fonts()

        # Setup the android keymap.
        if android is not None:
            android.map_key(android.KEYCODE_BACK, pygame.K_PAGEUP)
            android.map_key(android.KEYCODE_MENU, pygame.K_ESCAPE)

        # Double check, since at least on Linux, we can't set safe_mode until
        # the window maps.
        if renpy.first_utter_start and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
            self.safe_mode = True
            
        # Setup periodic event.
        pygame.time.set_timer(PERIODIC, PERIODIC_INTERVAL)

        # Don't grab the screen.
        pygame.event.set_grab(False)

        # Do we need a background screenshot?
        self.bgscreenshot_needed = False

        # Event used to signal background screenshot taken.
        self.bgscreenshot_event = threading.Event()

        # The background screenshot surface.
        self.bgscreenshot_surface = None

        
    def post_init(self):
        # Setup.
        self.set_window_caption(force=True)
        self.set_icon()
    
    def set_icon(self):
        """
        This is called to set up the window icon.
        """

        # Window icon.
        icon = renpy.config.window_icon

        if renpy.windows and renpy.config.windows_icon:
            icon = renpy.config.windows_icon
            
        if icon:

            im = renpy.display.scale.image_load_unscaled(
                renpy.loader.load(icon),
                icon,
                convert=False,
                )

            # Convert the aspect ratio to be square.
            iw, ih = im.get_size()
            imax = max(iw, ih)
            square_im = renpy.display.pgrender.surface_unscaled((imax, imax), True)
            square_im.blit(im, ( (imax-iw)/2, (imax-ih)/2 ))
            im = square_im

            if renpy.windows and im.get_size() != (32, 32):
                im = renpy.display.scale.real_smoothscale(im, (32, 32))
            
            pygame.display.set_icon(im)

            
    def set_window_caption(self, force=False):
        caption = renpy.config.window_title + renpy.store._window_subtitle
        if not force and caption == self.window_caption:
            return

        self.window_caption = caption
        pygame.display.set_caption(caption.encode("utf-8"))
        
    def iconify(self):
        pygame.display.iconify()

    def get_draw_constructors(self):
        """
        Figures out the list of draw constructors to try.
        """
        
        renderer = renpy.game.preferences.renderer
        renderer = os.environ.get("RENPY_RENDERER", renderer)
        
        if self.safe_mode:
            renderer = "sw"

        renpy.config.renderer = renderer

        if renderer == "auto":
            if renpy.windows:
                renderers = [ "gl", "angle", "sw" ]
            else:
                renderers = [ "gl", "sw" ]                
        else:
            renderers = [ renderer, "sw" ]
            
        draw_objects = { }

        def make_draw(name, mod, cls, *args):
            if name not in renderers:
                return False
            
            try:
                __import__(mod)
                module = sys.modules[mod]
                draw_class = getattr(module, cls)                
                draw_objects[name] = draw_class(*args)
                return True

            except:
                renpy.display.log.write("Couldn't import {0} renderer:".format(name))
                renpy.display.log.exception()

                return False

        if renpy.windows:
            has_angle = make_draw("angle", "renpy.angle.gldraw", "GLDraw")
        else:
            has_angle = False
        
        make_draw("gl", "renpy.gl.gldraw", "GLDraw", not has_angle)
        make_draw("sw", "renpy.display.swdraw", "SWDraw")

        rv = [ ]

        def append_draw(name):
            if name in draw_objects:
                rv.append(draw_objects[name])
            else:
                renpy.display.log.write("Unknown renderer: {0}".format(name))

        for i in renderers:
            append_draw(i)

        return rv


    def kill_textures(self):
        renpy.display.render.free_memory()
        renpy.text.text.layout_cache_clear()

    def kill_textures_and_surfaces(self):
        """
        Kill all textures and surfaces that are loaded.
        """

        self.kill_textures()
        
        renpy.display.im.cache.clear()
        renpy.display.module.bo_cache = None       
        
    def set_mode(self, physical_size=None):
        """
        This sets the video mode. It also picks the draw object.
        """
        
        # Ensure that we kill off the movie when changing screen res.
        renpy.display.video.movie_stop(clear=False)

        if self.display_reset:
            renpy.display.draw.deinit()

            if renpy.display.draw.info["renderer"] == "angle":
                renpy.display.draw.quit()

            renpy.display.render.free_memory()
            renpy.display.im.cache.clear()
            renpy.text.text.layout_cache_clear()

            renpy.display.module.bo_cache = None
            
            self.kill_textures_and_surfaces()
                        
        self.display_reset = False

        virtual_size = (renpy.config.screen_width, renpy.config.screen_height)

        if physical_size is None:
            if renpy.android or renpy.game.preferences.physical_size is None: #@UndefinedVariable
                physical_size = (renpy.config.screen_width, renpy.config.screen_height)
            else:
                physical_size = renpy.game.preferences.physical_size
                
        # Setup screen.
        fullscreen = renpy.game.preferences.fullscreen
        
        # If we're in fullscreen mode, and changing to another mode, go to
        # windowed mode first.
        s = pygame.display.get_surface()
        if s and (s.get_flags() & pygame.FULLSCREEN):
            fullscreen = False
            
        self.fullscreen = fullscreen

        if os.environ.get('RENPY_DISABLE_FULLSCREEN', False):
            fullscreen = False
            self.fullscreen = renpy.game.preferences.fullscreen
        
        if renpy.display.draw:
            draws = [ renpy.display.draw ]
        else:
            draws = self.get_draw_constructors()

        for draw in draws:
            if draw.set_mode(virtual_size, physical_size, fullscreen):
                renpy.display.draw = draw
                break
            else:
                pygame.display.quit()
        else:
            # Ensure we don't get stuck in fullscreen.
            renpy.game.preferences.fullscreen = False
            raise Exception("Could not set video mode.")
        
        # Save the video size.
        if renpy.config.save_physical_size and not fullscreen: 
            renpy.game.preferences.physical_size = renpy.display.draw.get_physical_size()
       
        if android:
            android.init()
        
        # We need to redraw the (now blank) screen.
        self.force_redraw = True

        # Assume we have focus until told otherwise.
        self.focused = True
        
        # Assume we're not minimized.
        self.minimized = False

    def draw_screen(self, root_widget, fullscreen_video):
        
        surftree = renpy.display.render.render_screen(
            root_widget,
            renpy.config.screen_width,
            renpy.config.screen_height,
            )

        renpy.display.draw.draw_screen(surftree, fullscreen_video)
        
        renpy.display.render.mark_sweep()
        renpy.display.focus.take_focuses()

        self.surftree = surftree
        self.fullscreen_video = fullscreen_video


    def take_screenshot(self, scale, background=False):
        """
        This takes a screenshot of the current screen, and stores it so
        that it can gotten using get_screenshot()
        
        `background`
           If true, we're in a background thread. So queue the request
           until it can be handled by the main thread.
        """

        if background:
            self.bgscreenshot_event.clear()
            self.bgscreenshot_needed = True
            self.bgscreenshot_event.wait()

            window = self.bgscreenshot_surface
            self.bgscreenshot_surface = None

        else:

            window = renpy.display.draw.screenshot(self.surftree, self.fullscreen_video)
        
        surf = renpy.display.pgrender.copy_surface(window, True)
        surf = renpy.display.scale.smoothscale(surf, scale)
        surf = surf.convert()
        
        sio = cStringIO.StringIO()
        renpy.display.module.save_png(surf, sio, 0)
        self.screenshot = sio.getvalue()
        sio.close()
        
        
    def save_screenshot(self, filename):
        """
        Saves a full-size screenshot in the given filename.
        """

        window = renpy.display.draw.screenshot(self.surftree, self.fullscreen_video)

        if renpy.config.screenshot_crop:
            window = window.subsurface(renpy.config.screenshot_crop)
        
        try:
            renpy.display.scale.image_save_unscaled(window, filename)
        except:
            if renpy.config.debug:
                raise
            pass
        
        
    def get_screenshot(self):
        """
        Gets the current screenshot, as a string. Returns None if there isn't
        a current screenshot.
        """

        rv = self.screenshot

        if not rv:
            self.take_screenshot((renpy.config.thumbnail_width, renpy.config.thumbnail_height))
            rv = self.screenshot
            self.lose_screenshot()

        return rv

    
    def lose_screenshot(self):
        """
        This deallocates the saved screenshot.
        """

        self.screenshot = None

        
    def show_window(self):

        if not renpy.store._window:
            return

        if renpy.game.context().scene_lists.shown_window:
            return

        if renpy.config.empty_window:
            renpy.config.empty_window()
            
    def do_with(self, trans, paired, clear=False):
        
        if renpy.config.with_callback:
            trans = renpy.config.with_callback(trans, paired)

        if (not trans) or self.suppress_transition:
            self.with_none()
            return False
        else:
            self.set_transition(trans)
            return self.interact(trans_pause=True,
                                 suppress_overlay=not renpy.config.overlay_during_with,
                                 mouse='with',
                                 clear=clear)

    def with_none(self):
        """
        Implements the with None command, which sets the scene we will
        be transitioning from.
        """

        renpy.exports.say_attributes = None

        # Show the window, if that's necessary.
        self.show_window()

        # Compute the overlay.
        self.compute_overlay()

        scene_lists = renpy.game.context().scene_lists

        # Compute the scene.
        self.old_scene = self.compute_scene(scene_lists)        

        # Get rid of transient things.

        for i in renpy.config.overlay_layers:
            scene_lists.clear(i)

        scene_lists.replace_transient()
        scene_lists.shown_window = False

        
    def set_transition(self, transition, layer=None, force=False):
        """
        Sets the transition that will be performed as part of the next
        interaction.
        """

        if self.suppress_transition and not force:
            return

        if transition is None:
            self.transition.pop(layer, None)
        else:
            self.transition[layer] = transition
        

    def event_peek(self):
        """
        This peeks the next event. It returns None if no event exists.
        """

        if self.pushed_event:
            return self.pushed_event

        ev = pygame.event.poll()

        if ev.type == pygame.NOEVENT:
            # Seems to prevent the CPU from speeding up.
            renpy.display.draw.event_peek_sleep()
            return None

        self.pushed_event = ev

        return ev

    def event_poll(self):
        """
        Called to busy-wait for an event while we're waiting to
        redraw a frame.
        """
        
        if self.pushed_event:
            rv = self.pushed_event
            self.pushed_event = None
        else:
            rv = pygame.event.poll()

        self.last_event = rv

        return rv
            

    def event_wait(self):
        """
        This is in its own function so that we can track in the
        profiler how much time is spent in interact.
        """

        if self.pushed_event:
            rv = self.pushed_event
            self.pushed_event = None
            self.last_event = rv
            return rv

        # Handle a request for a background screenshot.
        if self.bgscreenshot_needed:
            self.bgscreenshot_needed = False
            self.bgscreenshot_surface = renpy.display.draw.screenshot(self.surftree, self.fullscreen_video)
            self.bgscreenshot_event.set()
            
        try:
            cpu_idle.set()            
            ev = pygame.event.wait()
        finally:
            cpu_idle.clear()

        self.last_event = ev

        return ev

    
    def compute_overlay(self):

        if renpy.store.suppress_overlay:
            return
        
        # Figure out what the overlay layer should look like.
        renpy.ui.layer("overlay")

        for i in renpy.config.overlay_functions:
            i()

        if renpy.game.context().scene_lists.shown_window:
            for i in renpy.config.window_overlay_functions:
                i()
                
        renpy.ui.close()
        
    
    def compute_scene(self, scene_lists):
        """
        This converts scene lists into a dictionary mapping layer
        name to a Fixed containing that layer.
        """

        rv = { }

        for layer in renpy.config.layers + renpy.config.top_layers:
            rv[layer] = scene_lists.make_layer(layer, self.layer_properties[layer])

        root = renpy.display.layout.MultiBox(layout='fixed')
        root.layers = { }

        for layer in renpy.config.layers:
            root.layers[layer] = rv[layer]
            root.add(rv[layer])
        rv[None] = root
             
        return rv


    def quit_event(self):
        """
        This is called to handle the user invoking a quit.
        """

        if self.quit_time > (time.time() - .75):
            raise renpy.game.QuitException()

        if renpy.config.quit_action is not None:
            self.quit_time = time.time()

            # Make the screen more suitable for interactions.
            renpy.exports.movie_stop(only_fullscreen=True)
            renpy.store.mouse_visible = True

            renpy.display.behavior.run(renpy.config.quit_action)
        else:
            raise renpy.game.QuitException()

        
    def get_mouse_info(self):
        # Figure out if the mouse visibility algorithm is hiding the mouse.
        if self.mouse_event_time + renpy.config.mouse_hide_time < renpy.display.core.get_time():
            visible = False
        else:
            visible = renpy.store.mouse_visible and (not renpy.game.less_mouse)
            
        visible = visible and self.show_mouse

        # If not visible, hide the mouse.
        if not visible:
            return False, 0, 0, None
        
        # Deal with a hardware mouse, the easy way.
        if not renpy.config.mouse:
            return True, 0, 0, None

        # Deal with the mouse going offscreen.
        if not self.focused:
            return False, 0, 0, None
        
        mouse_kind = renpy.display.focus.get_mouse() or self.mouse 
        
        # Figure out the mouse animation.
        if mouse_kind in renpy.config.mouse:
            anim = renpy.config.mouse[mouse_kind]
        else:
            anim = renpy.config.mouse[getattr(renpy.store, 'default_mouse', 'default')]

        img, x, y = anim[self.ticks % len(anim)]
        tex = renpy.display.im.load_image(img)

        return False, x, y, tex

    def drawn_since(self, seconds_ago):
        """
        Returns true if the screen has been drawn in the last `seconds_ago`,
        and false otherwise.
        """

        return (get_time() - self.frame_time) <= seconds_ago

    def android_check_suspend(self):
        
        if android.check_pause():

            android.sound.pause_all()

            pygame.time.set_timer(PERIODIC, 0)
            pygame.time.set_timer(REDRAW, 0)
            pygame.time.set_timer(TIMEEVENT, 0)

            # The game has to be saved.
            renpy.loadsave.save("_reload-1")

            android.wait_for_resume()

            # Since we came back to life, we can get rid of the
            # auto-reload.
            renpy.loadsave.unlink_save("_reload-1")

            pygame.time.set_timer(PERIODIC, PERIODIC_INTERVAL)

            android.sound.unpause_all()
            
    def iconified(self):
        """
        Called when we become an icon.
        """

        if self.minimized:
            return

        self.minimized = True

        renpy.display.log.write("The window was minimized.")
        
    
    def restored(self):
        """
        Called when we are restored from being an icon.
        """
        
        # This is necessary on Windows/DirectX/Angle, as otherwise we get
        # a blank screen.

        if not self.minimized:
            return
        
        self.minimized = False

        renpy.display.log.write("The window was restored.")

        if renpy.windows:
            self.display_reset = True
            self.set_mode(self.last_resize)
    
    def interact(self, clear=True, suppress_window=False, **kwargs):
        """
        This handles an interaction, restarting it if necessary. All of the
        keyword arguments are passed off to interact_core.
        """

        # Cancel magic error reporting.
        renpy.bootstrap.report_error = None
        
        context = renpy.game.context()
        
        if context.interacting:
            raise Exception("Cannot start an interaction in the middle of an interaction, without creating a new context.")

        context.interacting = True
                
        # Show a missing window.
        if not suppress_window:
            self.show_window()
        
        # These things can be done once per interaction.

        preloads = self.preloads
        self.preloads = [ ]

        try:
            renpy.game.after_rollback = False

            for i in renpy.config.start_interact_callbacks:
                i()

            repeat = True

            while repeat:
                repeat, rv = self.interact_core(preloads=preloads, **kwargs)

            return rv
        
        finally:

            context.interacting = False
            
            # Clean out transient stuff at the end of an interaction.
            if clear:
                scene_lists = renpy.game.context().scene_lists
                scene_lists.replace_transient()

            self.ongoing_transition = { }
            self.transition_time = { }
            self.transition_from = { }
                
            self.restart_interaction = True

            renpy.game.context().scene_lists.shown_window = False
            
    def interact_core(self,
                      show_mouse=True,
                      trans_pause=False,
                      suppress_overlay=False,
                      suppress_underlay=False,
                      mouse='default',
                      preloads=[],
                      roll_forward=None,
                      ):

        """
        This handles one cycle of displaying an image to the user,
        and then responding to user input.

        @param show_mouse: Should the mouse be shown during this
        interaction? Only advisory, and usually doesn't work.

        @param trans_pause: If given, we must have a transition. Should we
        add a pause behavior during the transition?

        @param suppress_overlay: This suppresses the display of the overlay.
        @param suppress_underlay: This suppresses the display of the underlay.
        """
        
        self.roll_forward = roll_forward
        self.show_mouse = show_mouse
        
        suppress_transition = renpy.config.skipping or renpy.game.less_updates

        # The global one.
        self.suppress_transition = False
        
        # Figure out transitions.
        for k in self.transition:
            if k not in self.old_scene:
                continue
            
            self.ongoing_transition[k] = self.transition[k]            
            self.transition_from[k] = self.old_scene[k]
            self.transition_time[k] = None
                    
        self.transition.clear()

        if suppress_transition:
            self.ongoing_transition.clear()
            self.transition_from.clear()
            self.transition_time.clear()
 
        ## Safety condition, prevents deadlocks.
        if trans_pause:
            if not self.ongoing_transition:
                return False, None
            if None not in self.ongoing_transition:
                return False, None
            if suppress_transition:
                return False, None
            if not self.old_scene:
                return False, None
            
        # We just restarted.
        self.restart_interaction = False

        # Setup the mouse.
        self.mouse = mouse

        # The start and end times of this interaction.
        start_time = get_time()
        end_time = start_time

        # frames = 0

        for i in renpy.config.interact_callbacks:
            i()

        # Set the window caption.
        self.set_window_caption()
            
        # Tick time forward.
        renpy.display.im.cache.tick()
        renpy.text.text.layout_cache_tick()
        renpy.display.predict.reset()
        
        # Cleare the size groups.
        renpy.display.layout.size_groups.clear()
        
        # Clear some events.
        pygame.event.clear((pygame.MOUSEMOTION,
                            PERIODIC,
                            TIMEEVENT,
                            REDRAW))

        # Add a single TIMEEVENT to the queue.
        try:
            pygame.event.post(self.time_event)
        except:
            pass
        
        # Figure out the scene list we want to show.        
        scene_lists = renpy.game.context().scene_lists

        # Remove the now-hidden things.
        scene_lists.remove_hidden()

        # Compute the overlay.
        if not suppress_overlay:
            self.compute_overlay()

        # The root widget of everything that is displayed on the screen.
        root_widget = renpy.display.layout.MultiBox(layout='fixed') 
        root_widget.layers = { }

        # A list of widgets that are roots of trees of widgets that are
        # considered for focusing.
        focus_roots = [ ]

        # Add the underlay to the root widget.
        if not suppress_underlay:
            for i in renpy.config.underlay:
                root_widget.add(i)
                focus_roots.append(i)

            if roll_forward is not None:
                rfw = renpy.display.behavior.RollForward(roll_forward)
                root_widget.add(rfw)
                focus_roots.append(rfw)
                
        # Figure out the scene. (All of the layers, and the root.)
        scene = self.compute_scene(scene_lists)

        # If necessary, load all images here.
        for w in scene.itervalues():
            try:
                renpy.display.predict.displayable(w)
            except:
                pass

        # The root widget of all of the layers.
        layers_root = renpy.display.layout.MultiBox(layout='fixed')
        layers_root.layers = { }

        def add_layer(where, layer):

            scene_layer = scene[layer]
            focus_roots.append(scene_layer)

            if (self.ongoing_transition.get(layer, None) and
                not suppress_transition):

                trans = self.ongoing_transition[layer](
                    old_widget=self.transition_from[layer],
                    new_widget=scene_layer)
                                               
                if not isinstance(trans, Displayable):
                    raise Exception("Expected transition to be a displayable, not a %r" % trans)

                transition_time = self.transition_time.get(layer, None)
                
                where.add(trans, transition_time, transition_time)
                where.layers[layer] = trans
                
            else:
                where.layers[layer] = scene_layer
                where.add(scene_layer)

        # Add layers (perhaps with transitions) to the layers root.
        for layer in renpy.config.layers:
            add_layer(layers_root, layer)
                
        # Add layers_root to root_widget, perhaps through a transition.
        if (self.ongoing_transition.get(None, None) and
            not suppress_transition):

            old_root = renpy.display.layout.MultiBox(layout='fixed')
            old_root.layers = { }

            for layer in renpy.config.layers:
                d = self.transition_from[None].layers[layer]
                old_root.layers[layer] = d
                old_root.add(d)

            trans = self.ongoing_transition[None](
                old_widget=old_root,
                new_widget=layers_root)

            if not isinstance(trans, Displayable):
                raise Exception("Expected transition to be a displayable, not a %r" % trans)

            trans._show()
            
            transition_time = self.transition_time.get(None, None)
            root_widget.add(trans, transition_time, transition_time)

            if trans_pause:
                sb = renpy.display.behavior.SayBehavior()
                root_widget.add(sb)
                focus_roots.append(sb)

                pb = renpy.display.behavior.PauseBehavior(trans.delay)
                root_widget.add(pb, transition_time, transition_time)
                focus_roots.append(pb)
                
        else:
            root_widget.add(layers_root)

        # Add top_layers to the root_widget.
        for layer in renpy.config.top_layers:
            add_layer(root_widget, layer)

        prediction_coroutine = renpy.display.predict.prediction_coroutine(root_widget)
            
        # Clean out the registered adjustments.
        renpy.display.behavior.adj_registered.clear()

        # Clean up some movie-related things.
        renpy.display.video.early_interact()

        # Call per-interaction code for all widgets.
        root_widget.visit_all(lambda i : i.per_interact())
        
        # Now, update various things regarding scenes and transitions,
        # so we are ready for a new interaction or a restart.
        self.old_scene = scene

        # Okay, from here on we now have a single root widget (root_widget),
        # which we will try to show to the user.

        # Figure out what should be focused.
        renpy.display.focus.before_interact(focus_roots)

        # Redraw the screen.
        renpy.display.render.process_redraws()
        needs_redraw = True

        # First pass through the while loop?
        first_pass = True

        # We don't yet know when the interaction began.
        self.interact_time = None
        
        # We only want to do autosave once.
        did_autosave = False
        
        old_timeout_time = None
        old_redraw_time = None

        rv = None

        # Start sound.
        renpy.audio.audio.interact()

        # This try block is used to force cleanup even on termination
        # caused by an exception propigating through this function.
        try: 

            while rv is None:

                # Check for a change in fullscreen preference.                
                if self.fullscreen != renpy.game.preferences.fullscreen or self.display_reset:
                    self.set_mode()
                    needs_redraw = True

                # Check for suspend.
                if android:
                    self.android_check_suspend()

                # Redraw the screen.
                if (self.force_redraw or
                    ((first_pass or not pygame.event.peek(ALL_EVENTS)) and 
                     renpy.display.draw.should_redraw(needs_redraw, first_pass))):

                    self.force_redraw = False
                    
                    # If we have a movie, start showing it.
                    fullscreen_video = renpy.display.video.interact()

                    # Clean out the redraws, if we have to.
                    # renpy.display.render.kill_redraws()
                    
                    # Draw the screen.
                    self.frame_time = get_time()

                    if not self.interact_time:
                        self.interact_time = self.frame_time

                    self.draw_screen(root_widget, fullscreen_video)
                        
                    if first_pass:
                        scene_lists.set_times(self.interact_time)
                        for k, v in self.transition_time.iteritems():
                            if v is None:
                                self.transition_time[k] = self.interact_time

                    renpy.config.frames += 1

                    # If profiling is enabled, report the profile time.
                    if renpy.config.profile :
                        new_time = get_time()

                        if new_time - self.profile_time > .015:
                            print "Profile: Redraw took %f seconds." % (new_time - self.frame_time)
                            print "Profile: %f seconds to complete event." % (new_time - self.profile_time)

                        
                    if first_pass and self.last_event:
                        x, y = renpy.display.draw.get_mouse_pos()
                        renpy.display.focus.mouse_handler(self.last_event, x, y, default=False)

                    needs_redraw = False
                    first_pass = False

                    pygame.time.set_timer(REDRAW, 0)
                    pygame.event.clear([REDRAW])
                    old_redraw_time = None
                    
                # Draw the mouse, if it needs drawing.
                renpy.display.draw.update_mouse()
                    
                # See if we want to restart the interaction entirely.
                if self.restart_interaction:                    
                    return True, None

                # Determine if we need a redraw.
                needs_redraw = needs_redraw or renpy.display.render.process_redraws()

                # Predict images, if we haven't done so already.

                while (prediction_coroutine is not None) \
                        and not needs_redraw \
                        and not self.event_peek() \
                        and not renpy.audio.music.is_playing("movie"):
                    
                    result = prediction_coroutine.next()
                    if not result:
                        prediction_coroutine = None
                        break

                # If we need to redraw again, do it if we don't have an
                # event going on.
                if needs_redraw and not self.event_peek():
                    if renpy.config.profile:
                        self.profile_time = get_time()
                    continue

                try:

                    # Times until events occur.
                    # We use large values to approximate infinity.
                    redraw_in = 3600
                    timeout_in = 3600
                    
                    # Handle the redraw timer.
                    redraw_time = renpy.display.render.redraw_time()

                    if redraw_time and not needs_redraw:

                        if redraw_time != old_redraw_time:
                            time_left = redraw_time - get_time()
                            time_left = min(time_left, 3600)
                            redraw_in = time_left
                            pygame.time.set_timer(REDRAW, max(int(time_left * 1000), 1))
                            old_redraw_time = redraw_time
                    else:
                        pygame.time.set_timer(REDRAW, 0)

                    # Handle the timeout timer.
                    if not self.timeout_time:
                        pygame.time.set_timer(TIMEEVENT, 0)
                        ev = None
                    else:
                        time_left = self.timeout_time - get_time() 
                        time_left = min(time_left, 3600)
                        redraw_in = time_left
                        
                        if time_left < 0:
                            self.timeout_time = None
                            ev = self.time_event
                            pygame.time.set_timer(TIMEEVENT, 0)
                        else:
                            ev = None

                            if self.timeout_time != old_timeout_time:
                                # Always set to at least 1ms.
                                pygame.time.set_timer(TIMEEVENT, int(time_left * 1000 + 1))
                                old_timeout_time = self.timeout_time

                    # Handle autosaving, as necessary.
                    if not did_autosave and not needs_redraw and not self.event_peek() and redraw_in > .25 and timeout_in > .25:
                        renpy.loadsave.autosave()
                        did_autosave = True
                        
                    # Get the event, if we don't have one already.
                    if ev is None:
                        if needs_redraw:
                            ev = self.event_poll()
                        else:
                            ev = self.event_wait()
                        
                    if ev.type == pygame.NOEVENT:
                        continue

                    if renpy.config.profile:
                        self.profile_time = get_time()
                    
                    # Try to merge an TIMEEVENT with the next event.
                    if ev.type == TIMEEVENT:
                        old_timeout_time = None
                        pygame.event.clear([TIMEEVENT])
                            
                    # On Android, where we have multiple mouse buttons, we can
                    # merge a mouse down and mouse up event with its successor. This 
                    # prevents us from getting overwhelmed with too many events on 
                    # a multitouch screen.
                    if android and (ev.type == pygame.MOUSEBUTTONDOWN or ev.type == pygame.MOUSEBUTTONUP):
                        pygame.event.clear(ev.type)
                            
                    # Handle redraw timeouts.
                    if ev.type == REDRAW:
                        old_redraw_time = None
                        continue

                    # Handle periodic events. This includes updating the mouse timers (and through the loop,
                    # the mouse itself), and the audio system periodic calls.
                    if ev.type == PERIODIC:
                        events = 1 + len(pygame.event.get([PERIODIC]))
                        self.ticks += events

                        if renpy.config.periodic_callback:
                            renpy.config.periodic_callback()

                        renpy.audio.audio.periodic()
                        continue

                    # Handle ffdecode events.
                    if renpy.audio.audio.event(ev):
                        continue
                                            
                    # This can set the event to None, to ignore it.
                    ev = renpy.display.joystick.event(ev)
                    if not ev:
                        continue

                    # Handle skipping.
                    renpy.display.behavior.skipping(ev)
                    
                    # Handle quit specially for now.
                    if ev.type == pygame.QUIT:
                        self.quit_event()
                        continue
                        
                    # Handle videoresize.
                    if ev.type == pygame.VIDEORESIZE:
                        evs = pygame.event.get([pygame.VIDEORESIZE])
                        if len(evs):
                            ev = evs[-1]

                        if self.last_resize != ev.size:
                            self.last_resize = ev.size
                            self.set_mode((ev.w, ev.h))

                        continue

                    if ev.type == pygame.MOUSEMOTION or \
                            ev.type == pygame.MOUSEBUTTONDOWN or \
                            ev.type == pygame.MOUSEBUTTONUP:
            
                        self.mouse_event_time = renpy.display.core.get_time()

                    
                    # Merge mousemotion events.
                    if ev.type == pygame.MOUSEMOTION:
                        evs = pygame.event.get([pygame.MOUSEMOTION])
                        if len(evs):
                            ev = evs[-1]

                        if renpy.windows:
                            self.focused = True
                            
                    # Handle focus notifications.
                    if ev.type == pygame.ACTIVEEVENT:
                        if ev.state & 1:
                            self.focused = ev.gain

                        if ev.state & 4:                            
                            if ev.gain:
                                self.restored()
                            else:
                                self.iconified()


                    # This returns the event location. It also updates the
                    # mouse state as necessary.
                    x, y = renpy.display.draw.mouse_event(ev)

                    if not self.focused:
                        x = -1
                        y = -1
                    
                    self.event_time = end_time = get_time()

                    # Handle the event normally.
                    rv = renpy.display.focus.mouse_handler(ev, x, y)

                    if rv is None:
                        rv = root_widget.event(ev, x, y, 0)

                    if rv is None:
                        rv = renpy.display.focus.key_handler(ev)

                    if rv is not None:
                        break
                    
                    # Handle displayable inspector.
                    if renpy.config.inspector and renpy.display.behavior.inspector(ev):
                        l = self.surftree.main_displayables_at_point(x, y, renpy.config.transient_layers + renpy.config.context_clear_layers + renpy.config.overlay_layers)
                        renpy.game.invoke_in_new_context(renpy.config.inspector, l)
                        
            
                except IgnoreEvent:
                    # An ignored event can change the timeout. So we want to
                    # process an TIMEEVENT to ensure that the timeout is
                    # set correctly.
                    try:
                        pygame.event.post(self.time_event)
                    except:
                        pass
                        

                # Check again after handling the event.
                needs_redraw |= renpy.display.render.process_redraws()

                if self.restart_interaction:
                    return True, None

            # If we were trans-paused and rv is true, suppress
            # transitions up to the next interaction.
            if trans_pause and rv:
                self.suppress_transition = True

                
            # But wait, there's more! The finally block runs some cleanup
            # after this.
            return False, rv

        finally:

            renpy.exports.say_attributes = None

            # Clean out the overlay layers.
            for i in renpy.config.overlay_layers:
                scene_lists.clear(i)

            # Stop ongoing preloading.
            renpy.display.im.cache.end_tick()
                
            # We no longer disable periodic between interactions.
            # pygame.time.set_timer(PERIODIC, 0)

            pygame.time.set_timer(TIMEEVENT, 0)
            pygame.time.set_timer(REDRAW, 0)

            renpy.game.context().runtime += end_time - start_time

            # Restart the old interaction, which also causes a
            # redraw if needed.
            self.restart_interaction = True

            # print "It took", frames, "frames."

    def timeout(self, offset):
        if offset < 0:
            return

        if self.timeout_time:
            self.timeout_time = min(self.event_time + offset, self.timeout_time)
        else:
            self.timeout_time = self.event_time + offset

