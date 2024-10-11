import tkinter as tk

# Sample data for autocomplete (you can replace this with any large dataset)
WORDS = [
    "Apple", "Apricot", "Avocado", "Banana", "Blackberry", "Blueberry",
    "Cantaloupe", "Cherry", "Coconut", "Cranberry", "Date", "Dragonfruit",
    "Elderberry", "Fig", "Grape", "Grapefruit", "Kiwi", "Lemon",
    "Lime", "Mango", "Melon", "Orange", "Papaya", "Peach", "Pear",
    "Pineapple", "Plum", "Raspberry", "Strawberry", "Tangerine",
    "Watermelon", "Zucchini"
]

class AutocompleteApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Autocomplete Example")
        self.master.geometry("300x200")

        # Entry widget for user input
        self.entry = tk.Entry(master)
        self.entry.pack(pady=20, padx=20)
        self.entry.bind("<KeyRelease>", self.on_key_release)  # Bind key release event

        # Listbox to display suggestions
        self.listbox = tk.Listbox(master)
        self.listbox.pack(pady=5, padx=20, fill=tk.X)

        self.listbox.bind("<ButtonRelease-1>", self.on_listbox_select)  # Bind click event

    def on_key_release(self, event):
        # Clear the current suggestions
        self.listbox.delete(0, tk.END)

        # Get the text from the entry
        typed_text = self.entry.get()
        if typed_text:  # Only if there is text
            for word in WORDS:
                if word.lower().startswith(typed_text.lower()):  # Match case-insensitively
                    self.listbox.insert(tk.END, word)  # Add matching word to listbox

    def on_listbox_select(self, event):
        # Get the selected word from the listbox and set it to the entry
        selected_word = self.listbox.get(self.listbox.curselection())
        self.entry.delete(0, tk.END)  # Clear the entry
        self.entry.insert(0, selected_word)  # Insert the selected word
        self.listbox.delete(0, tk.END)  # Clear the listbox suggestions


# Main application
root = tk.Tk()
app = AutocompleteApp(root)
root.mainloop()
