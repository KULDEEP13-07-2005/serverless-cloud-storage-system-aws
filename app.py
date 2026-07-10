import tkinter as tk
from tkinter import filedialog, messagebox
import requests

API = "https://your-api-id.execute-api.region.amazonaws.com/prod"

# ---------------- UPLOAD ----------------
def upload_file():
    file_paths = filedialog.askopenfilenames()

    if not file_paths:
        return

    for file_path in file_paths:
        try:
            file_name = file_path.split("/")[-1]

            print("Uploading:", file_name)

            # Step 1: Get upload URL
            res = requests.post(API + "/generate-upload-url", json={
                "fileName": file_name
            })

            print("Upload URL response:", res.status_code, res.text)

            data = res.json()

            # Step 2: Upload file
            with open(file_path, "rb") as f:
                upload_res = requests.put(data["uploadURL"], data=f)

            print("S3 Upload:", upload_res.status_code)

            # Step 3: Save metadata
            meta_res = requests.post(API + "/save-metadata", json={
                "fileId": data["fileId"],
                "fileName": file_name,
                "s3Key": data["s3Key"]
            })

            print("Metadata save:", meta_res.status_code, meta_res.text)

        except Exception as e:
            print("Error:", e)

    messagebox.showinfo("Success", "Files uploaded")

# ---------------- LIST ----------------
def list_files():
    res = requests.get(API + "/list_files")

    import json
    data = res.json()

    print("DEBUG:", data)  # 🔍 helps you see actual response

    # Case 1: API Gateway format
    if "body" in data:
        body = json.loads(data["body"])
        files = body.get("files", [])
    else:
        files = data.get("files", [])

    # Clear listbox
    list_box.delete(0, tk.END)

    if not files:
        list_box.insert(tk.END, "No files found")
        return

    for f in files:
        list_box.insert(tk.END, f"{f['fileId']} | {f['fileName']}")

# ---------------- DOWNLOAD ----------------
def download_file():
    s3_key = entry.get()

    if not s3_key:
        messagebox.showerror("Error", "Enter S3 Key")
        return

    res = requests.post(API + "/download", json={"s3Key": s3_key})

    print("Download Status:", res.status_code)
    print("Download Response:", res.text)

    import json
    data = res.json()

    # 🔥 FIX HERE
    if "body" in data:
        body = json.loads(data["body"])
        url = body.get("downloadURL")
    else:
        url = data.get("downloadURL")

    if not url:
        messagebox.showerror("Error", "Download URL not found")
        return

    messagebox.showinfo("Download URL", url)

# ---------------- DELETE ----------------
def delete_file():
    selected = list_box.curselection()

    if not selected:
        messagebox.showerror("Error", "Select files to delete")
        return

    for index in selected:
        item = list_box.get(index)

        try:
            file_id = item.split("|")[0].strip()
        except:
            continue

        res = requests.post(API + "/delete", json={
            "fileId": file_id
        })

        print(f"Deleted {file_id}: ", res.text)

    messagebox.showinfo("Success", "Selected files deleted")

# ---------------- UI ----------------
def create_button(text, command, color):
    return tk.Button(root,
                     text=text,
                     command=command,
                     bg=color,
                     fg="white",
                     font=FONT,
                     width=25,
                     relief="flat",
                     padx=5,
                     pady=5)

root = tk.Tk()
root.title("Cloud Storage App")
root.geometry("500x450")
root.configure(bg="#1e1e2f")   # Dark background

FONT = ("Arial", 11)
TITLE_FONT = ("Arial", 16, "bold")

tk.Label(root, text="Cloud Storage App",
         font=TITLE_FONT,
         bg="#1e1e2f",
         fg="white").pack(pady=10)

create_button("Upload File", upload_file, "#4CAF50").pack(pady=5)
create_button("List Files", list_files, "#2196F3").pack(pady=5)
create_button("Download File", download_file, "#FF9800").pack(pady=5)
create_button("Delete File", delete_file, "#f44336").pack(pady=5)

entry = tk.Entry(root,
                 font=FONT,
                 width=40,
                 bg="#2c2c3e",
                 fg="white",
                 insertbackground="white")
entry.pack(pady=10)

list_box = tk.Listbox(root,
                      selectmode=tk.MULTIPLE,   # 🔥 IMPORTANT
                      height=12,
                      width=60,
                      bg="#2c2c3e",
                      fg="white",
                      selectbackground="#5555ff",
                      font=FONT)
list_box.pack(pady=10)

tk.Label(root, text="Files",
         bg="#1e1e2f",
         fg="white",
         font=("Arial", 12)).pack()

root.mainloop()