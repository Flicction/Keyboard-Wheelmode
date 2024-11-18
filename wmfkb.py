import time
import pyvjoy # type: ignore
import tkinter as tk
from tkinter import simpledialog, messagebox
from threading import Thread
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import keyboard
import webbrowser

# Initialize vJoy device
try:
    vj = pyvjoy.VJoyDevice(1)
except pyvjoy.exceptions.vJoyFailedToAcquireException:
    messagebox.showerror("Error", "VJoy device 1 is already in use")
    exit()
except Exception as e:
    if "No VJD" in str(e) or "VJD does not exist" in str(e):
        messagebox.showerror("Error", "No vJoy device found")
        exit()
    else:
        raise

# Global variable to track steering input
current_x_axis_value = 0

# Default settings
default_settings = {
    "steer_left_binding": "a",  # Default to 'A' for steering left
    "steer_right_binding": "d",  # Default to 'D' for steering right
    "pause_steering_reset_binding": "",  # Default to unbound
    "linearity": 100,             # Default linearity
    "sensitivity": 10,           # Default sensitivity
    "release_sensitivity": 15,   # Default sensitivity on release
    "sensitivity_when_paused": 3, # Default Sensitivity when Paused
    "countersteer_multiplier": 2,  # Default countersteer multiplier
    "fullsteer_left_binding": "",  # Default to unbound for fullsteer left
    "fullsteer_right_binding": "",  # Default to unbound for fullsteer right
    "snap_to_action_key_multiplier": 1,  # Default snap to action key multiplier
    "action_keys": [],  # Default empty action keys
    "permanent_max_lock": 100
}

# Function to load settings from a file
def load_settings(profile_name="default"):
    settings_file = f"keyboard_{profile_name}_settings.json"
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)
    return default_settings.copy()  # Return default settings

# Function to save settings to a file
def save_settings(settings, profile_name="default"):
    # Convert StringVar to string before saving
    for key, value in settings.items():
        if isinstance(value, tk.StringVar):
            settings[key] = value.get()
        elif isinstance(value, list):  # Handle lists like action_keys
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, tk.StringVar):
                            item[k] = v.get()

    settings_file = f"keyboard_{profile_name}_settings.json"
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=4)  # Save with indentation for better readability

# Function to save the selected profile
def save_selected_profile(profile_name):
    with open("selected_profile.json", 'w') as f:
        json.dump({"selected_profile": profile_name}, f)

# Function to load the selected profile
def load_selected_profile():
    if os.path.exists("selected_profile.json"):
        with open("selected_profile.json", 'r') as f:
            data = json.load(f)
            return data.get("selected_profile", "default")
    return "default"

# Function to rename the current profile
def rename_profile():
    current_profile = profile_var.get()
    new_name = simpledialog.askstring("Rename Profile", f"Enter a new name for the profile '{current_profile}':")
    if new_name and not os.path.exists(f"keyboard_{new_name}_settings.json"):
        os.rename(f"keyboard_{current_profile}_settings.json",
                  f"keyboard_{new_name}_settings.json")
        profile_var.set(new_name)
        update_profile_menu(new_name)
    elif os.path.exists(f"keyboard_{new_name}_settings.json"):
        tk.messagebox.showerror("Error", f"The profile '{new_name}' already exists. Please choose a different name.")

# Function to update the profile menu to reflect the new name
def update_profile_menu(new_name):
    profile_menu['menu'].delete(0, 'end')
    profiles = [f.replace("keyboard_", "").replace("_settings.json", "") for f in os.listdir(".") if f.startswith("keyboard_")]
    for profile in profiles:
        profile_menu['menu'].add_command(label=profile, command=lambda p=profile: profile_var.set(p))
    profile_var.set(new_name)

# Function to create a new profile
def create_new_profile():
    new_profile_name = simpledialog.askstring("Create New Profile", "Enter a name for the new profile:")
    if new_profile_name and not os.path.exists(f"keyboard_{new_profile_name}_settings.json"):
        profile_var.set(new_profile_name)
        save_settings(settings, new_profile_name)
        update_profile_menu(new_profile_name)
    elif os.path.exists(f"keyboard_{new_profile_name}_settings.json"):
        tk.messagebox.showerror("Error", f"The profile '{new_profile_name}' already exists. Please choose a different name.")

# Tkinter UI setup
root = tk.Tk()
root.title("Wheelmode for Keyboard")

# UI for profile management at the top
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

# Profile management
profile_var = tk.StringVar(root)
selected_profile_name = load_selected_profile()
profile_var.set(selected_profile_name)
profile_menu = tk.OptionMenu(top_frame, profile_var, "default")
profile_menu.pack(side=tk.LEFT, padx=(5, 5))

# Button for renaming the current profile
rename_profile_button = tk.Button(top_frame, text="Rename Current Profile", command=rename_profile)
rename_profile_button.pack(side=tk.LEFT, padx=(5, 5))

