import tkinter as tk
from tkinter import messagebox
from tkcalendar import DateEntry
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from datetime import datetime
from num2words import num2words
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
# -------------------- CONFIG --------------------
COMPANY_NAME = "ECO DRAIN SOLUTIONS"
# THEME_COLOR = "#9e4b78"
# THEME_COLOR = "#0F766E"
THEME_COLOR = "#1F4E79"
# THEME_COLOR = "#4B5563"

TERMS = [
    "1. Goods once sold will not be taken back.",
    "2. Interest @18% will be charges if the bill is not paid within due date.",
    "3. Subject to Pune jurisdiction.",
]

COL_WIDTHS = {
    "sr": 6, "date": 12, "challan": 15, "vehicle": 15, "material": 15,
    "trips": 8, "amount": 15, "delete": 8
}

table_rows = []

# -------------------- ROOT WINDOW --------------------
root = tk.Tk()
root.title("Invoice Generator")
root.geometry("1100x650")

# -------------------- PAGE FRAMES --------------------
page1 = tk.Frame(root)
page2 = tk.Frame(root)
for frame in (page1, page2):
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

# -------------------- PAGE 1 --------------------
def show_page2():
    page2.lift()

tk.Label(page1, text="INVOICE GENERATOR", font=("Arial", 18, "bold"), fg=THEME_COLOR).pack(pady=10)

# Company Frame
company_frame = tk.LabelFrame(page1, text="Company Details", padx=10, pady=10)
company_frame.pack(fill="x", padx=20, pady=5)

tk.Label(company_frame, text="Company Name").grid(row=0, column=0, sticky="w")
company_name_var = tk.StringVar(value=COMPANY_NAME)
tk.Entry(company_frame, textvariable=company_name_var, state="readonly", width=30).grid(row=0, column=1, pady=3)

tk.Label(company_frame, text="Company Address").grid(row=1, column=0, sticky="w")
company_address_var = tk.StringVar(value="Address here")
tk.Entry(company_frame, textvariable=company_address_var, width=50).grid(row=1, column=1, pady=3)

tk.Label(company_frame, text="Company Contact").grid(row=2, column=0, sticky="w")
company_contact_var = tk.StringVar(value="0000000000")
tk.Entry(company_frame, textvariable=company_contact_var, width=50).grid(row=2, column=1, pady=3)

# Customer Frame
customer_frame = tk.LabelFrame(page1, text="Customer Details", padx=10, pady=10)
customer_frame.pack(fill="x", padx=20, pady=5)

tk.Label(customer_frame, text="Customer Address").grid(row=0, column=0, sticky="w")
customer_address_var = tk.StringVar()
tk.Entry(customer_frame, textvariable=customer_address_var, width=60).grid(row=0, column=1, pady=3)

tk.Label(customer_frame, text="Customer Contact").grid(row=1, column=0, sticky="w")
customer_contact_var = tk.StringVar()
tk.Entry(customer_frame, textvariable=customer_contact_var, width=60).grid(row=1, column=1, pady=3)

# Button to go to Page 2
tk.Button(page1, text="Add Entry", bg=THEME_COLOR, fg="white", width=20, command=show_page2).pack(pady=20)

# -------------------- PAGE 2 --------------------
def show_page1():
    page1.lift()

tk.Label(page2, text="INVOICE DETAILS", font=("Arial", 16, "bold"), fg=THEME_COLOR).pack(pady=10)

# Trip Rate
rate_frame = tk.Frame(page2)
rate_frame.pack(pady=5)
tk.Label(rate_frame, text="Trip Rate (₹):", font=("Arial", 11, "bold")).pack(side="left")
trip_rate_var = tk.StringVar()
tk.Entry(rate_frame, textvariable=trip_rate_var, width=10).pack(side="left", padx=5)

# Back button
back_button = tk.Button(page2, text="← Back", bg=THEME_COLOR, fg="white", command=show_page1)
back_button.place(x=20, y=20)  # top-left corner
# Table Frame
table_frame = tk.LabelFrame(page2, text="Invoice Table")
table_frame.pack(fill="both", expand=True, padx=20, pady=10)

canvas_frame = tk.Frame(table_frame)
canvas_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(canvas_frame, height=300)
canvas.pack(side="left", fill="both", expand=True)

v_scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
v_scrollbar.pack(side="right", fill="y")

h_scrollbar = tk.Scrollbar(table_frame, orient="horizontal", command=canvas.xview)
h_scrollbar.pack(side="bottom", fill="x")

canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
rows_frame = tk.Frame(canvas)
canvas.create_window((0,0), window=rows_frame, anchor="nw")

