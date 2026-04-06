"""
CMPT 371 A3: Multiplayer Connect Four Client
Architecture: Tkinter GUI with Multithreaded Socket Communication
Reference: Gemini used to help develop the board GUI
"""
import socket
import threading
import tkinter as tk
from tkinter import messagebox

# Server configuration
HOST = '127.0.0.1'
PORT = 5555

# Message types
DELIMITER = "\n"
SEP = "|"

# Constants
ROWS = 6
COLS = 7

class ConnectFourGUI:
    def __init__(self, root, client_socket):
        """
        Input: root is a valid Tkinter root, client_socket is a connected socket
        Functionality: Initializes the GUI, game state, and starts listener thread
        """
        self.root = root
        self.sock = client_socket
        self.root.title("CMPT 371 - Multiplayer Connect Four")
        
        # Game state
        self.my_player_num = None
        self.is_my_turn = False
        self.game_active = True 
        # 6x7 board initialized to '0' (empty)
        self.board_data = [['0' for _ in range(COLS)] for _ in range(ROWS)]

        # UI Layout 
        self.status_label = tk.Label(
            root, 
            text="Connecting...", 
            font=('Helvetica', 16, 'bold'), 
            fg="blue")
        self.status_label.pack(pady=10)

        # Game Board Canvas
        self.canvas = tk.Canvas(root, width=700, height=600, bg='blue', highlightthickness=0)
        self.canvas.pack()
        
        self.draw_board()

        # Input Buttons 
        self.btn_frame = tk.Frame(root, width=700)
        self.btn_frame.pack(pady=10)

        self.buttons = []
        for i in range(COLS):
            # Styled buttons 
            # Each button sends a move for its column
            btn = tk.Button(self.btn_frame, text=f"Drop {i}", 
                            width=7, height=1,
                            font=('Helvetica', 10, 'bold'),
                            bg='#f0f0f0', activebackground='#d0d0d0',
                            relief='flat', cursor='hand2',
                            command=lambda c=i: self.send_move(c))
            btn.grid(row=0, column=i, padx=3)
            
            # Hover effects for UI feedback
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg='#e0e0e0'))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg='#f0f0f0'))
            
            self.buttons.append(btn)
        
        # Disable buttons until it is your turn
        self.set_buttons_state(False)

        # Background thread to receive network data 
        self.listen_thread = threading.Thread(target=self.listen_to_server, daemon=True)
        self.listen_thread.start()

    def set_buttons_state(self, enabled):
        """
        Input: enabled is a boolean
        Output: enables or disables the column buttons
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        for btn in self.buttons:
            btn.config(state=state)

    def draw_board(self):
        """
        Input: self.board_data is a 6x7 grid of 0, 1, and 2
        Output: Draws the grid circles based on the current board data.
        """
        self.canvas.delete("piece")
        for r in range(ROWS):
            for c in range(COLS):
                # Calculates circle position
                x0, y0 = c * 100 + 10, r * 100 + 10
                x1, y1 = x0 + 80, y0 + 80
                
                # Determine the board colours
                color = "white" # Default colour if empty
                if self.board_data[r][c] == '1': color = "red"
                elif self.board_data[r][c] == '2': color = "yellow"
                
                self.canvas.create_oval(
                    x0, y0, x1, y1, 
                    fill=color, 
                    outline="black", 
                    width=2, tags="piece")

    def show_overlay(self, text, color):
        """
        Input: Text is a string, color is valid for Tkinter
        Output: Displays a message directly on the board canvas.
        """
        self.canvas.create_rectangle(150, 250, 550, 350, fill="black", 
                                     stipple="gray75", outline=color, width=3)
        self.canvas.create_text(350, 300, text=text, font=('Helvetica', 30, 'bold'), fill=color)

    def send_move(self, col):
        """
        Input: col is between 0-6, and it is currently this client's turn
        Output: Send MOVE message to the server and disable input
        """
        if self.is_my_turn:
            try:
                msg = f"MOVE{SEP}{col}{DELIMITER}"
                self.sock.sendall(msg.encode('utf-8'))
                self.is_my_turn = False
                self.set_buttons_state(False)
                self.status_label.config(text="Move sent! Waiting...", fg="black")

            except Exception as e: 
                print(f"Error sending move: {e}")

    def listen_to_server(self):
        # Continuously receives and processes incoming data from the server
        buffer = "" # Stores partial TCP messages
        while self.game_active:
            try:
                data = self.sock.recv(1024).decode('utf-8')

                if not data: 
                    break # connection closed
                
                buffer += data
                # Process complete messages from the buffer
                while DELIMITER in buffer:
                    line, buffer = buffer.split(DELIMITER, 1)
                    self.process_message(line)

            except Exception as e:
                print(f"Connection error: {e}")
                break
        
        # If the loop broke but the game wasn't finished, it was an accidental disconnect
        if self.game_active:
            self.root.after(0, lambda: messagebox.showerror("Error", "Lost connection to server."))
            self.root.after(0, self.root.destroy)

    def process_message(self, line):
        """
        Input: line is a complete message from the server
        Output: Parses message, and schedules a UI update
        """
        if SEP in line:
            msg_type, payload = line.split(SEP, 1)
        else:
            msg_type, payload = line, None

        # UI updates on the main thread, Tkinter is not thread safe
        self.root.after(0, self._handle_ui_update, msg_type, payload)


    def _handle_ui_update(self, msg_type, payload):
        """
        Input: msg_type is a valid protocol command
        Output: Updates GUI based on server message
        """

        if msg_type == "WAIT":
            self.status_label.config(text="Connected! Waiting for Player 2...", fg="blue")
        
        elif msg_type == "START":
            self.my_player_num = payload
            color = "RED" if payload == "1" else "YELLOW"
            self.status_label.config(text=f"Game Started! You are {color}", fg="black")
        
        elif msg_type == "BOARD":
            if not payload:
                return
            flat = payload.split(',')
            # Convert flat list into a 2D board, 6x7
            self.board_data = [flat[i:i+COLS] for i in range(0, len(flat), COLS)]
            self.draw_board()
        
        elif msg_type == "YOUR_TURN":
            self.is_my_turn = True
            self.set_buttons_state(True)
            self.status_label.config(text="YOUR TURN!", fg="green")
        
        elif msg_type == "OPPONENT_TURN":
            self.status_label.config(text="Opponent's turn...", fg="black")
            self.set_buttons_state(False)

        elif msg_type in ["WIN", "LOSE", "DRAW", "OPPONENT_LEFT"]:
            self.game_active = False # Immediately stop the listener error-check
            self.set_buttons_state(False)
            
            if msg_type == "WIN":
                self.show_overlay("YOU WIN!", "green")
            elif msg_type == "LOSE":
                self.show_overlay("YOU LOST", "red")
            elif msg_type == "DRAW":
                self.show_overlay("DRAW!", "white")
            else:
                self.show_overlay("OPPONENT LEFT", "yellow")
            
            self.status_label.config(text="Game Over", fg="black")

            def safe_shutdown():
                try:
                    # shutdown socket before closing for a clean disconnect
                    self.sock.shutdown(socket.SHUT_RDWR)
                    self.sock.close()
                except:
                    pass

            # Close socket only after a short delay, to make sure the thread exits cleanly
            self.root.after(500, safe_shutdown)

        elif msg_type == "ERROR":
            self.status_label.config(text=f"ERROR: {payload}", fg="red")
            self.set_buttons_state(True)

def start_client():
    # Connects to server and displays the GUI
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.settimeout(5)
        client.connect((HOST, PORT))
        client.settimeout(None)
    except Exception as e:
        print(f"Could not connect to server: {e}")
        return

    root = tk.Tk()
    gui = ConnectFourGUI(root, client)
    root.mainloop()

if __name__ == "__main__":
    start_client()