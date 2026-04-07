"""
CMPT 371 A3: Multiplayer Connect Four Server
Architecture: TCP Sockets with Multithreaded Client Handling
"""
import socket
import threading
import time

# Server configuration
HOST = '127.0.0.1'
PORT = 5555

# Message types
# All messages are plain text strings ending with \n
DELIMITER = "\n"
SEP = "|"

# Messages the server sends to clients
MSG_WAIT = "WAIT" # tell player 1 to wait for player 2
MSG_START = "START" # game is starting, tells client their player number
MSG_BOARD = "BOARD"  # sends the current board state 
MSG_YOUR_TURN = "YOUR_TURN" # it is this player's turn to move
MSG_OPPONENT_TURN = "OPPONENT_TURN" # the other player is moving, wait
MSG_WIN = "WIN"  # this player won
MSG_LOSE = "LOSE" # this player lost
MSG_DRAW = "DRAW"  # board is full, no winner
MSG_ERROR = "ERROR" # invalid move, includes reason why
MSG_OPPONENT_LEFT = "OPPONENT_LEFT" # other player disconnected or quit

# Messages the server receives from clients
MSG_MOVE = "MOVE"
MSG_QUIT = "QUIT"

#Board constants
ROWS = 6
COLS = 7
EMPTY = 0
PLAYER_1 = 1
PLAYER_2 = 2

# Build a message string and encode it to bytes ready to send over the socket.
def encode(msg_type, payload=None):
    if payload is not None:
        msg = f"{msg_type}{SEP}{payload}{DELIMITER}"
    else:
        msg = f"{msg_type}{DELIMITER}"
    return msg.encode("utf-8")

# Split a received message string into its type and payload
def decode(raw):
    if SEP in raw:
        parts = raw.split(SEP, 1)
        return parts[0].strip(), parts[1].strip()
    return raw.strip(), None


# Making a blank 6x7 board filled with zeroes
def create_board():
    board = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            row.append(EMPTY)
        board.append(row)
    return board

# Check if column in range and not already full
# Check if a piece can be dropped into this column
def is_valid_move(board, col):
    if col < 0 or col >= COLS:
        return False
    if board[0][col] == EMPTY:
        return True
    return False

# Drop the piece into the column, which falls due to gravity
def drop_piece(board, col, player):
    for row in range(ROWS -1, -1, -1):
        if board[row][col] == EMPTY:
            board[row][col] = player
            return row
    return -1

# Check if the player has 4 in a row
def check_winner(board, player):
    # Check horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if board[r][c] == player and board[r][c+1] == player and \
               board[r][c+2] == player and board[r][c+3] == player:
                return True

    # Check vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if board[r][c] == player and board[r+1][c] == player and \
               board[r+2][c] == player and board[r+3][c] == player:
                return True

    # Check diagonal down-right
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if board[r][c] == player and board[r+1][c+1] == player and \
               board[r+2][c+2] == player and board[r+3][c+3] == player:
                return True

    # Check diagonal down-left
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if board[r][c] == player and board[r+1][c-1] == player and \
               board[r+2][c-2] == player and board[r+3][c-3] == player:
                return True

    return False # no winner found

# The board is full when the entire top row is occupied
def is_draw(board):
    for c in range(COLS):
        if board[0][c] == EMPTY:
            return False
    return True

def serialize_board(board):
    # Flatten 2d board to a string so we can send it over the socket
    flat = []
    for r in range(ROWS):
        for c in range(COLS):
            flat.append(str(board[r][c]))
    return ",".join(flat)

# Shared game state
# These variables are shared between both player threads so they need protection
board = create_board()
current_player = PLAYER_1
board_lock = threading.Lock() # stops both threads editing board at same time
game_over_event = threading.Event() # set this when game ends so both threads stop
player_socket = {} # stores both client sockets


# Send a message, ignore errors if socket already closed
def safe_send(sock, msg_type, payload=None):
    try:
        sock.sendall(encode(msg_type, payload))
    except:
        pass

# Broadcasting same message to both the connected players at the same time
def send_to_both(msg_type, payload=None):
    for s in player_socket.values():
        safe_send(s, msg_type, payload)

def recv_msg(sock):
    """
    Read one complete message from socket
    TCP is a stream protocol - data arrives in chunks and not complete messages
    """
    data = b""
    while True:
        try:
            chunk = sock.recv(1024)
        except:
            return None # socket error
        if not chunk:
            return None # connection closed
        data += chunk
        if DELIMITER.encode() in data:
            line, _ =data.split(DELIMITER.encode(), 1)
            return line.decode("utf-8")
        
