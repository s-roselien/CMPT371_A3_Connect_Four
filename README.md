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

This project is a two-player **Connect Four** game built using Python's Socket API over **TCP**. Two clients connect to a central server and play against each other in real time. The server handles all game logic, board state, move validation, and win/draw detection, ensuring clients cannot cheat by modifying their local state.

Each player sees a colourful terminal interface showing the board, whose turn it is, and the result of the game. Player 1 is represented by 🔴 in red and Player 2 by 🟡 in yellow.

## **2\. System Limitations & Edge Cases**

Add here

## **3\. Video Demo**

Our 2-minute video demonstration covering connection establishment, data exchange, real-time gameplay, and process termination can be viewed below:  
**▶️ Watch Project Demo on YouTube**

## **4\. Prerequisites (Fresh Environment)**

To run this project, you need:

- **Python 3.8** or higher
- 3 terminal window (one for server, one per client)
- All the files in the same folder

## **4\. Step-by-Step Run Guide**

Add here

## **5\. Technical Protocol Details**

We designed a custom application-layer protocol using plain text over TCP:

- **Message format:** `TYPE|payload\n`
- **Delimiter:** `\n` (newline) is appended to every message to handle TCP stream buffering

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
| `QUIT` | C → S | Player is leaving |


## **6\. Academic Integrity & References**

* **Code Origin:**
- README.md was adapted from the format of the template repo provided in the assignment instructions.
- The socket boilerplate and server structure was adapted from the course sample repo. 
- The Connect Four game logic, protocol design, and threading model were written by the group.
 
* **GenAI Usage:**  
- Claude was used to help polish the `README.md`.
* **References:** 
- [Python Socket Documentation](https://docs.python.org/3/library/socket.html)
- [Python Threading Documentation](https://docs.python.org/3/library/threading.html)
- [Connect Four Rules](https://en.wikipedia.org/wiki/Connect_Four)