# Button for creating a new profile
new_profile_button = tk.Button(top_frame, text="New Profile", command=create_new_profile)
new_profile_button.pack(side=tk.LEFT, padx=(5, 10))

# Load settings for the selected profile
settings = load_settings(profile_var.get())
steer_left_binding = settings.get("steer_left_binding", default_settings["steer_left_binding"])
steer_right_binding = settings.get("steer_right_binding", default_settings["steer_right_binding"])
pause_steering_reset_binding = settings.get("pause_steering_reset_binding", default_settings["pause_steering_reset_binding"])
linearity_value = settings.get("linearity", default_settings["linearity"])
sensitivity_value = settings.get("sensitivity", default_settings["sensitivity"])
release_sensitivity_value = settings.get("release_sensitivity", default_settings["release_sensitivity"])
sensitivity_when_paused_value = settings.get("sensitivity_when_paused", default_settings["sensitivity_when_paused"])
countersteer_multiplier_value = settings.get("countersteer_multiplier", default_settings["countersteer_multiplier"])
snap_to_action_key_multiplier_value = settings.get("snap_to_action_key_multiplier", default_settings["snap_to_action_key_multiplier"])
action_keys = settings.get("action_keys", default_settings["action_keys"])
permanent_max_lock = settings.get("permanent_max_lock", default_settings["permanent_max_lock"])
fullsteer_left_binding = settings.get("fullsteer_left_binding", default_settings["fullsteer_left_binding"])
fullsteer_right_binding = settings.get("fullsteer_right_binding", default_settings["fullsteer_right_binding"])

# Function to update the selected profile in the UI and settings
def update_selected_profile(*args):
    profile_name = profile_var.get()
    save_selected_profile(profile_name)
    global settings, steer_left_binding, steer_right_binding, linearity_value, sensitivity_value, release_sensitivity_value, countersteer_multiplier_value, snap_to_action_key_multiplier_value, action_keys, fullsteer_left_binding, fullsteer_right_binding
    settings = load_settings(profile_name)
    
    steer_left_binding = settings.get("steer_left_binding", default_settings["steer_left_binding"])
    steer_right_binding = settings.get("steer_right_binding", default_settings["steer_right_binding"])
    pause_steering_reset_binding = settings.get("pause_steering_reset_binding", default_settings["pause_steering_reset_binding"])
    linearity_value = settings.get("linearity", default_settings["linearity"])
    sensitivity_value = settings.get("sensitivity", default_settings["sensitivity"])
    release_sensitivity_value = settings.get("release_sensitivity", default_settings["release_sensitivity"])
    countersteer_multiplier_value = settings.get("countersteer_multiplier", default_settings["countersteer_multiplier"])
    snap_to_action_key_multiplier_value = settings.get("snap_to_action_key_multiplier", default_settings["snap_to_action_key_multiplier"])
    action_keys = settings.get("action_keys", default_settings["action_keys"])
    fullsteer_left_binding = settings.get("fullsteer_left_binding", default_settings["fullsteer_left_binding"])
    fullsteer_right_binding = settings.get("fullsteer_right_binding", default_settings["fullsteer_right_binding"])
    permanent_max_lock_var.set(settings.get("permanent_max_lock", default_settings["permanent_max_lock"]))

    # Update all entries without calling update_graph multiple times
    linearity_entry.delete(0, tk.END)
    linearity_entry.insert(0, str(linearity_value))

    sensitivity_entry.delete(0, tk.END)
    sensitivity_entry.insert(0, str(sensitivity_value))

    release_sensitivity_entry.delete(0, tk.END)
    release_sensitivity_entry.insert(0, str(release_sensitivity_value))

    countersteer_multiplier_entry.delete(0, tk.END)
    countersteer_multiplier_entry.insert(0, str(countersteer_multiplier_value))

    snap_to_action_key_multiplier_entry.delete(0, tk.END)
    snap_to_action_key_multiplier_entry.insert(0, str(snap_to_action_key_multiplier_value))

    # Update the graph after updating all settings
    update_graph()

profile_var.trace("w", update_selected_profile)

# Wheelmode label
frame = tk.Frame(root)
frame.pack(pady=10)

wheelmode_label = tk.Label(frame, text="Wheelmode", font=("Helvetica", 16))
wheelmode_label.grid(row=0, column=0, padx=5)

# Function to validate that only numeric input is allowed, with exception for "."
def validate_numeric_input(new_value):
    if new_value.isdigit() or new_value == "" or new_value == "." or (new_value.count('.') == 1 and new_value.replace('.', '').isdigit()):  # Allow digits, dot, and empty string (for deletion)
        return True
    return False

# Create a Tkinter validation command
vcmd = (root.register(validate_numeric_input), '%P')

# Function to handle value changes and immediate save
def on_value_change(entry, setting_key):
    def callback(*args):
        settings[setting_key] = float(entry.get()) if '.' in entry.get() else int(entry.get())
        save_settings(settings, profile_var.get())
        update_selected_profile()
    return callback

