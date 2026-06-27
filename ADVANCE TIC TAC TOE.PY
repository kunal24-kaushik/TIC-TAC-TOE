import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random

root = tk.Tk()
player_name = "Player"
difficulty = "Easy"
difficulty_options = ["Easy", "Hard", "Impossible"]
root.title("Tic Tac Toe Studio")
root.geometry("770x775")
root.resizable(False, False)
try:
	bg_image = Image.open(r"C:\Users\Kunal\Downloads\bear.jpg")
	bg_image = bg_image.resize((770, 775)).filter(ImageFilter.GaussianBlur(8))
	overlay = Image.new("RGBA", bg_image.size, (22, 28, 50, 140))
	bg_image = Image.alpha_composite(bg_image.convert("RGBA"), overlay)
	bg_photo = ImageTk.PhotoImage(bg_image)
except Exception:
	bg_photo = None
background_label = tk.Label(root, image=bg_photo, bd=0)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
BG_COLOR = "#0F172A"
ACCENT_COLOR = "#06B6D4"
BUTTON_COLOR = "#122A44"
BUTTON_HOVER = "#0A4B65"
TEXT_COLOR = "white"
root.configure(bg=BG_COLOR)
player_name_var = tk.StringVar(value=player_name)
difficulty_var = tk.StringVar(value=difficulty)
root.deiconify()
board = [""] * 9
buttons = []
wins = 0
losses = 0
draws = 0
COLORS = ["red","blue","purple","orange","yellow","cyan","magenta","white"]
x_color = "blue"
o_color = "red"
winning_combinations = [(0, 1, 2),(3, 4, 5),(6, 7, 8),(0, 3, 6),(1, 4, 7),(2, 5, 8),(0, 4, 8),(2, 4, 6)]
def generate_colors():
	global x_color, o_color
	x_color = random.choice(COLORS)
	o_color = random.choice(COLORS)
	while x_color == o_color:
		o_color = random.choice(COLORS)
score_card_items = {}

def update_score():
	score_card_items["wins"][0].itemconfig(score_card_items["wins"][1], text=str(wins))
	score_card_items["losses"][0].itemconfig(score_card_items["losses"][1], text=str(losses))
	score_card_items["draws"][0].itemconfig(score_card_items["draws"][1], text=str(draws))

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=20, **kwargs):
	points = [
		x1 + radius, y1,
		x2 - radius, y1,
		x2, y1,
		x2, y1 + radius,
		x2, y2 - radius,
		x2, y2,
		x2 - radius, y2,
		x1 + radius, y2,
		x1, y2,
		x1, y2 - radius,
		x1, y1 + radius,
		x1, y1,
	]
	return canvas.create_polygon(points, smooth=True, **kwargs)

def create_score_card(parent, icon, title, color):
	# Create a frame wrapper so cards can expand evenly in a single row
	card_width = 144
	card_height = 96
	wrapper = tk.Frame(parent, bg=BG_COLOR)
	wrapper.pack(side=tk.LEFT, expand=True, fill="x", padx=12)
	# canvas slightly larger to draw shadow
	card_canvas = tk.Canvas(wrapper, width=card_width + 12, height=card_height + 12, bg=BG_COLOR, bd=0, highlightthickness=0)
	card_canvas.pack(expand=True, fill="both")
	# shadow
	shadow_color = "#071421"
	card_canvas.create_rectangle(6, 6, card_width + 6, card_height + 6, fill=shadow_color, outline="", stipple="gray12")
	# rounded colored card
	draw_rounded_rect(card_canvas, 0, 0, card_width, card_height, radius=14, fill=color, outline="")
	# icon, title and value
	card_canvas.create_text(20, 24, text=icon, font=("Segoe UI Emoji", 16), fill="white", anchor="w")
	card_canvas.create_text(20, 42, text=title, font=("Segoe UI Semibold", 8), fill="#E8EEF6", anchor="w")
	value_id = card_canvas.create_text(card_width - 12, 66, text="0", font=("Segoe UI Bold", 22), fill="white", anchor="e")

	# hover effects: subtle brighten and lift
	def on_enter(e):
		card_canvas.scale("all", 0, 0, 1.02, 1.02)
		# brighten by overlaying translucent white
		card_canvas.create_rectangle(0, 0, card_width, card_height, fill="#ffffff", stipple="gray25", outline="", tags=("hover_overlay",))

	def on_leave(e):
		card_canvas.scale("all", 0, 0, 1.0/1.02, 1.0/1.02)
		card_canvas.delete("hover_overlay")

	card_canvas.bind("<Enter>", on_enter)
	card_canvas.bind("<Leave>", on_leave)

	return card_canvas, value_id

