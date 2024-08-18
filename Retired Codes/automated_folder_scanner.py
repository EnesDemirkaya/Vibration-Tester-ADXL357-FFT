import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

def process_folder(process_function, folder_path=None):
    """
    Process all .npy files named 'accelerometer_data.npy' in the specified folder and its subfolders using the given function.

    Args:
        process_function (function): The function to be applied to each selected .npy file. This function must take a single argument, the file path.
        folder_path (str): The path to the folder to process. If not provided, a UI will prompt the user to select a folder.

    Returns:
        None
    """
    # Ask for folder if not provided
    if folder_path is None:
        root = Tk()
        root.withdraw()  # Hide the root window
        folder_path = askdirectory(title="Select the folder to process")

        if not folder_path:
            print("No folder selected.")
            return

    # Walk through the folder and its subfolders
    for root_dir, _, files in os.walk(folder_path):
        for file in files:
            if file == 'accelerometer_data.npy':
                file_path = os.path.join(root_dir, file)
                print(f"Processing file: {file_path}")
                # Call the provided processing function with the selected file path
                process_function(file_path)

if __name__ == "__main__":
    from find_damping_ratio_script import find_damping_ratio  # Import your specific processing function
    process_folder(find_damping_ratio)