# Deselect after 5s
def auto_deselect(entry_widget):
    # Ensure only one timer is active at any time
    if hasattr(entry_widget, "deselect_id") and entry_widget.deselect_id is not None:
        entry_widget.after_cancel(entry_widget.deselect_id)  # Cancel any existing timer

    # Function to remove focus (deselect the entry)
    def remove_focus():
        frame.focus_set()  # Set focus to the parent frame or another widget to deselect the entry
        entry_widget.deselect_id = None  # Reset the timer ID after removal

    # Reset the 5-second timer every time there is activity
    def reset_timer(event=None):
        # Cancel any existing timer to prevent overlaps
        if hasattr(entry_widget, "deselect_id") and entry_widget.deselect_id is not None:
            entry_widget.after_cancel(entry_widget.deselect_id)

        # Start a new 5-second timer
        entry_widget.deselect_id = entry_widget.after(5000, remove_focus)

    # Bind events to reset the timer on keypress or when the user clicks on the box
    entry_widget.bind("<KeyPress>", reset_timer)  # Reset timer when typing
    entry_widget.bind("<FocusIn>", reset_timer)   # Reset timer when the box is clicked or focused

    # Cancel the timer if the box loses focus, but only if a valid timer exists
    entry_widget.bind("<FocusOut>", lambda event: (
        entry_widget.after_cancel(entry_widget.deselect_id) if hasattr(entry_widget, "deselect_id") and entry_widget.deselect_id is not None else None
    ))

    # Start the timer when the box is first focused
    reset_timer()

linearity_label = tk.Label(frame, text="Linearity", font=("Helvetica", 12))
linearity_label.grid(row=1, column=0, padx=5, pady=5)
linearity_entry = tk.Entry(frame, width=5, validate='key', validatecommand=vcmd)
linearity_entry.insert(0, str(linearity_value))
linearity_entry.grid(row=1, column=1, padx=5, pady=5)
linearity_entry.bind("<FocusOut>", on_value_change(linearity_entry, "linearity"))
auto_deselect(linearity_entry)  # Apply auto-deselect logic to this entry

# Sensitivity label and input with validation
sensitivity_label = tk.Label(frame, text="Sensitivity", font=("Helvetica", 12))
sensitivity_label.grid(row=2, column=0, padx=5, pady=5)
sensitivity_entry = tk.Entry(frame, width=5, validate='key', validatecommand=vcmd)
sensitivity_entry.insert(0, str(sensitivity_value))
sensitivity_entry.grid(row=2, column=1, padx=5, pady=5)
sensitivity_entry.bind("<FocusOut>", on_value_change(sensitivity_entry, "sensitivity"))
auto_deselect(sensitivity_entry)

# Sensitivity on release label and input with validation
release_sensitivity_label = tk.Label(frame, text="Sensitivity on Release", font=("Helvetica", 12))
release_sensitivity_label.grid(row=3, column=0, padx=5, pady=5)
release_sensitivity_entry = tk.Entry(frame, width=5, validate='key', validatecommand=vcmd)
release_sensitivity_entry.insert(0, str(release_sensitivity_value))
release_sensitivity_entry.grid(row=3, column=1, padx=5, pady=5)
release_sensitivity_entry.bind("<FocusOut>", on_value_change(release_sensitivity_entry, "release_sensitivity"))
auto_deselect(release_sensitivity_entry)

# Sensitivity when Paused label and input with validation
sensitivity_when_paused_label = tk.Label(frame, text="Sensitivity when Paused", font=("Helvetica", 12))
sensitivity_when_paused_label.grid(row=4, column=0, padx=5, pady=5)
sensitivity_when_paused_entry = tk.Entry(frame, width=5, validate='key', validatecommand=vcmd)
sensitivity_when_paused_entry.insert(0, str(settings.get("sensitivity_when_paused", 2)))
sensitivity_when_paused_entry.grid(row=4, column=1, padx=5, pady=5)
sensitivity_when_paused_entry.bind("<FocusOut>", on_value_change(sensitivity_when_paused_entry, "sensitivity_when_paused"))
auto_deselect(sensitivity_when_paused_entry)

# Countersteer Multiplier label and input with validation
countersteer_multiplier_label = tk.Label(frame, text="Countersteer Multiplier", font=("Helvetica", 12))
countersteer_multiplier_label.grid(row=5, column=0, padx=5, pady=5)
countersteer_multiplier_entry = tk.Entry(frame, width=5, validate='key', validatecommand=vcmd)
countersteer_multiplier_entry.insert(0, str(countersteer_multiplier_value))
countersteer_multiplier_entry.grid(row=5, column=1, padx=5, pady=5)
countersteer_multiplier_entry.bind("<FocusOut>", on_value_change(countersteer_multiplier_entry, "countersteer_multiplier"))
auto_deselect(countersteer_multiplier_entry)