def check_winner(player):
	for combo in winning_combinations:
		if all(board[pos] == player for pos in combo):
			return True
	return False
def is_draw():
	return "" not in board
def disable_board():
	for btn in buttons:
		btn.config(state=tk.DISABLED)
def enable_board():
	for i, btn in enumerate(buttons):
		if board[i] == "":
			btn.config(state=tk.NORMAL)
def hex_to_rgb(hex_color):
	hex_color = hex_color.lstrip("#")
	return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def interpolate_color(color1, color2, t):
	r1, g1, b1 = hex_to_rgb(color1)
	r2, g2, b2 = hex_to_rgb(color2)
	r = int(r1 + (r2 - r1) * t)
	g = int(g1 + (g2 - g1) * t)
	b = int(b1 + (b2 - b1) * t)
	return f"#{r:02x}{g:02x}{b:02x}"

def create_gradient_photo(width, height, start_color, end_color):
	image = Image.new("RGB", (width, height), start_color)
	draw = ImageDraw.Draw(image)
	r1, g1, b1 = hex_to_rgb(start_color)
	r2, g2, b2 = hex_to_rgb(end_color)
	for y in range(height):
		t = y / (height - 1)
		r = int(r1 + (r2 - r1) * t)
		g = int(g1 + (g2 - g1) * t)
		b = int(b1 + (b2 - b1) * t)
		draw.line([(0, y), (width, y)], fill=(r, g, b))
	return ImageTk.PhotoImage(image)

def animate_button_hover(widget, entering):
	if widget["state"] != tk.NORMAL:
		return
	if not hasattr(widget, "_hover_progress"):
		widget._hover_progress = 0.0
	step = 0.2
	if entering:
		widget._hover_progress = min(widget._hover_progress + step, 1.0)
	else:
		widget._hover_progress = max(widget._hover_progress - step, 0.0)
	t = widget._hover_progress
	new_bg = interpolate_color(BUTTON_COLOR, BUTTON_HOVER, t)
	widget.config(bg=new_bg)
	if (entering and t < 1.0) or (not entering and t > 0.0):
		widget.after(25, lambda: animate_button_hover(widget, entering))

def on_button_enter(event):
	if event.widget["state"] == tk.NORMAL:
		animate_button_hover(event.widget, True)

def on_button_leave(event):
	if event.widget["state"] == tk.NORMAL:
		animate_button_hover(event.widget, False)
def easy_move():
	available = [
		i for i in range(9)
		if board[i] == ""]
	return random.choice(available)
def hard_move():
	for move in range(9):
		if board[move] == "":
			board[move] = "O"
			if check_winner("O"):
				board[move] = ""
				return move
			board[move] = ""
	for move in range(9):
		if board[move] == "":
			board[move] = "X"
			if check_winner("X"):
				board[move] = ""
				return move
			board[move] = ""
	available = [
		i for i in range(9)
		if board[i] == ""]
	return random.choice(available)
def winner_temp(temp_board, player):
	for combo in winning_combinations:
		if all(
			temp_board[pos] == player
			for pos in combo):
			return True
	return False
