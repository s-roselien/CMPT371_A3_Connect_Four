# **CMPT 371 A3 Socket Programming `Connect Four`**

**Course:** CMPT 371 \- Data Communications & Networking  
**Instructor:** Mirza Zaeem Baig  
**Semester:** Spring 2026  

## **Group Members**

| Name | Student ID | Email |
| :---- | :---- | :---- |
| Shelby Haines | 301548669 | srh11@sfu.ca |
| Meyer Kaur Sarna | 301556804 | mks53@sfu.ca | 

## **1\. Project Overview & Description**

This project is a two-player **Connect Four** game built using Python's Socket API over **TCP**. Two clients connect to a central server and play against each other in real time through a **graphical user interface (GUI)** built with Tkinter.

The server handles all game logic, board state, move validation, and win/draw detection, ensuring clients cannot cheat by modifying their local state. Each player sees a blue game board with red and yellow circles. Players clikc buttons to drop their piece into a column. The first player to connect 4 in a row (horizontally, vertically, or diagonally) wins.
- **Player 1** = 🔴 
- **Player 2** = 🟡 

## **2\. System Limitations & Edge Cases**

As required by the project specifications, we have identified and handled (or defined) the following limitations and potential issues within our application scope:

- **Exactly 2 players required:** the server waits for excatly 2 clients. No more or less.
- **No reconnection:** If a player disconnects mid-game, the game ends and other player sees "OPPONENT LEFT" on their screen.
- **One game per server run:** Restart the server to play again.
- **LAN/localhost only:** The server binds to localhost by default. For play over a network, change `HOST` in both `server.py` and `client.py` to the server machine's local IP address.
- **Tkinter thread safety:** Tkinter is not thread safe. All UI updates are scheduled on the main thread using `root.after()` to avoid crashes.
- **TCP stream buffering:** TCP is a continuous byte stream so multiple messages can arrive together. We handle this by appending `\n` to all messages and splitting on it to process them one at a time.

## **3\. Video Demo**

Our 2-minute video demonstration covering connection establishment, data exchange, real-time gameplay, and process termination can be viewed below:  
**▶️ Watch Project Demo on YouTube**

## **4\. Prerequisites (Fresh Environment)**

To run this project, you need:

- **Python 3.8** or higher
- **tkinter** - comes built into Python, no installation needed
- 3 terminal window (one for server, one per client)
- All commands run from inside the `src/` folder

## **5\. Installation**

**Step 1 - Clone the repo:**

```bash
git clone https://github.com/YOURUSERNAME/CMPT371_A3_Connect_Four.git
cd CMPT371_A3_Connect_Four
```
**Step 2 - No dependencies to install!**

tkinter is included with Python 3 by default. Non `pip install` needed.

## **6\. Step-by-Step Run Guide**

**Step 1 - Navigate to the src folder:**

```bash 
cd src
```

**Step 2 - Start the server:**

```bash 
python3 server.py
```

Expected output:

```
[Server] Listening on 127.0.0.1:5555, waiting for two players...
```
**Step 3 - Connect Player 1:**

Open a second terminal, navigate to `src/`, and run:

```bash
python3 client.py
```

A GUI window opens showing "Connected! Waiting for Player 2..."

**Step 4 - Connect Player 2:**

Open a third terminal, navigate to `src/`, and run:

```bash
python3 client.py
```

Both GUI windows update and the game begins immediately.

**Step 5 - Gameplay:**

1. The status bar at the top shows whose turn it is
1. When it is your turn, click any **Drop** buttom at the bottom to drop your piece into that column
1. The board updates on both screens after every move
1. When the game ends, a message appears on the board showing WIN, LOST, DRAW, or OPPONENT LEFT
1. Close the window to exit

## **7. Playing on Different Machines (same network)**

Find the server machine’s local IP:

```bash
# macOS / Linux
hostname -I

# Windows
ipconfig
```

Change `HOST` in both `server.py` and `client.py` to that IP:

```python
HOST = '192.168.X.X'
```

Then run as normal — the GUI client will connect to the server over the network.

## **8\. Technical Protocol Details**

We designed a custom application-layer protocol using plain text over TCP:

- **Message format:** `TYPE|payload\n`
- **Delimiter:** `\n` appends to every message to handle TCP stream buffering

| Message | Direction | Meaning |
|---------|-----------|---------|
| `WAIT` | S → C | You are Player 1, waiting for Player 2 |
| `START\|<1 or 2>` | S → C | Game starting, here is your player number |
| `BOARD\|<data>` | S → C | Updated board (42 comma-separated integers) |
| `YOUR_TURN` | S → C | Your turn to move |
| `OPPONENT_TURN` | S → C | Waiting for opponent |
| `WIN` | S → C | You won |
| `LOSE` | S → C | You lost |
| `DRAW` | S → C | Game is a draw |
| `ERROR\|<msg>` | S → C | Invalid move, try again |
| `OPPONENT_LEFT` | S → C | Opponent disconnected |
| `MOVE\|<col>` | C → S | Drop piece in this column (0-indexed) |


## **9\. Academic Integrity & References**

* **Code Origin:**
  - README.md was adapted from the format of the template repo provided in the assignment instructions.
  - The socket boilerplate and server structure was adapted from the course sample repo. 
  - The Connect Four game logic, protocol design, and threading model were written by the group.
 
* **GenAI Usage:**  
  - Claude was used to help polish the `README.md`.
  - Gemini was used to help develop the GUI in `client.py`.
  
* **References:** 
  - [Python Socket Documentation](https://docs.python.org/3/library/socket.html)
  - [Python Threading Documentation](https://docs.python.org/3/library/threading.html)
  - [Connect Four Rules](https://en.wikipedia.org/wiki/Connect_Four)