# Snap to Action Key Multiplier label and input with validation
snap_to_action_key_multiplier_label = tk.Label(frame, text="Snap to Action Key Multiplier", font=("Helvetica", 12))
snap_to_action_key_multiplier_label.grid(row=6, column=0, padx=5, pady=5)
snap_to_action_key_multiplier_entry = tk.Entry(frame, width=5, validate='key', validatecommand=vcmd)
snap_to_action_key_multiplier_entry.insert(0, str(snap_to_action_key_multiplier_value))
snap_to_action_key_multiplier_entry.grid(row=6, column=1, padx=5, pady=5)
snap_to_action_key_multiplier_entry.bind("<FocusOut>", on_value_change(snap_to_action_key_multiplier_entry, "snap_to_action_key_multiplier"))
auto_deselect(snap_to_action_key_multiplier_entry)

# Permanent Max Lock label and input with validation
permanent_max_lock_label = tk.Label(frame, text="Permanent Max Lock (%)", font=("Helvetica", 12))
permanent_max_lock_label.grid(row=10, column=0, padx=5, pady=5)
permanent_max_lock_var = tk.IntVar(value=settings.get("permanent_max_lock", 100))
permanent_max_lock_entry = tk.Entry(frame, width=5, validate='key', validatecommand=vcmd)
permanent_max_lock_entry.insert(0, str(permanent_max_lock_var.get()))
permanent_max_lock_entry.grid(row=10, column=1, padx=5, pady=5)
permanent_max_lock_entry.bind("<FocusOut>", on_value_change(permanent_max_lock_entry, "permanent_max_lock"))
auto_deselect(permanent_max_lock_entry)

# Ensure the value stays between 1 and 100
def validate_permanent_max_lock_input(value):
    try:
        value = int(value)
        return 1 <= value <= 100
    except ValueError:
        return False

# Function to bind the Pause Steering Reset button
def bind_pause_steering_reset():
    def on_key_press(event):
        global pause_steering_reset_binding
        pause_steering_reset_binding = event.keysym
        pause_steering_reset_var.set(pause_steering_reset_binding)  # Update the button label
        pause_steering_reset_window.unbind("<Key>")
    pause_steering_reset_window.bind("<Key>", on_key_press)

# Function to unbind the Pause Steering Reset button
def unbind_pause_steering_reset():
    global pause_steering_reset_binding
    pause_steering_reset_binding = ""
    pause_steering_reset_var.set("Not Set")

# Full function for the steering bindings window
def open_steering_bindings_window():
    global pause_steering_reset_window, pause_steering_reset_var
    steering_window = tk.Toplevel(root)
    steering_window.title("Bind Steering")

    # Steer Left Binding
    tk.Label(steering_window, text="Steer Left").grid(row=0, column=0, padx=5, pady=5)
    steer_left_var = tk.StringVar(steering_window)
    steer_left_var.set(steer_left_binding)  # Default to current steering left binding
    steer_left_button = tk.Button(steering_window, textvariable=steer_left_var, width=10)
    steer_left_button.grid(row=0, column=1, padx=5, pady=5)

    # Steer Right Binding
    tk.Label(steering_window, text="Steer Right").grid(row=1, column=0, padx=5, pady=5)
    steer_right_var = tk.StringVar(steering_window)
    steer_right_var.set(steer_right_binding)  # Default to current steering right binding
    steer_right_button = tk.Button(steering_window, textvariable=steer_right_var, width=10)
    steer_right_button.grid(row=1, column=1, padx=5, pady=5)

    # Adding the horizontal line after Steer Right row
    tk.Frame(steering_window, height=2, bd=1, relief=tk.SUNKEN).grid(row=2, columnspan=3, padx=5, pady=10, sticky="ew")

    # Function to bind keys to the buttons
    def bind_key(button, var):
        def on_key_press(event):
            var.set(event.keysym)
            steering_window.unbind("<Key>")
            button.config(text=event.keysym)
        steering_window.bind("<Key>", on_key_press)

    # Bind buttons for Steer Left and Steer Right
    steer_left_button.config(command=lambda: bind_key(steer_left_button, steer_left_var))
    steer_right_button.config(command=lambda: bind_key(steer_right_button, steer_right_var))

    # Save button for steering bindings
    def save_bindings():
        global steer_left_binding, steer_right_binding
        steer_left_binding = steer_left_var.get()
        steer_right_binding = steer_right_var.get()
        settings["steer_left_binding"] = steer_left_binding
        settings["steer_right_binding"] = steer_right_binding
        settings["pause_steering_reset_binding"] = pause_steering_reset_binding
        save_settings(settings, profile_var.get())
        steering_window.destroy()

    # Save button
    tk.Button(steering_window, text="Save", command=save_bindings).grid(row=4, column=0, columnspan=2, pady=10)

    # Pause Steering Reset binding UI
    tk.Label(steering_window, text="Pause Steering Reset").grid(row=3, column=0, padx=5, pady=5)
    pause_steering_reset_var = tk.StringVar(steering_window)
    pause_steering_reset_var.set(pause_steering_reset_binding)  # Default to unbound
    pause_steering_reset_button = tk.Button(steering_window, textvariable=pause_steering_reset_var, width=10, command=bind_pause_steering_reset)
    pause_steering_reset_button.grid(row=3, column=1, padx=5, pady=5)

    # Unbind button for Pause Steering Reset
    unbind_pause_steering_reset_button = tk.Button(steering_window, text="Unbind", command=unbind_pause_steering_reset)
    unbind_pause_steering_reset_button.grid(row=3, column=2, padx=5, pady=5)

    # Make pause_steering_reset_window point to this steering window for binding
    pause_steering_reset_window = steering_window