def minimax(temp_board, depth, is_max):
	if winner_temp(temp_board, "O"):
		return 1
	if winner_temp(temp_board, "X"):
		return -1
	if "" not in temp_board:
		return 0
	if is_max:
		best_score = -100
		for i in range(9):
			if temp_board[i] == "":
				temp_board[i] = "O"
				score = minimax(temp_board,depth + 1,False)
				temp_board[i] = ""
				best_score = max(best_score,score)
		return best_score
	best_score = 100
	for i in range(9):
		if temp_board[i] == "":
			temp_board[i] = "X"
			score = minimax(temp_board,depth + 1,True)
			temp_board[i] = ""
			best_score = min(best_score,score)
	return best_score
def impossible_move():
	best_score = -100
	best_move = None
	for i in range(9):
		if board[i] == "":
			board[i] = "O"
			score = minimax(board,0,False)
			board[i] = ""
			if score > best_score:
				best_score = score
				best_move = i
	return best_move
def show_bear_only():
	# Remove all widgets except the background image
	for widget in root.winfo_children():
		if widget is background_label:
			continue
		try:
			widget.destroy()
		except Exception:
			pass
	disable_board()

def show_game_over_popup(title, message):
	popup = tk.Toplevel(root)
	popup.title(title)
	popup.configure(bg=BG_COLOR)
	popup.resizable(False, False)
	popup.transient(root)
	popup.grab_set()
	popup_frame = tk.Frame(popup, bg="#0F172A", bd=2, relief="ridge")
	popup_frame.pack(expand=True, fill="both", padx=10, pady=10)
	tk_title = tk.Label(popup_frame, text=title, font=("Segoe UI Semibold", 18, "bold"), bg="#0F172A", fg=ACCENT_COLOR)
	tk_title.pack(pady=(12, 4))
	message_label = tk.Label(popup_frame, text=message, font=("Segoe UI", 14), bg="#0F172A", fg=TEXT_COLOR)
	message_label.pack(pady=(0, 8))
	stats_label = tk.Label(popup_frame, text=f"Wins: {wins}   Losses: {losses}   Draws: {draws}", font=("Segoe UI", 12), bg="#0F172A", fg=TEXT_COLOR)
	stats_label.pack(pady=(0, 12))
	button_frame = tk.Frame(popup_frame, bg="#0F172A")
	button_frame.pack(pady=(8, 12))
	def on_play_again():
		popup.destroy()
		reset_game()
	def on_exit():
		root.destroy()
	play_again_btn = tk.Button(button_frame, text="PLAY AGAIN", command=on_play_again, width=12, font=("Arial", 11, "bold"), bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=2, relief="groove")
	exit_btn = tk.Button(button_frame, text="EXIT", command=on_exit, width=12, font=("Arial", 11, "bold"), bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=2, relief="groove")
	play_again_btn.grid(row=0, column=0, padx=10)
	exit_btn.grid(row=0, column=1, padx=10)
	play_again_btn.bind("<Enter>", on_button_enter)
	play_again_btn.bind("<Leave>", on_button_leave)
	exit_btn.bind("<Enter>", on_button_enter)
	exit_btn.bind("<Leave>", on_button_leave)
	root.update_idletasks()
	x = root.winfo_rootx() + (root.winfo_width() - popup.winfo_width()) // 2
	y = root.winfo_rooty() + (root.winfo_height() - popup.winfo_height()) // 2
	popup.geometry(f"+{x}+{y}")

def ask_play_again(title, message):
	show_game_over_popup(title, message)

def computer_move():
	global losses
	global draws
	available = [i for i in range(9)if board[i] == ""]
	if not available:
		return
	if difficulty == "Easy":
		move = easy_move()
	elif difficulty == "Hard":
		move = hard_move()
	else:
		move = impossible_move()
	board[move] = "O"
	buttons[move].config(text="O",fg=o_color,state=tk.DISABLED)
	if check_winner("O"):
		losses += 1
		update_score()
		status_label.config(text="Computer Wins!")
		disable_board()
		# show custom popup instead of simple messagebox
		root.after(200, lambda: ask_play_again("Computer Wins!", "Computer Wins!"))
		return
	if is_draw():
		draws += 1
		update_score()
		status_label.config(text="Draw!")
		disable_board()
		root.after(200, lambda: ask_play_again("Draw", "It's a Draw!"))
		return
	status_label.config(text=f"{player_name}'s Turn (X)")
	enable_board()

