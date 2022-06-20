
import threading, socket, os, random

player_total = 0
player_turn = 1

isWin = False
winner = 0
rand = 0

# IP for Localhost
host = "127.0.0.1"  
#port
port = 12000

#Create a server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Bind server to ip
server.bind((host, port))  
#Server listening
server.listen(2)  

#store client and multiple choice
clients = []
winCount = [0, 0]
tempRoll = [0, 0]

#Broadcast from one client to another
def broadcast(message):
    for client in clients:
        client.send(message)


#Handle client if want to send message or leave
def handle_client(client):
    global player_total, player_turn, winner, isWin, rand, tempRoll, winCount

    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            temp = message.split(" ")

            if int(temp[1]) == 1:
                player_turn = int(temp[0])

                rand = random.randint(1, 6)
                tempRoll[player_turn - 1] += rand

                if tempRoll[0] != 0 and tempRoll[1] != 0:
                    if tempRoll[0] > tempRoll[1]:
                        winCount[0] += 1
                    elif tempRoll[0] < tempRoll[1]:
                        winCount[1] += 1
                    tempRoll = [0, 0]

            if winCount[player_turn - 1] == 3:
                winner = player_turn
                isWin = True

            if player_turn == 1:
                player_turn = 2
            elif player_turn == 2:
                player_turn = 1

            if isWin == False:
                game()
            else:
                os.system("CLS")
                print("\nPlayer-1 Win Count\t: {}".format(winCount[0]))
                print("Player-2 Win Count\t: {}".format(winCount[1]))
                print("GAME OVER! The Winner is Player-{}".format(winner))

                for index, client in enumerate(clients):
                    client.send(
                        f"gameover? {str(winner)} {winCount[index]}".encode("utf-8")
                    )

        except:
            #delete and close connection
            index = clients.index(client)
            clients.remove(client)
            client.close()

            print(f"Player-{index + 1} has left the game room!")
            player_total -= 1
            break


#server at the time of receiving
def receive():
    global player_total, clients, numbers
    print("Server is running and listening ...")
    
    #Server will always listening until player_total = 2
    while player_total < 2:
        client, address = server.accept()

        #Count player total
        player_total += 1
        print(f"Player-{player_total} has joined the game room!")

        #Storing to array
        clients.append(client)

        #Open thread for handle client connection
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

    game()


def game():
    global player_total, player_turn, winCount, tempRoll

    #Send the playerId to connected client
    os.system("CLS")
    for index, client in enumerate(clients):
        client.send(
            f"id? {str(index + 1)} {winCount[index]} {tempRoll[index]}".encode("utf-8")
        )

    print("Gamblers Master Started!")
    print("Player-{} turn\n".format(player_turn))
    print("Player-1 Win Count\t: {}".format(winCount[0]))
    print("Player-1 Last Roll\t: {}\n".format(tempRoll[0]))
    print("Player-2 Win Count\t: {}".format(winCount[1]))
    print("Player-2 Last Roll\t: {}\n".format(tempRoll[1]))

    broadcast(f"turn? {player_turn}".encode("utf-8"))


if __name__ == "__main__":
    receive()