bind_steering_button = tk.Button(frame, text="Bind Steering", command=open_steering_bindings_window)
bind_steering_button.grid(row=7, column=0, columnspan=2, pady=10)

# Fullsteer Bindings Button and Window
def open_fullsteer_bindings_window():
    fullsteer_window = tk.Toplevel(root)
    fullsteer_window.title("Bind Fullsteer Keys")

    # Fullsteer Left Binding
    tk.Label(fullsteer_window, text="Fullsteer Left").grid(row=0, column=0, padx=5, pady=5)
    fullsteer_left_var = tk.StringVar(fullsteer_window)
    fullsteer_left_var.set(settings.get("fullsteer_left_binding", ""))  # Default to unbound
    fullsteer_left_button = tk.Button(fullsteer_window, textvariable=fullsteer_left_var, width=10)
    fullsteer_left_button.grid(row=0, column=1, padx=5, pady=5)

    # Fullsteer Right Binding
    tk.Label(fullsteer_window, text="Fullsteer Right").grid(row=1, column=0, padx=5, pady=5)
    fullsteer_right_var = tk.StringVar(fullsteer_window)
    fullsteer_right_var.set(settings.get("fullsteer_right_binding", ""))  # Default to unbound
    fullsteer_right_button = tk.Button(fullsteer_window, textvariable=fullsteer_right_var, width=10)
    fullsteer_right_button.grid(row=1, column=1, padx=5, pady=5)

    # Unbind Buttons
    unbind_fullsteer_left_button = tk.Button(fullsteer_window, text="Unbind", command=lambda: fullsteer_left_var.set(""))
    unbind_fullsteer_left_button.grid(row=0, column=2, padx=5, pady=5)

    unbind_fullsteer_right_button = tk.Button(fullsteer_window, text="Unbind", command=lambda: fullsteer_right_var.set(""))
    unbind_fullsteer_right_button.grid(row=1, column=2, padx=5, pady=5)

    # Checkbox for Snap to Center
    snap_to_center_var = tk.BooleanVar(value=settings.get("snap_to_center", False))  # Default to off
    snap_to_center_checkbox = tk.Checkbutton(fullsteer_window, text="Snap to Center when Released", variable=snap_to_center_var)
    snap_to_center_checkbox.grid(row=2, column=0, columnspan=3, pady=5)

    # Function to bind keys to the buttons
    def bind_key(button, var):
        def on_key_press(event):
            var.set(event.keysym)
            fullsteer_window.unbind("<Key>")
            button.config(text=event.keysym)
        fullsteer_window.bind("<Key>", on_key_press)

    # Bind the buttons to listen for key presses
    fullsteer_left_button.config(command=lambda: bind_key(fullsteer_left_button, fullsteer_left_var))
    fullsteer_right_button.config(command=lambda: bind_key(fullsteer_right_button, fullsteer_right_var))

    # Save Button
    def save_fullsteer_bindings():
        settings["fullsteer_left_binding"] = fullsteer_left_var.get()
        settings["fullsteer_right_binding"] = fullsteer_right_var.get()
        settings["snap_to_center"] = snap_to_center_var.get()

        save_settings(settings, profile_var.get())

        # Reload the fullsteer bindings immediately
        global fullsteer_left_binding, fullsteer_right_binding
        fullsteer_left_binding = settings["fullsteer_left_binding"]
        fullsteer_right_binding = settings["fullsteer_right_binding"]

        fullsteer_window.destroy()

    tk.Button(fullsteer_window, text="Save", command=save_fullsteer_bindings).grid(row=3, column=0, columnspan=3, pady=10)

bind_fullsteer_button = tk.Button(frame, text="Bind Fullsteer Keys", command=open_fullsteer_bindings_window)
bind_fullsteer_button.grid(row=8, column=0, columnspan=2, pady=10)

# Ensure that the action_keys list is properly initialized if not already present in the settings
if "action_keys" not in settings:
    settings["action_keys"] = []  # Initialize as an empty list if not present

# Global variable to track the action keys window
action_keys_window = None

