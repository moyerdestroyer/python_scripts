import tkinter as tk
from tkinter import ttk, messagebox
import random

class ChoiceWheel:
    def __init__(self, root):
        self.root = root
        self.root.title("Choice Wheel Randomizer")
        self.root.geometry("600x500")
        
        # Store options as list of tuples (name, percentage)
        self.options = []
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weight
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Choice Wheel Randomizer", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Add Option", padding="5")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="Option Name:").grid(row=0, column=0, padx=5)
        self.name_entry = ttk.Entry(input_frame, width=20)
        self.name_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="Percentage:").grid(row=0, column=2, padx=5)
        self.percent_entry = ttk.Entry(input_frame, width=10)
        self.percent_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="%").grid(row=0, column=4)
        
        add_button = ttk.Button(input_frame, text="Add Option", command=self.add_option)
        add_button.grid(row=0, column=5, padx=10)
        
        # Options list
        list_frame = ttk.LabelFrame(main_frame, text="Current Options", padding="5")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # Create Treeview for options display
        columns = ('Option', 'Percentage')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        self.tree.heading('Option', text='Option')
        self.tree.heading('Percentage', text='Percentage')
        self.tree.column('Option', width=300)
        self.tree.column('Percentage', width=100)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, pady=5)
        
        remove_button = ttk.Button(button_frame, text="Remove Selected", 
                                  command=self.remove_option)
        remove_button.grid(row=0, column=0, padx=5)
        
        clear_button = ttk.Button(button_frame, text="Clear All", 
                                 command=self.clear_all)
        clear_button.grid(row=0, column=1, padx=5)
        
        # Total percentage label
        self.total_label = ttk.Label(main_frame, text="Total: 0%", 
                                     font=('Arial', 10, 'bold'))
        self.total_label.grid(row=3, column=0, columnspan=3, pady=5)
        
        # Spin section
        spin_frame = ttk.LabelFrame(main_frame, text="Spin the Wheel!", padding="10")
        spin_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        self.spin_button = ttk.Button(spin_frame, text="SPIN!", 
                                      command=self.spin_wheel,
                                      style='Accent.TButton')
        self.spin_button.grid(row=0, column=0, padx=10)
        
        # Result display
        self.result_label = ttk.Label(spin_frame, text="Click SPIN to get a result!", 
                                     font=('Arial', 14))
        self.result_label.grid(row=0, column=1, padx=20)
        
        # Style configuration
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Arial', 12, 'bold'))
        
        # Add some example options
        self.add_example_options()
        
    def add_option(self):
        """Add a new option to the wheel"""
        name = self.name_entry.get().strip()
        try:
            percentage = float(self.percent_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid percentage number")
            return
        
        if not name:
            messagebox.showerror("Error", "Please enter an option name")
            return
        
        if percentage <= 0 or percentage > 100:
            messagebox.showerror("Error", "Percentage must be between 0 and 100")
            return
        
        # Add to options list
        self.options.append((name, percentage))
        
        # Update display
        self.update_display()
        
        # Clear entries
        self.name_entry.delete(0, tk.END)
        self.percent_entry.delete(0, tk.END)
        
    def remove_option(self):
        """Remove selected option from the wheel"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an option to remove")
            return
        
        # Get index and remove from options
        index = self.tree.index(selected[0])
        del self.options[index]
        
        # Update display
        self.update_display()
        
    def clear_all(self):
        """Clear all options"""
        if self.options and messagebox.askyesno("Confirm", "Clear all options?"):
            self.options = []
            self.update_display()
    
    def update_display(self):
        """Update the treeview display and total percentage"""
        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add all options
        for name, percentage in self.options:
            self.tree.insert('', tk.END, values=(name, f"{percentage}%"))
        
        # Update total
        total = sum(p for _, p in self.options)
        self.total_label.config(text=f"Total: {total:.1f}%")
        
        # Color code total label
        if abs(total - 100) < 0.01:
            self.total_label.config(foreground='green')
        else:
            self.total_label.config(foreground='red')
    
    def spin_wheel(self):
        """Spin the wheel and select a random option based on percentages"""
        if not self.options:
            messagebox.showwarning("Warning", "Please add at least one option")
            return
        
        total = sum(p for _, p in self.options)
        if abs(total - 100) > 0.01:
            if not messagebox.askyesno("Warning", 
                                       f"Total percentage is {total:.1f}%, not 100%.\n"
                                       "Continue anyway? (Results will be normalized)"):
                return
        
        # Create weighted random selection
        # Normalize percentages if they don't sum to 100
        weights = [p/total*100 for _, p in self.options]
        names = [name for name, _ in self.options]
        
        # Select random option based on weights
        selected = random.choices(names, weights=weights, k=1)[0]
        
        # Display result with animation effect
        self.animate_result(selected)
    
    def animate_result(self, final_result):
        """Simple animation effect before showing final result"""
        # Quick "spinning" effect
        animation_steps = 10
        for i in range(animation_steps):
            # Show random option during "spin"
            random_option = random.choice([name for name, _ in self.options])
            self.result_label.config(text=f"🎲 {random_option}...")
            self.root.update()
            self.root.after(50 + i * 10)  # Gradually slow down
        
        # Show final result
        self.result_label.config(text=f"🎉 Result: {final_result}!", 
                               foreground='green',
                               font=('Arial', 16, 'bold'))
        
        # Reset color after 2 seconds
        self.root.after(2000, lambda: self.result_label.config(foreground='black',
                                                               font=('Arial', 14)))
    
    def add_example_options(self):
        """Add some example options to demonstrate"""
        examples = [
            ("Pizza", 25),
            ("Burger", 25),
            ("Sushi", 25),
            ("Tacos", 25)
        ]
        
        for name, percentage in examples:
            self.options.append((name, percentage))
        
        self.update_display()

def main():
    root = tk.Tk()
    app = ChoiceWheel(root)
    root.mainloop()

if __name__ == "__main__":
    main()