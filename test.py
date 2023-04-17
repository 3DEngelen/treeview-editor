import tkinter as tk
from tkinter import ttk
from pydantic import BaseModel


class Vehicle(BaseModel):
    name: str
    year: int
    color: str
    type: str


class TreeviewEdit(ttk.Treeview):
    def __init__(self, master, model, **kwargs):
        super().__init__(master, **kwargs)
        self._model = model
        self._populate_treeview(model)
        # bind mouse double click to self.on_double_click
        self.bind("<Double-1>", self.on_double_click, add="+")

    def _populate_treeview(self, model):
        # Create an instance of the Pydantic model to get the field names
        instance = Vehicle(name="", year=0, color="", type="")
        # Add columns to the treeview
        self["columns"] = [
            field.name for field in instance.__fields__.values() if field.name != "type"
        ]
        for col in self["columns"]:
            self.heading(col, text=col.capitalize())

        # Create a dictionary to group the vehicles by type
        vehicles_by_type = {}
        for item in model:
            # Create an instance of the Pydantic model for each item in the list
            vehicle = Vehicle(**item)
            if vehicle.type not in vehicles_by_type:
                vehicles_by_type[vehicle.type] = []
            vehicles_by_type[vehicle.type].append(vehicle)

        # Add data to the treeview
        for vehicle_type, vehicles in vehicles_by_type.items():
            type_node = self.insert("", tk.END, text=vehicle_type)
            for vehicle in vehicles:
                values = [
                    str(getattr(vehicle, field.name))
                    for field in vehicle.__fields__.values()
                ]
                self.insert(type_node, tk.END, text=vehicle.name, values=values)

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
            # Validate the entered value using the VehicleModel
            current_values = self.item(selected_iid).get("values")
            new_values = list(current_values)
            new_values[column_index - 1] = new_text
            try:
                vehicle = Vehicle(
                    vehicle_name=new_values[0], year=new_values[1], color=new_values[2]
                )
            except ValueError as error:
                # If validation fails, show an error message and return
                error_message = tk.Toplevel(self)
                error_message.title("Error")
                tk.Label(error_message, text=str(error)).pack()
                return
            # Update the values of the selected column index
            self.item(selected_iid, values=new_values)
        # After updating the text, destroy the entry widget
        event.widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test TreeviewEdit")

    # Create data using the Pydantic model
    vehicle_data = [
        {
            "name": "Nissan Versa",
            "year": 2018,
            "color": "Black",
            "type": "Sedan",
        },
        {
            "name": "Honda Civic",
            "year": 2019,
            "color": "White",
            "type": "Sedan",
        },
        {
            "name": "Toyota Corolla",
            "year": 2020,
            "color": "Red",
            "type": "Sedan",
        },
        {
            "name": "Ford Mustang",
            "year": 2017,
            "color": "Blue",
            "type": "Muscle Car",
        },
        {
            "name": "Chevrolet Camaro",
            "year": 2015,
            "color": "Yellow",
            "type": "Muscle Car",
        },
    ]
    treeview_edit = TreeviewEdit(root, vehicle_data)
    treeview_edit.pack(expand=True, fill="both")

    root.mainloop()