def handle_client(player_num, sock):
    """
    This function runs in its own thread for each player
    Manages the entire game loop for one player
    - tells the client which player they are
    - signals whose turn it is
    - receives and validates moves
    - check for win/draw after each move
    """
    global current_player, board

    # Figure out who the opponent is 
    if player_num == PLAYER_1:
        opponent = PLAYER_2     
    else:
        opponent = PLAYER_1

    # Tells client which player number they are
    safe_send(sock, MSG_START, str(player_num))
    print(f"[Server] Player {player_num} is ready")

    # Send initial empty board
    with board_lock:
        safe_send(sock, MSG_BOARD, serialize_board(board))
    
    while not game_over_event.is_set():

        # Check if it is this player's turn
        with board_lock:
            my_turn = (current_player == player_num)

        if my_turn:
            safe_send(sock, MSG_YOUR_TURN)

            # Wait for the given player to send a move
            raw = recv_msg(sock)
            if raw is None:
                # Player disconnected unexpectedly
                print(f"[Server] Player {player_num} disconnected")
                game_over_event.set()
                safe_send(player_socket[opponent], MSG_OPPONENT_LEFT)
                break

            msg_type, payload = decode(raw)

            # Player chose to quit voluntarily
            if msg_type == MSG_QUIT:
                print(f"[Server] Player {player_num} quit")
                game_over_event.set()
                safe_send(player_socket[opponent], MSG_OPPONENT_LEFT)
                break

            if msg_type != MSG_MOVE:
                safe_send(sock, MSG_ERROR, "expected a MOVE message")
                continue

            try:
                col = int(payload)
            except:
                safe_send(sock, MSG_ERROR, "column must be a number")
                continue

            # validate and apply the move inside the lock so both threads don't conflict
            with board_lock:
                if not is_valid_move(board, col):
                    safe_send(sock, MSG_ERROR, f"column {col+1} is full or invalid, pick another")
                    continue
                
                # Apply the move, the piece drops to lowest empty row
                drop_piece(board, col, player_num)

                # Sends the updated board to both players 
                send_to_both(MSG_BOARD, serialize_board(board))

                # Check if this move won the game
                if check_winner(board, player_num):
                    safe_send(sock, MSG_WIN)
                    safe_send(player_socket[opponent], MSG_LOSE)
                    print(f"[Server] Player {player_num} wins!")
                    game_over_event.set()
                    break

                # Check if the board is completely full with no winner
                if is_draw(board):
                    send_to_both(MSG_DRAW)
                    print("[Server] Draw!")
                    game_over_event.set()
                    break

                # Swap turn to the other player
                current_player = opponent

        else:
            # Not the given player turn, tell them to wait
            safe_send(sock, MSG_OPPONENT_TURN)
            #keep checking until game ends
            while not game_over_event.is_set():
                with board_lock:
                    if current_player == player_num:
                        break
                time.sleep(0.1)

    print(f"[Server] Player {player_num} thread done")
    try:
        # give the client time to process the WIN/LOSE message
        # and activate the game over event
        time.sleep(1)
        sock.close()
    except:
        pass

def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # SO_REUSEADDR allows us to restart the server quickly without "address already in use" errors
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_sock.bind((HOST, PORT))
    server_sock.listen()
    print(f"[Server] Listening on {HOST}:{PORT}, waiting for 2 players...")

    try:
        # Wait until exactly 2 players have connected
        connected = 0
        while connected < 2:
            client_sock, addr = server_sock.accept()
            connected += 1
            player_socket[connected] = client_sock
            print(f"[Server] Player {connected} connected from {addr}")

            # Tell player 1 to wait while we wait for player 2 
            if connected == 1:
                safe_send(client_sock, MSG_WAIT)

        print("[Server] Both players connected, starting game!")

        # Start a thread for each player
        threads = []
        for pnum in [PLAYER_1, PLAYER_2]:
            t = threading.Thread(target=handle_client, args=(pnum, player_socket[pnum]), daemon=True)
            t.start()
            threads.append(t)

        # Wait for both the threads to finish before closing the server
        for t in threads:
            t.join()

    except KeyboardInterrupt:
        print("\n[Server] Shutting down")
    finally:
        server_sock.close()


if __name__ == "__main__":
    start_server()