def open_action_keys_window():
    global action_keys_window
    
    # Close any existing action keys window before opening a new one
    if action_keys_window is not None and action_keys_window.winfo_exists():
        action_keys_window.destroy()
    
    action_keys_window = tk.Toplevel(root)
    action_keys_window.title("Configure Action Keys")

    # Function to bind keys to buttons
    def bind_key(button, var):
        if not isinstance(var, tk.StringVar):
            var = tk.StringVar(value=var)  # Ensure `var` is a StringVar

        def on_key_press(event):
            var.set(event.keysym)  # Correctly set the key to StringVar
            action_keys_window.unbind("<Key>")  # Unbind after key press
            button.config(text=var.get())  # Update button text with the key press
        
        action_keys_window.bind("<Key>", on_key_press)

    def add_action_key():
        if len(action_keys) < 10:  # Limit to 10 action keys
            new_action_key = {
                "binding": tk.StringVar(value="Not Set"),  # Initialize binding as StringVar
                "cap_percentage": tk.StringVar(value="50"),  # Initialize cap_percentage as StringVar
            }
            action_keys.append(new_action_key)
            update_action_keys_window()  # Immediately update the window to show the new key
            bind_key_to_button(new_action_key)  # Immediately enable binding for the new key

    # Function to immediately clamp cap percentage values and reset the input if needed
    def save_cap_percentage(event, cap_entry, cap_var):
        try:
            cap_value = int(cap_entry.get())
            if cap_value > 100:
                cap_value = 100  # Reset to maximum if above 100
                cap_entry.delete(0, tk.END)
                cap_entry.insert(0, "100")
            cap_value = max(1, min(cap_value, 100))  # Clamp between 1 and 100
            cap_var.set(str(cap_value))  # Update the StringVar
        except ValueError:
            pass  # Ignore invalid values

    # Function to bind the action key button immediately after adding a new key
    def bind_key_to_button(action_key):
        bind_button = tk.Button(action_keys_window, textvariable=action_key["binding"], width=15)
        bind_button.grid(row=len(action_keys)-1, column=2, padx=5, pady=5)
        bind_button.config(command=lambda ak=action_key: bind_key(bind_button, ak["binding"]))

    def delete_action_key(index):
        if 0 <= index < len(action_keys):
            action_keys.pop(index)
            update_action_keys_window()

    def save_action_keys():
        # Ensure all bindings and cap_percentages are converted to StringVar if needed
        for ak in action_keys:
            if not isinstance(ak["binding"], tk.StringVar):
                ak["binding"] = tk.StringVar(value=ak["binding"])
            if not isinstance(ak["cap_percentage"], tk.StringVar):
                ak["cap_percentage"] = tk.StringVar(value=ak["cap_percentage"])

        # Save each action key's binding and cap percentage to the settings
        settings["action_keys"] = [
            {
                "binding": ak["binding"].get() if isinstance(ak["binding"], tk.StringVar) else ak["binding"],
                "cap_percentage": min(100, int(ak["cap_percentage"].get()))  # Clamp the value at 100
            }
            for ak in action_keys
        ]
        save_settings(settings, profile_var.get())  # Save the updated settings
        action_keys_window.destroy()

    def update_action_keys_window():
        for widget in action_keys_window.winfo_children():
            widget.destroy()

        for index, action_key in enumerate(action_keys):
            # Ensure binding and cap_percentage are StringVars
            if not isinstance(action_key["binding"], tk.StringVar):
                action_key["binding"] = tk.StringVar(value=action_key["binding"])
            if not isinstance(action_key["cap_percentage"], tk.StringVar):
                action_key["cap_percentage"] = tk.StringVar(value=action_key["cap_percentage"])

            # Display Action Key label
            tk.Label(action_keys_window, text=f"Action Key {index + 1}").grid(row=index, column=0, padx=5, pady=5)

            # Display Cap Percentage Entry
            cap_entry = tk.Entry(action_keys_window, textvariable=action_key["cap_percentage"], width=5)
            cap_entry.grid(row=index, column=1, padx=5, pady=5)
            cap_entry.bind("<FocusOut>", lambda event, entry=cap_entry, var=action_key["cap_percentage"]: save_cap_percentage(event, entry, var))

            # Display Binding Button
            bind_button = tk.Button(action_keys_window, textvariable=action_key["binding"], width=15)
            bind_button.grid(row=index, column=2, padx=5, pady=5)

            # Unbind Button
            unbind_button = tk.Button(action_keys_window, text="Unbind", command=lambda ak=action_key: ak["binding"].set(""))
            unbind_button.grid(row=index, column=3, padx=5, pady=5)

            # Delete Button
            delete_button = tk.Button(action_keys_window, text="Delete", command=lambda i=index: delete_action_key(i))
            delete_button.grid(row=index, column=4, padx=5, pady=5)

            # Bind the button to listen for key presses
            bind_button.config(command=lambda ak=action_key: bind_key(bind_button, ak["binding"]))

        # Only show the Add Button if there are less than 10 action keys
        if len(action_keys) < 10:
            add_button = tk.Button(action_keys_window, text="+", command=add_action_key)
            add_button.grid(row=len(action_keys), column=0, columnspan=2, pady=5)

        # Save Button
        save_button = tk.Button(action_keys_window, text="Save", command=save_action_keys)
        save_button.grid(row=len(action_keys), column=2, columnspan=2, pady=5)

    update_action_keys_window()

