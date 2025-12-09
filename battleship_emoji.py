import tkinter as tk
from tkinter import messagebox
import random

BOARD_SIZE = 10
SHIPS = [5, 4, 3, 3, 2]  # кеме өлшемдері
EMO_SHIP = "🚢"
EMO_HIT = "💥"
EMO_MISS = "❌"

class BattleshipEmoji:
    def __init__(self, root):
        self.root = root
        self.root.title("Теңіз шайқасы — Emoji")
        self.phase = "place"
        self.current_player = 1
        self.boards = [[["O"]*BOARD_SIZE for _ in range(BOARD_SIZE)] for _ in range(2)]
        self.ships_left = [list(SHIPS), list(SHIPS)]
        self.ship_index = 0
        self.first_click = None

        self.info = tk.Label(root, text="", font=("Arial", 14))
        self.info.pack(pady=6)
        self.frame = tk.Frame(root)
        self.frame.pack()
        self.buttons = [[None]*BOARD_SIZE for _ in range(BOARD_SIZE)]
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                btn = tk.Button(self.frame, text=" ", width=3, height=1,
                                command=lambda r=r, c=c: self.on_click(r, c))
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

        self.turn_label = tk.Label(root, text="", font=("Arial", 12))
        self.turn_label.pack(pady=6)
        self.update_ui_placement()

    def update_ui_placement(self):
        idx = self.current_player-1
        size = self.ships_left[idx][self.ship_index] if self.ship_index < len(self.ships_left[idx]) else None
        if size:
            self.info.config(text=f"{self.current_player}-ойыншы: {size} клеткалы кеме — 1-басу: бастау, 2-басу: бағыт")
        else:
            self.info.config(text=f"{self.current_player}-ойыншы орналастыру аяқталды")
        self.turn_label.config(text=f"{self.current_player}-ойыншы орналастыруда...")
        self.render_board(idx, show_ships=True)

    def render_board(self, idx, show_ships=False):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = self.boards[idx][r][c]
                btn = self.buttons[r][c]
                btn.config(state="normal")
                if self.phase == "place":
                    btn.config(text=EMO_SHIP if show_ships and cell=="S" else " ", bg="SystemButtonFace")
                else:
                    if cell=="X": btn.config(text=EMO_HIT)
                    elif cell=="*": btn.config(text=EMO_MISS)
                    else: btn.config(text=" ")

    def on_click(self, r, c):
        if self.phase=="place":
            self.place_click(r,c)
        else:
            self.play_click(r,c)

    def place_click(self, r,c):
        idx = self.current_player-1
        if self.ship_index>=len(self.ships_left[idx]): return
        size = self.ships_left[idx][self.ship_index]

        if self.first_click is None:
            if self.boards[idx][r][c]!="O": return
            self.first_click = (r,c)
            self.buttons[r][c].config(bg="#e8f4ff")
        else:
            r1,c1 = self.first_click
            dr,dc = r-r1, c-c1
            if abs(dr)+abs(dc)!=1: self.first_click=None; self.update_ui_placement(); return
            dr,dc = (dr//abs(dr) if dr!=0 else 0, dc//abs(dc) if dc!=0 else 0)
            if not self.can_place(self.boards[idx], r1,c1,size,(dr,dc)):
                self.first_click=None; self.update_ui_placement(); return
            for i in range(size):
                self.boards[idx][r1+i*dr][c1+i*dc]="S"
            self.ship_index+=1
            self.first_click=None
            if self.ship_index>=len(self.ships_left[idx]):
                if self.current_player==1: self.current_player=2; self.ship_index=0; self.update_ui_placement()
                else: self.phase="play"; self.current_player=1; self.info.config(text="Ойын басталды!"); self.update_ui_play()
            else: self.update_ui_placement()
        self.render_board(idx, show_ships=True)

    # ✅ Мұнда tuple unpacking орнына жай параметр
    def can_place(self, board, r, c, size, dir_vec):
        dr, dc = dir_vec
        cells=[]
        for i in range(size):
            rr,cc = r+i*dr, c+i*dc
            if not (0<=rr<BOARD_SIZE and 0<=cc<BOARD_SIZE): return False
            if board[rr][cc]!="O": return False
            cells.append((rr,cc))
        for rr,cc in cells:
            for adr in (-1,0,1):
                for adc in (-1,0,1):
                    nr,nc=rr+adr,cc+adc
                    if 0<=nr<BOARD_SIZE and 0<=nc<BOARD_SIZE and board[nr][nc]=="S" and (nr,nc) not in cells: return False
        return True

    def update_ui_play(self):
        self.turn_label.config(text=f"{self.current_player}-ойыншының кезегі (оқ ату)")
        self.render_board(1 if self.current_player==1 else 0, show_ships=False)

    def play_click(self,r,c):
        enemy = 1 if self.current_player==1 else 0
        cell = self.boards[enemy][r][c]
        if cell in ("X","*"): return
        if cell=="S":
            self.boards[enemy][r][c]="X"
            self.buttons[r][c].config(text=EMO_HIT)
            if self.check_win(self.boards[enemy]):
                messagebox.showinfo("Жеңіс!", f"{self.current_player}-ойыншы жеңді!")
                self.fireworks()
                for row in self.buttons:
                    for b in row: b.config(state="disabled")
                self.info.config(text=f"{self.current_player}-ойыншы жеңді!"); self.turn_label.config(text="Ойын аяқталды")
                return
        else:
            self.boards[enemy][r][c]="*"
            self.current_player=2 if self.current_player==1 else 1
        self.update_ui_play()

    def check_win(self,board):
        return all(cell!="S" for row in board for cell in row)

    def fireworks(self):
        colors=["red","yellow","orange","blue","purple","green"]
        for _ in range(20):
            x=random.randint(0,self.frame.winfo_width()-20)
            y=random.randint(0,self.frame.winfo_height()-20)
            c=random.choice(colors)
            l=tk.Label(self.frame,bg=c,width=2,height=1)
            l.place(x=x,y=y)
            self.frame.after(800,l.destroy)

if __name__=="__main__":
    root=tk.Tk()
    game=BattleshipEmoji(root)
    root.mainloop()
