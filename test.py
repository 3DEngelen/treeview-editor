import tkinter as tk
from tkinter import ttk


class TreeviewEdit(ttk.Treeview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        # bind mouse double click to self.on_double_click
        self.bind("<Double-1>", self.on_double_click, add="+")

    def on_double_click(self, event):
        # identify what region was Double clicked
        region_clicked = self.identify("region", event.x, event.y)

        # Only edit cell and tree region
        if region_clicked not in ("tree", "cell"):
            return

        # Which item was Double clicked
        column_clicked = self.identify_column(event.x)
        # For Example: #0 will become 0
        column_index = int(column_clicked[1:])
        # Get the item id
        # For Example: I001
        selected_iid = self.focus()

        # This will contain both text and values from the selected iid
        # For Example: ('Nissan Versa', '2018', 'Black')
        selected_values = self.item(selected_iid)

        # If the column clicked is the first column
        if column_clicked == "#0":
            # Edit the text of the selected iid
            selected_text = selected_values.get("text")
        else:
            # Edit the value of the selected iid and selected column index
            # (-1 because index starts at 0)
            try:
                selected_text = selected_values.get("values")[column_index - 1]
            except IndexError:
                # If the selected column index is out of range, return
                return

        # Get the bbox of the selected column
        colomn_box = self.bbox(selected_iid, column=column_clicked)

        # Create an Entry widget and place it on the selected column,
        # make the size of the entry the same as the column
        entry_edit = tk.Entry(root, width=colomn_box[2])

        # Record the column index of the selected column and the selected item iid
        entry_edit.editing_column_index = column_index
        entry_edit.editing_item_iid = selected_iid

        # Set the text of the entry to the selected text
        entry_edit.insert(0, selected_text)
        entry_edit.select_range(0, tk.END)
        # Set focus on the entry
        entry_edit.focus()

        # When the entry loses focus, call self.on_focus_out
        entry_edit.bind(
            "<FocusOut>",
            self.on_focus_out,
        )

        # When the user presses the enter key, call self.on_enter_pressed
        entry_edit.bind(
            "<Return>",
            self.on_enter_pressed,
        )

        # Place the entry on the selected column
        entry_edit.place(
            x=colomn_box[0], y=colomn_box[1], w=colomn_box[2], h=colomn_box[3]
        )

    def on_focus_out(self, event):
        # Destroy the entry widget
        event.widget.destroy()

    def on_enter_pressed(self, event):
        # Get the new text from the entry widget
        new_text = event.widget.get()

        # For Example: I002
        selected_iid = event.widget.editing_item_iid

        # For Example: -1 (tree column), 0 (first column), 1 (second column)
        column_index = event.widget.editing_column_index

        if column_index == 0:
            # Update the text of the selected iid (First item of the tree)
            self.item(selected_iid, text=new_text)
        else:
            # Select the values of the selected iid
            current_values = self.item(selected_iid).get("values")
            # update the value of the selected column index
            current_values[column_index - 1] = new_text
            # Update the values of the selected iid in the tree view
            self.item(selected_iid, values=current_values)
        # After updating the text, destroy the entry widget
        event.widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test TreeviewEdit")
    # Add data to the treeview
    column_names = ("vehicle_name", "year", "color")

    treeview_vehicles = TreeviewEdit(root, columns=column_names)

    treeview_vehicles.heading("#0", text="Vehicle Type")
    treeview_vehicles.heading("vehicle_name", text="Vehicle Name")
    treeview_vehicles.heading("year", text="Year")
    treeview_vehicles.heading("color", text="Color")
    # First element of the tree
    sedan_row = treeview_vehicles.insert(parent="", index=tk.END, text="Sedan")
    # Add data to the treeview
    treeview_vehicles.insert(
        parent=sedan_row, index=tk.END, values=("Nissan Versa", "2018", "Black")
    )
    treeview_vehicles.insert(
        parent=sedan_row, index=tk.END, values=("Toyota Camry", "2019", "White")
    )

    treeview_vehicles.pack(fill=tk.BOTH, expand=True)

    root.mainloop()
