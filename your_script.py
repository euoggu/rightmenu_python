import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import os

class MenuItem:
    def __init__(self, name="", command=""):
        self.name = name
        self.command = command

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Right-Click Menu Items Manager")
        self.menu_items = []
        self.selected_item_index = None

        self.load_menu_items_from_registry()
        self.create_widgets()
        self.populate_list()

    def load_menu_items_from_registry(self):
        self.menu_items = []
        registry_paths = [
            r"*\shell",
            r"Directory\shell",
            r"Directory\Background\shell",
            r"Drive\shell",
        ]

        try:
            hkey = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, "")
            for path_suffix in registry_paths:
                try:
                    key_path = path_suffix
                    subkey = winreg.OpenKey(hkey, key_path)
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(subkey, i)
                            command_path = f"{key_path}\\{subkey_name}\\command"
                            try:
                                command_key = winreg.OpenKey(hkey, command_path)
                                command_value, _ = winreg.QueryValueEx(command_key, None)
                                self.menu_items.append(MenuItem(subkey_name, command_value))
                                winreg.CloseKey(command_key)
                            except FileNotFoundError:
                                pass
                            except Exception as e:
                                print(f"Error reading command for {subkey_name}: {e}")
                            i += 1
                        except WindowsError:
                            break
                        except Exception as e:
                            print(f"Error enumerating subkeys in {key_path}: {e}")
                    winreg.CloseKey(subkey)
                except FileNotFoundError:
                    pass
                except Exception as e:
                    print(f"Error opening registry key {path_suffix}: {e}")
            winreg.CloseKey(hkey)
        except Exception as e:
            print(f"Error accessing registry: {e}")

    def create_widgets(self):
        # Item List
        self.tree = ttk.Treeview(self, columns=("Name", "Command"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Command", text="Command")
        self.tree.bind("<ButtonRelease-1>", self.select_item)
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)

        # Input Frames
        input_frame = ttk.Frame(self)
        input_frame.pack(pady=5, padx=10, fill="x")

        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(input_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Command:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.command_entry = ttk.Entry(input_frame)
        self.command_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        input_frame.columnconfigure(1, weight=1)

        # Buttons Frame
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(pady=5, padx=10, fill="x")

        self.add_button = ttk.Button(buttons_frame, text="Add", command=self.add_menu_item)
        self.add_button.pack(side="left", padx=5)

        self.delete_button = ttk.Button(buttons_frame, text="Delete", command=self.delete_menu_item, state=tk.DISABLED)
        self.delete_button.pack(side="left", padx=5)

    def populate_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for item in self.menu_items:
            self.tree.insert("", tk.END, values=(item.name, item.command))

    def add_menu_item(self):
        name = self.name_entry.get().strip()
        command = self.command_entry.get().strip()

        if not name or not command:
            messagebox.showerror("Error", "Name and Command cannot be empty.")
            return

        registry_paths = [
            r"*\shell",  # 针对所有文件
            r"Directory\shell",  # 针对文件夹
        ]

        for registry_path in registry_paths:
            try:
                hkey = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, registry_path, 0, winreg.KEY_WRITE)
                subkey = winreg.CreateKey(hkey, name)
                command_key = winreg.CreateKey(subkey, "command")
                winreg.SetValueEx(command_key, None, 0, winreg.REG_SZ, command)
                winreg.CloseKey(command_key)
                winreg.CloseKey(subkey)
                winreg.CloseKey(hkey)
                print(f"Successfully added to {registry_path}")  # 可以添加日志输出

            except WindowsError as e:
                messagebox.showerror("Error", f"Could not add right-click menu item to '{registry_path}': {e}")
                return  # 如果添加到其中一个失败，就返回

        # 添加到本地列表并更新显示 (只添加一次)
        self.menu_items.append(MenuItem(name, command))
        self.populate_list()
        self.clear_inputs()
        messagebox.showinfo("Success", f"Successfully added right-click menu item '{name}' to file and folder contexts.")

    import tkinter as tk
    from tkinter import ttk, messagebox
    import winreg
    import os

    # ... (之前的代码)

    def delete_menu_item(self):
        if self.selected_item_index is not None:
            if messagebox.askyesno("Confirm", "Are you sure you want to delete this menu item? (This will modify the registry!)"):
                try:
                    selected_item = self.menu_items[self.selected_item_index]
                    item_name = selected_item.name

                    registry_paths = [
                        r"*\shell",
                        r"Directory\shell",
                    ]

                    for base_path in registry_paths:
                        full_path = rf"{base_path}\{item_name}"
                        try:
                            # 尝试获取完全控制权限后再删除
                            os.system(f'reg add "HKEY_CLASSES_ROOT\\{full_path}" /f') # 尝试添加键，如果存在相当于修改
                            os.system(f'reg add "HKEY_CLASSES_ROOT\\{base_path}" /f') # 尝试添加父键，如果存在相当于修改
                            os.system(f'reg delete "HKEY_CLASSES_ROOT\\{full_path}" /f')
                            print(f"Successfully deleted from {full_path}")
                            break
                        except Exception as e:
                            messagebox.showerror("Error", f"删除注册表项 '{full_path}' 失败: {e}")
                            return

                    else:
                        messagebox.showinfo("Info", f"未找到名为 '{item_name}' 的右键菜单项。")
                        return

                    # 从本地列表移除并更新显示
                    del self.menu_items[self.selected_item_index]
                    self.populate_list()
                    self.clear_inputs()
                    self.selected_item_index = None
                    self.delete_button['state'] = tk.DISABLED
                    messagebox.showinfo("Success", f"Successfully deleted right-click menu item '{item_name}' from registry.")

                except Exception as e:
                    messagebox.showerror("Error", f"删除右键菜单项时发生错误: {e}")
        else:
            messagebox.showinfo("Info", "请选择要删除的项。")

    # ... (剩余的代码)

    def select_item(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            self.selected_item_index = self.tree.index(selected_item)
            name, command = self.tree.item(selected_item, 'values')
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, name)
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, command)
            self.delete_button['state'] = tk.NORMAL
        else:
            self.selected_item_index = None
            self.delete_button['state'] = tk.DISABLED

    def clear_inputs(self):
        self.name_entry.delete(0, tk.END)
        self.command_entry.delete(0, tk.END)

if __name__ == "__main__":
    app = App()
    app.mainloop()