def player_move(i):
	global wins
	global draws
	if board[i] != "":
		return
	board[i] = "X"
	buttons[i].config(text="X",fg=x_color,state=tk.DISABLED)
	if check_winner("X"):
		wins += 1
		update_score()
		status_label.config(text=f"{player_name} Wins!")
		disable_board()
		root.after(200, lambda: ask_play_again("Winner", f"{player_name} Wins!"))
		return
	if is_draw():
		draws += 1
		update_score()
		status_label.config(text="Draw!")
		disable_board()
		root.after(200, lambda: ask_play_again("Draw", "It's a Draw!"))
		return
	disable_board()
	status_label.config(text="Computer Thinking...")
	root.after(500,computer_move)

def reset_game():
	global board
	board = [""] * 9
	generate_colors()
	for btn in buttons:
		btn.config(text="",state=tk.NORMAL,bg=BUTTON_COLOR)
	status_label.config(text=f"{player_name}'s Turn (X)")

def show_new_player_popup():
	popup = tk.Toplevel(root)
	popup.title("New Player")
	popup.configure(bg=BG_COLOR)
	popup.resizable(False, False)
	popup.transient(root)
	popup.grab_set()
	popup_frame = tk.Frame(popup, bg="#0F172A", bd=2, relief="ridge")
	popup_frame.pack(expand=True, fill="both", padx=10, pady=10)
	tk_title = tk.Label(popup_frame, text="New Player", font=("Segoe UI Semibold", 18, "bold"), bg="#0F172A", fg=ACCENT_COLOR)
	tk_title.pack(pady=(12, 4))
	message_label = tk.Label(popup_frame, text="Enter player name and choose difficulty below.", font=("Segoe UI", 13), bg="#0F172A", fg=TEXT_COLOR)
	message_label.pack(pady=(0, 10))
	form_frame = tk.Frame(popup_frame, bg="#0F172A")
	form_frame.pack(padx=10, pady=(0, 10), fill="x")
	name_label = tk.Label(form_frame, text="Player Name", font=("Segoe UI", 12), bg="#0F172A", fg=TEXT_COLOR)
	name_label.pack(anchor="w", pady=(0, 4))
	name_entry = tk.Entry(form_frame, font=("Segoe UI", 12), bd=2, relief="groove")
	name_entry.pack(fill="x", pady=(0, 10))
	name_entry.insert(0, player_name)
	difficulty_label_widget = tk.Label(form_frame, text="Difficulty", font=("Segoe UI", 12), bg="#0F172A", fg=TEXT_COLOR)
	difficulty_label_widget.pack(anchor="w", pady=(0, 4))
	diff_var = tk.StringVar(value=difficulty)
	difficulty_menu = tk.OptionMenu(form_frame, diff_var, *difficulty_options)
	difficulty_menu.config(font=("Segoe UI", 12), bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=0, highlightthickness=0)
	difficulty_menu.pack(fill="x", pady=(0, 6))
	button_frame = tk.Frame(popup_frame, bg="#0F172A")
	button_frame.pack(pady=(6, 12))
	result = {"name": None, "difficulty": None}
	def on_save():
		entered_name = name_entry.get().strip()
		chosen_diff = diff_var.get()
		if not entered_name:
			return
		result["name"] = entered_name
		result["difficulty"] = chosen_diff if chosen_diff in difficulty_options else "Easy"
		popup.destroy()
	def on_cancel():
		popup.destroy()
	save_btn = tk.Button(button_frame, text="SAVE", command=on_save, width=12, font=("Arial", 11, "bold"), bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=2, relief="groove")
	cancel_btn = tk.Button(button_frame, text="CANCEL", command=on_cancel, width=12, font=("Arial", 11, "bold"), bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=2, relief="groove")
	save_btn.grid(row=0, column=0, padx=10)
	cancel_btn.grid(row=0, column=1, padx=10)
	save_btn.bind("<Enter>", on_button_enter)
	save_btn.bind("<Leave>", on_button_leave)
	cancel_btn.bind("<Enter>", on_button_enter)
	cancel_btn.bind("<Leave>", on_button_leave)
	root.update_idletasks()
	x = root.winfo_rootx() + (root.winfo_width() - popup.winfo_reqwidth()) // 2
	y = root.winfo_rooty() + (root.winfo_height() - popup.winfo_reqheight()) // 2
	popup.geometry(f"+{x}+{y}")
	popup.wait_window()
	return result if result["name"] else None

