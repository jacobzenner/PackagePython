import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import random
import os
import sys
import math

class ContestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contest Winner Picker")
        
        # Load buttons
        self.load_button = tk.Button(root, text="Upload Contest CSV", command=self.load_csv)
        self.load_button.pack(pady=10)
        
        self.pick_button = tk.Button(root, text="Pick Winner", command=self.pick_winner, state=tk.DISABLED)
        self.pick_button.pack(pady=10)
        
        self.result_label = tk.Label(root, text="Winner: None", font=("Helvetica", 14))
        self.result_label.pack(pady=10)
        
        # Determine the path for ContestHistory.csv in the executable’s directory
        if getattr(sys, 'frozen', False):
            app_dir = os.path.dirname(sys.executable)
        else:
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.history_path = os.path.join(app_dir, 'ContestHistory.csv')

        # Initialize contest history file if it doesn’t exist
        self.check_history_file()

    def check_history_file(self):
        if not os.path.exists(self.history_path) or os.stat(self.history_path).st_size == 0:
            # Create ContestHistory.csv with necessary columns if it doesn't exist or is empty
            pd.DataFrame(columns=["username", "total_entries", "total_wins"]).to_csv(self.history_path, index=False)
            messagebox.showwarning("Warning", "Created a new 'ContestHistory.csv' file.")
        else:
            # Enable CSV load functionality if history file is present and correctly formatted
            self.load_button.config(state=tk.NORMAL)

    def load_csv(self):
        file_path = filedialog.askopenfilename(title="Select Contest CSV", filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.users_df = pd.read_csv(file_path)
                if 'username' not in self.users_df.columns:
                    messagebox.showerror("Error", "CSV must contain a 'username' column.")
                    return
                if os.path.exists(self.history_path):
                    self.pick_button.config(state=tk.NORMAL)
                    messagebox.showinfo("Success", "CSV loaded successfully and ready to pick a winner!")
                else:
                    messagebox.showerror("Error", f"History file '{self.history_path}' not found. Cannot proceed without it.")
            except pd.errors.EmptyDataError:
                messagebox.showerror("Error", "The uploaded CSV file is empty.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def pick_winner(self):
        if self.users_df is None or 'username' not in self.users_df.columns:
            messagebox.showerror("Error", "No valid CSV loaded.")
            return
        if not os.path.exists(self.history_path):
            messagebox.showerror("Error", f"History file '{self.history_path}' not found.")
            return

        # Read ContestHistory and handle possible empty data (besides headers)
        history_df = pd.read_csv(self.history_path)
        if history_df.empty or history_df.shape[0] == 0:
            # If history is empty, initialize the DataFrame with columns
            history_df = pd.DataFrame(columns=["username", "total_entries", "total_wins"])

        # List of correct usernames for this contest
        correct_usernames = self.users_df['username'].tolist()
        num_users = len(correct_usernames)
        max_answer_order_weight = 10  # Maximum weight for the first responder
        weights = []

        # Calculate Weight
        for i, user in enumerate(correct_usernames):
            user_data = history_df[history_df['username'] == user]
            total_entries = user_data['total_entries'].values[0] if not user_data.empty else 0

            # Logarithmic scaling for total entries
            entry_weight = math.log(total_entries + 1)

            # Scaled answer order weight, from max_answer_order_weight down to 0
            answer_order_weight = max_answer_order_weight * (num_users - i - 1) / max(1, num_users - 1)

            weight = entry_weight + answer_order_weight
            weights.append(weight)

        # Select the winner based on weighted choices
        winner = random.choices(correct_usernames, weights=weights, k=1)[0]
        self.result_label.config(text=f"Winner: {winner}")

        # Update ContestHistory
        if winner in history_df['username'].values:
            history_df.loc[history_df['username'] == winner, 'total_entries'] += 1
            history_df.loc[history_df['username'] == winner, 'total_wins'] += 1
        else:
            new_entry = pd.DataFrame({"username": [winner], "total_entries": [1], "total_wins": [1]})
            history_df = pd.concat([history_df, new_entry], ignore_index=True)

        # Update total entries for other users who participated
        for user in correct_usernames:
            if user != winner:
                if user in history_df['username'].values:
                    history_df.loc[history_df['username'] == user, 'total_entries'] += 1
                else:
                    new_entry = pd.DataFrame({"username": [user], "total_entries": [1], "total_wins": [0]})
                    history_df = pd.concat([history_df, new_entry], ignore_index=True)

        # Save updated history
        history_df.to_csv(self.history_path, index=False)
        messagebox.showinfo("Winner Selected", f"The winner is {winner}")

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ContestApp(root)
    root.mainloop()
