#!/usr/bin/env python3

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
gi.require_version("GdkPixbuf", "2.0")

from gi.repository import Gtk, Gdk, GdkPixbuf, GLib


class GifWindow(Gtk.ApplicationWindow):
    def __init__(self, app, gif_path):
        super().__init__(application=app)

        self.set_decorated(False)
        self.set_resizable(False)
        self.set_title("gif_runner")
        self.set_opacity(1.0)

        self.locked = False
        self.drag_x = 0
        self.drag_y = 0

        # Load GIF
        animation = GdkPixbuf.PixbufAnimation.new_from_file(gif_path)
        self.iter = animation.get_iter(None)
        pixbuf = self.iter.get_pixbuf()

        # Gtk.Picture (HiDPI-safe)
        self.picture = Gtk.Picture.new_for_pixbuf(pixbuf)
        self.picture.set_can_shrink(False)
        self.picture.set_keep_aspect_ratio(True)
        self.set_child(self.picture)

        # Window size
        self.set_default_size(pixbuf.get_width(), pixbuf.get_height())
        self.set_size_request(pixbuf.get_width(), pixbuf.get_height())

        # Drag controller
        drag = Gtk.GestureDrag()
        drag.connect("drag-begin", self.on_drag_begin)
        drag.connect("drag-update", self.on_drag_update)
        self.add_controller(drag)

        # Right-click menu
        click = Gtk.GestureClick(button=3)
        click.connect("pressed", self.on_right_click)
        self.add_controller(click)

        # Start animation
        self.tick()

        self.present()

    # ---------------- Animation ----------------

    def tick(self):
        if self.iter.advance(None):
            self.picture.set_pixbuf(self.iter.get_pixbuf())

        delay = self.iter.get_delay_time()
        GLib.timeout_add(max(delay, 20), self.tick)

    # ---------------- Dragging ----------------

    def on_drag_begin(self, gesture, start_x, start_y):
        if self.locked:
            return
        surface = self.get_surface()
        if surface:
            self.drag_x, self.drag_y = surface.get_position()

    def on_drag_update(self, gesture, offset_x, offset_y):
        if self.locked:
            return
        surface = self.get_surface()
        if surface:
            surface.move(
                int(self.drag_x + offset_x),
                int(self.drag_y + offset_y)
            )

    # ---------------- Context Menu ----------------

    def on_right_click(self, gesture, n_press, x, y):
        menu = Gtk.PopoverMenu()
        menu.set_has_arrow(False)
        menu.set_parent(self)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        lock_btn = Gtk.Button(
            label="Unlock" if self.locked else "Lock"
        )
        lock_btn.connect("clicked", self.toggle_lock)
        box.append(lock_btn)

        close_btn = Gtk.Button(label="Close")
        close_btn.connect("clicked", lambda *_: self.close())
        box.append(close_btn)

        menu.set_child(box)
        menu.popup()

    def toggle_lock(self, *_):
        self.locked = not self.locked
        self.set_title("gif_runner (locked)" if self.locked else "gif_runner")


class GifRunner(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.local.gifrunner")
        self.parent_window = None

    def do_activate(self):
        if not self.parent_window:
            self.parent_window = Gtk.ApplicationWindow(application=self)
            self.parent_window.set_default_size(1, 1)
            self.parent_window.set_visible(False)

        self.open_dialog()

    def open_dialog(self):
        dialog = Gtk.FileDialog(title="Choose a GIF")

        filter_gif = Gtk.FileFilter()
        filter_gif.set_name("GIF images")
        filter_gif.add_pattern("*.gif")
        dialog.set_default_filter(filter_gif)

        dialog.open(self.parent_window, None, self.on_file_chosen)

    def on_file_chosen(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            path = file.get_path()
            if path:
                GifWindow(self, path)
                self.open_dialog()
        except Exception:
            pass


if __name__ == "__main__":
    app = GifRunner()
    app.run()