headers = ["Sr", "Date", "Challan No.", "Vehicle No.", "Material", "Trips", "Amount", "Delete"]
for col, h in enumerate(headers):
    tk.Label(rows_frame, text=h, font=("Arial",10,"bold"), bg="#dddddd")\
        .grid(row=0, column=col, padx=2, pady=2, sticky="we")
    rows_frame.grid_columnconfigure(col, weight=1)

def update_scroll(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
rows_frame.bind("<Configure>", update_scroll)

def _on_mousewheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
# -------------------- TABLE FUNCTIONS --------------------
import os

def get_next_invoice_no():
    file_path = "invoice_no.txt"
    # Read last invoice no
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            last_no = int(f.read().strip())
    else:
        last_no = 0
    next_no = last_no + 1
    # Save back
    with open(file_path, "w") as f:
        f.write(str(next_no))
    return next_no
def calculate_amounts():
    total = 0
    try:
        trip_rate = float(trip_rate_var.get())
    except:
        trip_rate = 0
    for row in table_rows:
        try:
            trips = float(row["trips"].get())
        except:
            trips = 0
        amount = trips * trip_rate
        row["amount"].config(state="normal")
        row["amount"].delete(0, tk.END)
        row["amount"].insert(0, f"{amount:.2f}")
        row["amount"].config(state="readonly")
        total += amount
    total_label.config(text=f"Total Amount: ₹ {total:.2f}")

def refresh_rows():
    for i, row in enumerate(table_rows, start=1):
        row["sr"].config(state="normal")
        row["sr"].delete(0, tk.END)
        row["sr"].insert(0, i)
        row["sr"].config(state="readonly")
        row_widgets = [row["sr"], row["date"], row["challan"], row["vehicle"],
                       row["material"], row["trips"], row["amount"], row["delete"]]
        for col_index, widget in enumerate(row_widgets):
            widget.grid(row=i, column=col_index, padx=2, pady=2, sticky="we")
            rows_frame.grid_columnconfigure(col_index, weight=1)

def delete_row(row_index):
    for widget in rows_frame.grid_slaves(row=row_index):
        widget.destroy()
    table_rows.pop(row_index-1)
    refresh_rows()
    calculate_amounts()

def move_focus(event, r, c):
    total_rows = len(table_rows)

    if event.keysym == "Return":   # Enter → next row
        if r < total_rows:
            table_rows[r]["widgets"][c].focus_set()

    elif event.keysym == "Right":
        if c < 6:
            table_rows[r-1]["widgets"][c+1].focus_set()

    elif event.keysym == "Left":
        if c > 1:
            table_rows[r-1]["widgets"][c-1].focus_set()

    elif event.keysym == "Down":
        if r < total_rows:
            table_rows[r]["widgets"][c].focus_set()

    elif event.keysym == "Up":
        if r > 1:
            table_rows[r-2]["widgets"][c].focus_set()
def add_row():
    row_number = len(table_rows) + 1
    row_data = {}
    sr_entry = tk.Entry(rows_frame)
    sr_entry.insert(0,row_number)
    sr_entry.config(state="readonly")
    row_data["sr"] = sr_entry

    date_entry = DateEntry(rows_frame, date_pattern="dd-mm-yyyy")
    row_data["date"] = date_entry
    for col_index, col in enumerate(["challan","vehicle","material","trips"], start=2):
        entry = tk.Entry(rows_frame)
        entry.bind("<Right>", lambda e, r=row_number, c=col_index: move_focus(e,r,c))
        entry.bind("<Left>", lambda e, r=row_number, c=col_index: move_focus(e,r,c))
        entry.bind("<Up>", lambda e, r=row_number, c=col_index: move_focus(e,r,c))
        entry.bind("<Down>", lambda e, r=row_number, c=col_index: move_focus(e,r,c))

        if col=="trips":
            entry.bind("<KeyRelease>", lambda e: calculate_amounts())
        row_data[col] = entry

    amount_entry = tk.Entry(rows_frame, state="readonly")
    row_data["amount"] = amount_entry

    delete_btn = tk.Button(rows_frame, text="🗑", fg="white", bg=THEME_COLOR,
                           command=lambda idx=row_number: delete_row(idx))
    row_data["delete"] = delete_btn

    row_widgets = [sr_entry, date_entry, row_data["challan"], row_data["vehicle"],
                   row_data["material"], row_data["trips"], amount_entry, delete_btn]
    for col_index, widget in enumerate(row_widgets):
        widget.grid(row=row_number, column=col_index, padx=2, pady=2, sticky="we")
        rows_frame.grid_columnconfigure(col_index, weight=1)

    row_data["widgets"] = row_widgets
    table_rows.append(row_data)

# Total Label
total_label = tk.Label(page2, text="Total Amount: ₹ 0", font=("Arial", 12, "bold"))
total_label.pack(pady=10)

# -------------------- PDF GENERATION --------------------
def draw_wrapped_text(c, text, x, y, max_width, line_height=12, font="Helvetica", font_size=10):
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if stringWidth(test_line, font, font_size) <= max_width:
            line = test_line
        else:
            c.drawString(x, y, line)
            y -= line_height
            line = word + " "
    if line:
        c.drawString(x, y, line)
        y -= line_height
    return y

def draw_page_border(c, width, height):
    c.setLineWidth(1)
    c.rect(20, 20, width-40, height-40)
def generate_pdf():
    if not company_address_var.get():
        messagebox.showerror("Error", "Company Address Required")
        return
    if not company_contact_var.get():
        messagebox.showerror("Error", "Company Contact Required")
        return
        
    if not customer_address_var.get():
        messagebox.showerror("Error", "Customer Address Required")
        return
        
    try:
        trip_rate = float(trip_rate_var.get())
    except:
        messagebox.showerror("Error", "Enter Trip Rate")
        return
    company_address = company_address_var.get()
    company_contact = company_contact_var.get()
    customer_address = customer_address_var.get()
    customer_contact = customer_contact_var.get()


    file_name = f"Invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    c = pdf_canvas.Canvas(file_name, pagesize=A4)
    
    width, height = A4
    border_thickness = 1
    c.setLineWidth(border_thickness)
    c.rect(20, 20, width - 40, height - 40)
    invoice_no = get_next_invoice_no()
    invoice_date = datetime.now().strftime("%d-%b-%Y") 
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 90, height - 50, "Invoice No:")
    c.drawRightString(width - 120, height - 65, "Date:")

    c.setFont("Helvetica", 10)
    c.drawRightString(width - 80, height - 50, str(invoice_no))
    c.drawRightString(width - 60, height - 65, str(invoice_date))
    
    y = height - 60

    # ------------------ INVOICE HEADING ------------------
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(THEME_COLOR)
    c.drawCentredString(width/2, y, "INVOICE")

    y -= 10
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(40, y, width-40, y)

    # ------------------ COMPANY DETAILS ------------------
    y -= 40
    c.setFont("Times-Bold", 11)
    c.setFillColor(THEME_COLOR)
    c.drawString(50, y, "ECO DRAIN SOLUTIONS")
    
    # Align Bill To with company name
    c.setFont("Times-Bold", 11)
    c.setFillColor(THEME_COLOR)
    c.drawString(380, y, "Bill To:")
    y -= 18
    
    c.setFont("Times-Bold", 10)
    c.setFillColor(colors.black)
    c.drawString(50, y, "Address:")
    y -= 15
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    for line in company_address.split("\n"):
        y = draw_wrapped_text(c, line, 50, y, max_width=150)

    c.setFont("Times-Bold", 10)
    c.drawString(50, y, "Contact:")
    c.setFont("Helvetica", 10)
    c.drawString(93, y, company_contact)
    y -= 20

    # ------------------ BILL TO ------------------
    bill_y = height - 120

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    bill_y -= 8
    bill_y = draw_wrapped_text(
        c,
        customer_address,
        380,
        bill_y,
        max_width=180
    )
    if customer_contact.strip():
        c.setFont("Times-Bold", 10)
        c.drawString(380, bill_y, "Contact:")
        c.setFont("Helvetica", 10)
        c.drawString(423, bill_y, customer_contact)
        bill_y-=20
    y = min(y, bill_y)
    
    y -= 10
    # Horizontal line
    c.line(50, y, width - 50, y)
    y -= 20

    # ------------------ INVOICE DETAILS HEADING ------------------
    c.setFont("Times-Bold", 12)
    c.setFillColor(THEME_COLOR)
    c.drawString(50, y, "Invoice Details")
    y -= 15

    # Table Headers
    data = [["Sr","Date","Challan No.","Vehicle No.","Material","Trips","Amount"]]

    total = 0

    # Table Rows
    for row in table_rows:
        sr = row["sr"].get()
        date = row["date"].get()
        challan = row["challan"].get()
        vehicle = row["vehicle"].get()
        material = row["material"].get()
        trips = row["trips"].get()
        amount = row["amount"].get()

        data.append([sr, date, challan, vehicle, material, trips, amount])
        try:
            total += float(amount)
        except:
            pass    
    amount_words = num2words(int(total), lang='en_IN').upper() + " RUPEES"
    # -------- TABLE WIDTH CONTROL --------
    col_widths = [30,70,70,70,90,40,70]
    available_width = width - 100
    table_width = sum(col_widths)
    scale = available_width / table_width
    col_widths = [w * scale for w in col_widths]

    # -------- PREPARE DATA --------
    left_margin = 50
    rows = data[1:]     # actual rows
    header = data[0]
    # -------- SPLIT TABLE FOR FIXED ROWS --------
    first_page_rows = rows[:22]      
    remaining_rows = rows[22:]

    # Add total row at the end of first page if no remaining rows
    if not remaining_rows:
        first_page_rows.append(["", "", "", "", "", "Total", f"{total:,.2f}"])
        
    # -------- DRAW FIRST PAGE TABLE --------
    table_data = [header] + first_page_rows
    table = Table(table_data, colWidths=col_widths)
    styles = [
        ('GRID',(0,0),(-1,-1),1,colors.black),
        ('BACKGROUND',(0,0),(-1,0),THEME_COLOR),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTSIZE',(0,0),(-1,-1),10),
    ]

    # Add Total row styles only if it exists
    if first_page_rows and first_page_rows[-1][5] == "Total":
        styles.append(('FONTNAME', (0,-1), (-1,-1), 'Times-Bold'))       # bold all columns of last row
        styles.append(('BACKGROUND', (5,-1), (6,-1), colors.lightgrey))   # optional highlight

    # Apply styles
    table.setStyle(TableStyle(styles))
    table.wrapOn(c, width, height)
    table.drawOn(c, left_margin, y - table._height)

    y -= table._height + 20


    # -------- DRAW REMAINING ROWS --------
    rows_per_page = 25

    while remaining_rows:

        c.showPage()
        draw_page_border(c, width, height)

        y = height - 60

        chunk = remaining_rows[:rows_per_page]
        remaining_rows = remaining_rows[rows_per_page:]

        # add total on last page
        if not remaining_rows:
            chunk.append(["", "", "", "", "", "Total", f"{total:.2f}"])

        table_data = [header] + chunk

        table = Table(table_data, colWidths=col_widths)

        table.setStyle(TableStyle([
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('BACKGROUND',(0,0),(-1,0),THEME_COLOR),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME', (0,-1), (-1,-1), 'Times-Bold'),
            ('BACKGROUND', (5,-1), (6,-1), colors.lightgrey),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTSIZE',(0,0),(-1,-1),10),
        ]))

        table.wrapOn(c, width, height)
        table.drawOn(c, left_margin, y - table._height)

        y -= table._height + 20
    y -= 20
    # ------------------ GRAND TOTAL ------------------
    #Draw Grand Total label
    grand_label = "Grand Total - "
    c.setFont("DejaVuSans", 10)
    c.setFillColor(THEME_COLOR)
    label_x = 50
    c.drawString(label_x, y, grand_label)

    #Draw Grand Total amount with ₹
    c.setFont("DejaVuSans", 10)
    value_x = label_x + c.stringWidth(grand_label, "DejaVuSans", 10) + 1
    c.setFillColor(colors.black)
    c.drawString(value_x, y, f"₹{total:,.2f}")
    y -= 15
    # -------- Amount in Words -------- 
    #Draw label
    c.setFont("Helvetica", 10)
    c.setFillColor(THEME_COLOR)
    label_x = 50
    c.drawString(label_x, y, "Amount in Words:")

    #Prepare value
    c.setFont("Helvetica", 10)
    value_x = label_x + c.stringWidth("Amount in Words:  ", "Times-Bold", 10) + 1
    c.setFillColor(colors.black)
    c.drawString(value_x, y, amount_words)

    #Draw underline below value
    underline_y = y - 2
    text_width = c.stringWidth(amount_words, "Helvetica", 10)
    c.setLineWidth(0.5)
    c.setStrokeColor(colors.grey)
    c.line(value_x, underline_y, value_x + text_width, underline_y)
    y -= 30
    
    # Terms
    c.setFont("Times-Bold", 12)
    c.setFillColor(THEME_COLOR)
    c.drawString(50, y, "Terms & Conditions")
    y -= 15
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.black)
    for t in TERMS:
        c.drawString(50, y, t)
        y -= 12

    # Footer
    c.setFont("Times-Bold", 12)
    c.setFillColor(THEME_COLOR)
    c.drawCentredString(width/2, 40, "Thank you for your business.")

    c.save()
    messagebox.showinfo("Success", f"Invoice Created\n{file_name}")

# -------------------- BUTTONS --------------------
button_frame = tk.Frame(page2)
button_frame.pack(pady=10)
tk.Button(
    button_frame,
    text="+ Add Row",
    command=add_row,
    width=15,
    bg=THEME_COLOR,
    fg="white"
).pack(side="left", padx=10)
tk.Button(button_frame, text="Generate Invoice", width=20, bg=THEME_COLOR, fg="white", command=generate_pdf).pack(side="left")

# First row by default
add_row()
table_rows[0]["challan"].focus_set()

# -------------------- START APP --------------------
page1.lift()
root.mainloop()