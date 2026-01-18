import tkinter as tk
from tkinter import filedialog, Menu
from PIL import Image, ImageTk, ImageSequence


class GifWindow(tk.Toplevel):
    def __init__(self, root, path):
        super().__init__(root)

        self.locked = False
        self.frames = []
        self.delays = []
        self.frame_index = 0

        # Load GIF
        gif = Image.open(path)
        for frame in ImageSequence.Iterator(gif):
            self.frames.append(ImageTk.PhotoImage(frame.convert("RGBA")))
            self.delays.append(frame.info.get("duration", 50))

        self.label = tk.Label(self, bg="black", bd=0)
        self.label.pack()

        # Window behavior
        self.overrideredirect(True)
        self.attributes("-topmost", False)

        # Transparency (works best on Windows)
        try:
            self.attributes("-transparentcolor", "black")
        except tk.TclError:
            pass

        self.geometry(f"{gif.width}x{gif.height}")

        # Dragging
        self.bind("<ButtonPress-1>", self.drag_start)
        self.bind("<B1-Motion>", self.drag_move)

        # Right-click menu
        self.menu = Menu(self, tearoff=0)
        self.menu.add_command(label="Lock", command=self.toggle_lock)
        self.menu.add_separator()
        self.menu.add_command(label="Close", command=self.destroy)
        self.bind("<Button-3>", self.show_menu)

        self.animate()

    # ---------------- Animation ----------------

    def animate(self):
        self.label.config(image=self.frames[self.frame_index])
        delay = self.delays[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.after(max(delay, 20), self.animate)

    # ---------------- Dragging ----------------

    def drag_start(self, event):
        if self.locked:
            return
        self._drag_x = event.x
        self._drag_y = event.y

    def drag_move(self, event):
        if self.locked:
            return
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.geometry(f"+{x}+{y}")

    # ---------------- Menu ----------------

    def toggle_lock(self):
        self.locked = not self.locked
        self.menu.entryconfig(
            0, label="Unlock" if self.locked else "Lock"
        )

    def show_menu(self, event):
        self.menu.tk_popup(event.x_root, event.y_root)


def main():
    root = tk.Tk()
    root.withdraw()

    while True:
        path = filedialog.askopenfilename(
            title="Choose a GIF",
            filetypes=[("GIF files", "*.gif")]
        )
        if not path:
            break
        GifWindow(root, path)

    root.mainloop()


if __name__ == "__main__":
    main()