# Configure Action Keys button on the main UI
config_action_keys_button = tk.Button(frame, text="Configure Action Keys", command=open_action_keys_window)
config_action_keys_button.grid(row=9, column=0, columnspan=2, pady=10)

# Matplotlib figure for the linearity curve
fig, ax = plt.subplots(figsize=(5, 2))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

# Function to update the graph based on linearity and show the current X axis position
def update_graph():
    try:
        linearity = int(linearity_entry.get())
        linearity = max(50, min(linearity, 200))  # Clamp between 1 and 100
        settings["linearity"] = linearity
        save_settings(settings, profile_var.get())

        x = np.linspace(-1, 1, 100)
        y = np.abs(x) ** (100 / linearity)  # Apply linearity curve

        ax.clear()
        ax.plot(x, y)
        ax.set_title("Linearity Curve")

        # Add a line for the current steering output
        current_output = (current_x_axis_value + 1) / 2  # Normalize to 0 to 1
        ax.axvline(current_x_axis_value, color='r', linestyle='--')

        canvas.draw()
    except ValueError:
        pass

# Function to update the steering visualization
def update_steering_visualization(x_axis_output):
    global current_x_axis_value
    current_x_axis_value = x_axis_output
    update_graph()

# Function to update the steering visualization
def update_steering_visualization(x_axis_output):
    global current_x_axis_value
    current_x_axis_value = x_axis_output
    update_graph()

def normalize_key_name(key_name):
    # Normalize common special keys for compatibility with keyboard module
    key_map = {
        "Control_L": "ctrl",
        "Control_R": "ctrl",
        "Alt_L": "alt",
        "Alt_R": "alt",
        "Shift_L": "shift",
        "Shift_R": "shift",
    }
    return key_map.get(key_name, key_name)  # Return mapped value or original key name