def new_player():
	global player_name
	global difficulty
	global wins
	global losses
	global draws
	data = show_new_player_popup()
	if not data:
		return
	player_name = data["name"]
	difficulty = data["difficulty"]
	wins = 0
	losses = 0
	draws = 0
	player_label.config(text=f"Player: {player_name}")
	difficulty_label.config(text=f"Difficulty: {difficulty}")
	update_score()
	reset_game()

def start_game():
	global player_name, difficulty
	name = player_name_var.get().strip()
	if not name:
		name = "Player"
	level = difficulty_var.get()
	if level not in difficulty_options:
		level = "Easy"
	player_name = name
	difficulty = level
	if welcome_frame.winfo_exists():
		welcome_frame.destroy()
	create_game_ui()


def create_game_ui():
	global player_label, difficulty_label, status_label, game_frame
	content_frame = tk.Frame(root, bg=BG_COLOR)
	content_frame.pack(expand=True, fill="both", padx=24, pady=16)

	header_frame = tk.Frame(content_frame, bg=BG_COLOR)
	header_frame.pack(pady=(0, 14), fill="x")
	header_photo = create_gradient_photo(760, 90, "#0F172A", "#06B6D4")
	header_canvas = tk.Canvas(header_frame, width=760, height=90, bd=0, highlightthickness=0)
	header_canvas.create_image(0, 0, image=header_photo, anchor="nw")
	header_canvas.create_text(380, 34, text="🏆  TIC TAC TOE ULTIMATE", fill="white", font=("Segoe UI Semibold", 24, "bold"))
	header_canvas.create_text(380, 62, text="Premium arcade experience", fill="#D1E8FF", font=("Segoe UI", 11, "italic"))
	header_canvas.pack()
	header_canvas.image = header_photo

	# Glassmorphism card for player info (centered, rounded corners, padding, subtle shadow)
	card_width = 620
	card_height = 100
	card_canvas = tk.Canvas(content_frame, width=card_width, height=card_height, bg=BG_COLOR, bd=0, highlightthickness=0)
	card_canvas.pack(pady=(0, 16))
	# shadow
	shadow_offset = 6
	card_canvas.create_rounded_rect = lambda x1, y1, x2, y2, r, **kw: (
		card_canvas.create_arc(x1, y1, x1+2*r, y1+2*r, start=90, extent=90, style='pieslice', **kw),
		card_canvas.create_arc(x2-2*r, y1, x2, y1+2*r, start=0, extent=90, style='pieslice', **kw),
		card_canvas.create_arc(x1, y2-2*r, x1+2*r, y2, start=180, extent=90, style='pieslice', **kw),
		card_canvas.create_arc(x2-2*r, y2-2*r, x2, y2, start=270, extent=90, style='pieslice', **kw),
		card_canvas.create_rectangle(x1+r, y1, x2-r, y2, **kw),
		card_canvas.create_rectangle(x1, y1+r, x2, y2-r, **kw)
	)
	# draw subtle shadow
	card_canvas.create_rounded_rect(shadow_offset, shadow_offset, card_width-1+shadow_offset, card_height-1+shadow_offset, 14, fill="#071026")
	# draw glass card (slightly translucent look via light color)
	card_canvas.create_rounded_rect(0, 0, card_width-1, card_height-1, 14, fill="#0B1220")

	# Place labels on the canvas centered inside the card with padding
	inner_frame = tk.Frame(card_canvas, bg="#0B1220")
	player_label = tk.Label(inner_frame, text=f"Player: {player_name}", font=("Segoe UI Semibold", 16, "bold"), bg="#0B1220", fg=TEXT_COLOR)
	player_label.pack(anchor="w")
	difficulty_label = tk.Label(inner_frame, text=f"Difficulty: {difficulty}", font=("Segoe UI", 13), bg="#0B1220", fg=TEXT_COLOR)
	difficulty_label.pack(anchor="w", pady=(6, 0))
	# padding and centering
	card_canvas.create_window(card_width//2 - 20, card_height//2, window=inner_frame)

	score_frame = tk.Frame(content_frame, bg=BG_COLOR)
	score_frame.pack(pady=(0, 20), fill="x")
	score_card_items["wins"] = create_score_card(score_frame, "🏆", "Wins", "#0E9F6E")
	score_card_items["losses"] = create_score_card(score_frame, "💀", "Losses", "#BE123C")
	score_card_items["draws"] = create_score_card(score_frame, "🤝", "Draws", "#F59E0B")

	status_label = tk.Label(content_frame, text=f"{player_name}'s Turn (X)", font=("Arial", 16), bg=BG_COLOR, fg=TEXT_COLOR)
	status_label.pack(pady=(0, 14))

	board_container = tk.Frame(content_frame, bg=BG_COLOR)
	board_container.pack(pady=(0, 14), fill="x")
	game_frame = tk.Frame(board_container, bg=BG_COLOR, bd=3, relief="ridge", highlightbackground=ACCENT_COLOR, highlightcolor=ACCENT_COLOR, highlightthickness=2)
	game_frame.pack(padx=8, pady=0)

	for i in range(9):
		btn = tk.Button(game_frame, text="", font=("Arial", 18, "bold"), width=4, height=1, bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, relief="raised", bd=4, command=lambda i=i: player_move(i))
		btn.grid(row=i // 3, column=i % 3, padx=4, pady=4)
		btn.bind("<Enter>", on_button_enter)
		btn.bind("<Leave>", on_button_leave)
		buttons.append(btn)

	button_frame = tk.Frame(content_frame, bg=BG_COLOR)
	button_frame.pack(pady=(0, 14))
	new_game_btn = tk.Button(button_frame, text="NEW GAME", width=12, font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=2, relief="groove", command=reset_game)
	new_game_btn.grid(row=0, column=0, padx=10)
	new_game_btn.bind("<Enter>", on_button_enter)
	new_game_btn.bind("<Leave>", on_button_leave)
	new_player_btn = tk.Button(button_frame, text="NEW PLAYER", width=12, font=("Arial", 12, "bold"), bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=2, relief="groove", command=new_player)
	new_player_btn.grid(row=0, column=1, padx=10)
	new_player_btn.bind("<Enter>", on_button_enter)
	new_player_btn.bind("<Leave>", on_button_leave)
	generate_colors()
	update_score()
	reset_game()


welcome_frame = tk.Frame(root, bg=BG_COLOR)
welcome_frame.pack(expand=True, fill="both")

# Decorative header with gradient and logo
hdr_photo = create_gradient_photo(760, 140, "#061021", "#06384a")
hdr_can = tk.Canvas(welcome_frame, width=760, height=140, bd=0, highlightthickness=0, bg=BG_COLOR)
hdr_can.create_image(0, 0, image=hdr_photo, anchor="nw")
hdr_can.create_text(120, 64, text="🎮", font=("Segoe UI Emoji", 64))
hdr_can.create_text(420, 42, text="Tic Tac Toe Studio", fill="#E6FFFF", font=("Segoe UI Semibold", 26, "bold"))
hdr_can.create_text(420, 70, text="Premium Arcade Experience", fill="#BFEAF6", font=("Segoe UI", 11, "italic"))
hdr_can.pack(pady=(24, 6))
hdr_can.image = hdr_photo

# Center card with glassmorphism look for the welcome controls
card_w, card_h = 700, 320
card = tk.Canvas(welcome_frame, width=card_w, height=card_h, bg=BG_COLOR, bd=0, highlightthickness=0)
card.pack(pady=(6, 24))
draw_rounded_rect(card, 6, 6, card_w - 6, card_h - 6, radius=18, fill="#071421")
draw_rounded_rect(card, 0, 0, card_w - 12, card_h - 12, radius=18, fill="#0B1220")

inner = tk.Frame(card, bg="#0B1220")
card.create_window(card_w//2, card_h//2, window=inner)

logo_label = tk.Label(inner, text="🎮", font=("Segoe UI Emoji", 48), bg="#0B1220")
logo_label.grid(row=0, column=0, rowspan=2, padx=(16, 24))
title_label = tk.Label(inner, text="Welcome to Tic Tac Toe", font=("Segoe UI Semibold", 20, "bold"), bg="#0B1220", fg=ACCENT_COLOR)
title_label.grid(row=0, column=1, sticky="w")
subtitle_label = tk.Label(inner, text="Enter your name and pick a difficulty to begin.", font=("Segoe UI", 11), bg="#0B1220", fg="#D1E8FF")
subtitle_label.grid(row=1, column=1, sticky="w", pady=(4, 12))

name_label = tk.Label(inner, text="Player Name", font=("Segoe UI", 12), bg="#0B1220", fg=TEXT_COLOR)
name_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=(16,0))
name_entry = tk.Entry(inner, textvariable=player_name_var, font=("Segoe UI", 12), bd=2, relief="groove")
name_entry.grid(row=3, column=0, columnspan=2, padx=16, pady=(6, 12), sticky="we")

# Stylish difficulty buttons
diff_frame = tk.Frame(inner, bg="#0B1220")
diff_frame.grid(row=4, column=0, columnspan=2, padx=16, sticky="we")
tk.Label(diff_frame, text="Difficulty", font=("Segoe UI", 12), bg="#0B1220", fg=TEXT_COLOR).pack(anchor="w")

def make_diff_btn(text, val, color):
	def set_val():
		difficulty_var.set(val)
		# visual feedback
		for b in diff_frame.winfo_children():
			if getattr(b, "is_diff_btn", False):
				b.config(relief="raised")
		btn.config(relief="sunken")
	btn = tk.Button(diff_frame, text=text, command=set_val, width=12, font=("Segoe UI", 11, "bold"), bg=color, fg="white", bd=2)
	btn.is_diff_btn = True
	btn.pack(side="left", padx=8, pady=8)
	return btn

btn_easy = make_diff_btn("EASY", "Easy", "#0E9F6E")
btn_hard = make_diff_btn("HARD", "Hard", "#F59E0B")
btn_imp = make_diff_btn("IMPOSSIBLE", "Impossible", "#BE123C")

# default selection visual
if difficulty_var.get() == "Hard":
	btn_hard.config(relief="sunken")
elif difficulty_var.get() == "Impossible":
	btn_imp.config(relief="sunken")
else:
	btn_easy.config(relief="sunken")

button_row = tk.Frame(inner, bg="#0B1220")
button_row.grid(row=5, column=0, columnspan=2, pady=(12,4))
start_button = tk.Button(button_row, text="START GAME", width=18, font=("Arial", 14, "bold"), bg=BUTTON_COLOR, fg=TEXT_COLOR, activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=0, relief="raised", command=start_game)
start_button.pack(side="left", padx=12)
start_button.bind("<Enter>", on_button_enter)
start_button.bind("<Leave>", on_button_leave)

credits = tk.Label(button_row, text="New Player / Play Again options appear in-game", font=("Segoe UI", 9), bg="#0B1220", fg="#9FBCCF")
credits.pack(side="left", padx=8)
root.mainloop()