# Monitor kb
def monitor_keyboard():
    global fullsteer_left_binding, fullsteer_right_binding, current_x_axis_value
    action_key_active = False
    fullsteer_active = False
    previous_fullsteer_active = False

    while True:
        try:
            # Retrieve and clamp all sensitivity-related settings
            linearity = int(linearity_entry.get())
            linearity = max(50, min(linearity, 200))  # Clamp between 50 and 200
            sensitivity = int(sensitivity_entry.get())
            sensitivity = max(1, min(sensitivity, 100))  # Clamp between 1 and 100
            release_sensitivity = int(release_sensitivity_entry.get())
            release_sensitivity = max(1, min(release_sensitivity, 100))  # Clamp between 1 and 100
            countersteer_multiplier = float(countersteer_multiplier_entry.get())
            snap_to_action_key_multiplier = float(snap_to_action_key_multiplier_entry.get())

            # Get the Permanent Max Lock value
            permanent_max_lock = permanent_max_lock_var.get() / 100.0  # Convert percentage to fraction
        except ValueError:
            continue  # Skip the iteration if there are invalid inputs

        # Normalize the key bindings for steering
        steer_left_binding_normalized = normalize_key_name(steer_left_binding)
        steer_right_binding_normalized = normalize_key_name(steer_right_binding)

        # Get the current X-axis value (steering output)
        x_axis_output = current_x_axis_value

        # Default action_key_cap
        action_key_cap = permanent_max_lock  # Start with permanent max lock
        action_key_active = False  # Reset action key active state

        # Process each action key
        for action_key in action_keys:
            action_key_binding = action_key["binding"].get() if isinstance(action_key["binding"], tk.StringVar) else action_key["binding"]
            
            # Normalize action key bindings
            action_key_binding_normalized = normalize_key_name(action_key_binding)

            # Ensure a key is properly set and not "Not Set"
            if action_key_binding_normalized and action_key_binding_normalized != "Not Set" and keyboard.is_pressed(action_key_binding_normalized):
                action_key_cap = float(action_key["cap_percentage"].get()) / 100.0 if isinstance(action_key["cap_percentage"], tk.StringVar) else float(action_key["cap_percentage"]) / 100.0
                action_key_active = True
                break

        fullsteer_active = False

        # Handle Fullsteer Left
        if fullsteer_left_binding and keyboard.is_pressed(normalize_key_name(fullsteer_left_binding)):
            x_axis_output = -1  # Fullsteer left to 100%
            fullsteer_active = True

        # Handle Fullsteer Right
        if fullsteer_right_binding and keyboard.is_pressed(normalize_key_name(fullsteer_right_binding)):
            x_axis_output = 1  # Fullsteer right to 100%
            fullsteer_active = True

        # Handle fullsteer release (snap to center or smooth return)
        if previous_fullsteer_active and not fullsteer_active:
            if settings.get("snap_to_center", False):
                x_axis_output = 0  # Snap to center
                current_x_axis_value = 0
            else:
                # Smoothly return to center
                if x_axis_output > 0:
                    x_axis_output -= 0.01 * release_sensitivity
                    x_axis_output = max(x_axis_output, 0)
                elif x_axis_output < 0:
                    x_axis_output += 0.01 * release_sensitivity
                    x_axis_output = min(x_axis_output, 0)

        # Normal steering input handling (if fullsteer is not active)
        if not fullsteer_active:
            if keyboard.is_pressed(steer_left_binding_normalized):
                if x_axis_output > 0:
                    x_axis_output -= 0.01 * sensitivity * countersteer_multiplier
                else:
                    x_axis_output -= 0.01 * sensitivity * (snap_to_action_key_multiplier if action_key_active else 1)
                x_axis_output = max(x_axis_output, -action_key_cap)
            elif keyboard.is_pressed(steer_right_binding_normalized):
                if x_axis_output < 0:
                    x_axis_output += 0.01 * sensitivity * countersteer_multiplier
                else:
                    x_axis_output += 0.01 * sensitivity * (snap_to_action_key_multiplier if action_key_active else 1)
                x_axis_output = min(x_axis_output, action_key_cap)
            else:
                    # Smoothly return to the center
                    if x_axis_output > action_key_cap:
                        x_axis_output -= 0.01 * release_sensitivity * snap_to_action_key_multiplier
                        x_axis_output = max(x_axis_output, action_key_cap)
                    elif x_axis_output < -action_key_cap:
                        x_axis_output += 0.01 * release_sensitivity * snap_to_action_key_multiplier
                        x_axis_output = min(x_axis_output, -action_key_cap)
                    else:
                        if x_axis_output > 0:
                            x_axis_output -= 0.01 * release_sensitivity * (snap_to_action_key_multiplier if action_key_active else 1)
                            x_axis_output = max(x_axis_output, 0)
                        elif x_axis_output < 0:
                            x_axis_output += 0.01 * release_sensitivity * (snap_to_action_key_multiplier if action_key_active else 1)
                            x_axis_output = min(x_axis_output, 0)

        # Handle action key capping and smooth transition
        if action_key_active and abs(x_axis_output) > action_key_cap:
            if x_axis_output > action_key_cap:
                x_axis_output -= 0.01 * release_sensitivity * snap_to_action_key_multiplier
                x_axis_output = max(x_axis_output, action_key_cap)
            elif x_axis_output < -action_key_cap:
                x_axis_output += 0.01 * release_sensitivity * snap_to_action_key_multiplier
                x_axis_output = min(x_axis_output, -action_key_cap)

       # Apply linearity to the output
        vjoy_output = np.sign(x_axis_output) * np.abs(x_axis_output) ** (100 / linearity)
        
        # Apply smoothing: The higher the smoothing_value, the slower the output change
        vjoy_output = np.sign(x_axis_output) * np.abs(x_axis_output) ** (100 / linearity)
        vj.set_axis(pyvjoy.HID_USAGE_X, int((vjoy_output + 1) * 0x4000))

        current_x_axis_value = x_axis_output

        # Update the steering visualization
        update_steering_visualization(x_axis_output)

        previous_fullsteer_active = fullsteer_active

        time.sleep(0.01)  # Small delay to prevent CPU overuse

# Run the keyboard monitoring in a separate thread
def start_monitoring():
    keyboard_thread = Thread(target=monitor_keyboard)
    keyboard_thread.daemon = True
    keyboard_thread.start()

# Load all profiles on startup
def load_all_profiles():
    profiles = [f.replace("keyboard_", "").replace("_settings.json", "") for f in os.listdir(".") if f.startswith("keyboard_")]
    profile_menu['menu'].delete(0, 'end')
    for profile in profiles:
        profile_menu['menu'].add_command(label=profile, command=lambda p=profile: profile_var.set(p))
    if profiles:
        profile_var.set(profiles[0])  # Set the first profile as selected
    else:
        profile_var.set("default")  # Fallback to default if no profiles found

# Define the open_url function to open the web browser
def open_url():
    webbrowser.open("https://github.com/BrokenGameNoob/BrokenTC2")

# Create a frame to hold the button and the text
bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, anchor=tk.W, padx=10, pady=10)

# Create the credit label
credit_label = tk.Label(
    bottom_frame, text="Made by Flicction with help from BrokenGameNoob", font=("Helvetica", 10))
credit_label.pack(side=tk.LEFT, padx=10)

# Create the button to open the URL
url_button = tk.Button(
    bottom_frame, text="Check out Clutch helper Software (BTC2)", command=open_url)
url_button.pack(side=tk.RIGHT)

# Load profiles and start monitoring on startup
load_all_profiles()
start_monitoring()

# Ensure the application closes fully when the X button is pressed
root.protocol("WM_DELETE_WINDOW", root.quit)

# Start monitoring when the profile selection changes
profile_var.trace("w", lambda *args: start_monitoring())

# Run the Tkinter event loop
root.mainloop()
