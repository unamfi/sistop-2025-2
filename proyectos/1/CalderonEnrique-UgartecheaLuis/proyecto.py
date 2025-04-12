import random
import threading
import time
import tkinter as tk
import random

# This code simulates a gym where random people (brawny) train with different equipment.
# Each brawny has a unique ID and a list of equipment they will use for training.
# Up to 3 brawny can train at the same time with the same equipment.
# The code uses threading to simulate concurrent training sessions.

EQUIPMENT_NUM = 60
MAX_BRAWNY = EQUIPMENT_NUM * 3

#List of colors for brawny
BRAWNY_COLORS = [
    "red", "blue", "green", "yellow", "purple", "orange", "pink", "brown",
    "gray", "cyan", "magenta"
]

# Emojis of brawny
BRAWNY_EMOJIS = [ "💪", "🏋️‍♂️", "🏋️‍♀️", "🤸‍♂️", "🤸‍♀️" ]

# To limit the number of brawny that can train at the same time with the same equipment
class Equipment:
    def __init__(self, id: int):
        self.id = id # Equipment ID
        self.training_num = 0
        self.training_num_lock = threading.Semaphore(1)

    def __str__(self):
        return f"Equipment #{self.id}"

# Simulate the gym

# List of equipment in the gym
equipment_list = []
for i in range(EQUIPMENT_NUM):
   equipment_list.append(Equipment(i))

# Number of brawny in the gym counter, including a lock
brawnyInGym = 0
brawnyInGymLock = threading.Semaphore(1)

# Brawny class
# Each brawny has an ID, a training number, and a list of equipment they will use for training
# The training number indicates how many exercises the brawny will do
# The training equipment list is generated randomly, representing the equipment the brawny will use
# The brawny will enter the gym, train with the equipment, and leave the gym
# The brawny will wait if the gym is full
# The brawny will also check if the equipment is available (not in use by 3 or more brawny)
# The brawny will leave the gym if all the equipment is full and he has already done 5 exercises
class Brawny(threading.Thread):
    def __init__(self, id: int, gym_gui):
        super().__init__()
        self.id = id
        self.gym_gui = gym_gui
        self.training_num = random.randint(6,10)
        self.training_num_original = self.training_num # Original number of training exercises
        self.training_equipment = [] # Training routine list
        self.color = BRAWNY_COLORS[id % len(BRAWNY_COLORS)] # Color of the brawny
        self.emoji = BRAWNY_EMOJIS[id % len(BRAWNY_EMOJIS)] # Emoji of the brawny

        # Generate a random list of equipment for training
        while len(self.training_equipment) < self.training_num:
            equipment = random.randint(0, EQUIPMENT_NUM-1)
            if equipment not in self.training_equipment:
                self.training_equipment.append(equipment)
        # Sort the equipment list to ensure consistent order and avoid deadlocks
        sorted(self.training_equipment)

    def __str__(self):
        return f"Brawny {self.id}"

    def run(self):
        global brawnyInGym
        global brawnyInGymLock

        # Draw the brawny
        entrance_x, entrance_y = self.gym_gui.entrance_position
        self.gym_gui.create_brawny(self.id, self.emoji, entrance_x, entrance_y, self.color)

        #Try to enter the gym until the brawny can enter and train
        while True:
            # Check if the gym is full
            brawnyInGymLock.acquire()
            if brawnyInGym < MAX_BRAWNY:
                print(f"{self} has entered the gym")
                # Enter the gym, increment the counter of brawny in the gym
                brawnyInGym += 1
                brawnyInGymLock.release()

                # Enter the gym and training
                self.train()

                # Leave the gym, decrement the counter of brawny in the gym
                brawnyInGymLock.acquire()
                brawnyInGym -= 1
                brawnyInGymLock.release()
                print(f"{self} has left the gym")

                # Delete the brawny from the gym
                self.gym_gui.move_brawny(self.id, [self.gym_gui.get_equipment_position(-1), self.gym_gui.get_equipment_position(-2)], delete_brawny=True)

                break
            else:
                brawnyInGymLock.release()
                # Wait for a while before checking again
                print(f"{self} is returning later")

                # Move to LIDSoL
                path = [self.gym_gui.get_equipment_position(-1), self.gym_gui.get_equipment_position(-2)]
                self.gym_gui.move_brawny(self.id, path, delete_brawny=False)
                # Simulate waiting time
                time.sleep(3)

                # Move to the entrance
                path = [self.gym_gui.get_equipment_position(-2), self.gym_gui.get_equipment_position(-1)]
                self.gym_gui.move_brawny(self.id, path, delete_brawny=False)

    def train(self):
        global equipment_list
        last_equipment = -1

        # If the brawny is in the gym, start training until all exercises are done
        while self.training_num > 0:
            tn = self.training_num

            # Search for the equipment
            for equipment in self.training_equipment:
                # Check if the equipment is available (not in use by 3 or more brawnies)
                equipment_list[equipment].training_num_lock.acquire()
                if equipment_list[equipment].training_num < 3:
                    equipment_list[equipment].training_num += 1
                    equipment_list[equipment].training_num_lock.release()

                    # Calculate the path to the equipment use the calculate_brawny_path function
                    path_points = self.gym_gui.calculate_brawny_path(last_equipment, equipment)
                    # Move the brawny to the equipment
                    self.gym_gui.move_brawny(self.id, path_points, False)

                    # Simulate training time
                    print(f"{self} is using {equipment_list[equipment]}")
                    time.sleep(3)

                    # Release the equipment after training
                    equipment_list[equipment].training_num_lock.acquire()
                    equipment_list[equipment].training_num -= 1
                    equipment_list[equipment].training_num_lock.release()

                    # Decrease the number of exercises left
                    self.training_num -= 1
                    last_equipment = equipment
                    self.training_equipment.remove(equipment)
                else:
                    # If the equipment is full, release the lock and try next equipment
                    equipment_list[equipment].training_num_lock.release()

            # Check if all the equipment are full
            if tn == self.training_num:
                # If the brawny has done 5 exercises, he can leave the gym
                if self.training_num_original - self.training_num > 5:
                    break

        if self.training_num == 0:
            print(f"{self} has finished training")
        else:
            print(f"{self} has left the gym without finishing training")

        # If the brawny has finished training, move to the entrance
        path_points = self.gym_gui.calculate_brawny_path(last_equipment, -1)
        # Move the brawny to the entrance
        self.gym_gui.move_brawny(self.id, path_points, True)

class GymGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gym Simulator")
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.control_panel = tk.Frame(self.root)
        self.control_panel.pack(fill=tk.X, pady=5)
        self.brawny_count = 0
        self.brawny_count_label = tk.Label(self.control_panel, text="Brawny in gym: 0", font=("Courier", 14))
        self.brawny_count_label.pack(side=tk.LEFT, padx=10)
        self.canvas.bind("<Configure>", self.draw_gym)
        self.brawny_objects = {}

    def draw_gym(self, event=None):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.x_center = width // 2
        self.y_center = height // 2
        self.equipment_num = EQUIPMENT_NUM
        # Draw the gym

        # Draw rectangles representing the equipment
        rect_width = 100
        rect_height = 100
        rows = 6
        cols = 10
        padding = 50
        # Draw the gym square outline
        square_x1 = self.x_center - (cols * (rect_width + padding) // 2) - 50
        square_y1 = self.y_center - (rows * (rect_height + padding) // 2) - 30
        square_x2 = self.x_center + (cols * (rect_height + padding) // 2)
        square_y2 = self.y_center + (rows * (rect_height + padding) // 2)
        self.canvas.create_rectangle(square_x1, square_y1, square_x2, square_y2, outline="black", width=4)
        for r in range(rows):
            for c in range(cols):
                x1 = self.x_center - (cols * (rect_width + padding) // 2) + c * (rect_width + padding)
                y1 = self.y_center - (rows * (rect_height + padding) // 2) + r * (rect_height + padding)
                x2 = x1 + rect_width
                y2 = y1 + rect_height
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgray", outline="black", width=2)
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=f"Equipment\n{r * cols + c}", font=("Courier", 12), anchor="center", justify="center")

        # Entrance
        # Draw entrance tourniquet on the left of the canvas
        # Calculate the position of the first equipment on the left
        x1 = self.x_center - (10 * (rect_width + padding) // 2) - (padding) - rect_width
        y1 = self.y_center - (6 * (rect_height + padding) // 2)
        x2 = x1 + rect_width
        y2 = y1 + rect_height

        # Draw the entrance/exit rectangle divided diagonally
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=2)
        self.canvas.create_polygon(x1, y1, x2, y1, x1, y2, fill="green", outline="black")
        self.canvas.create_polygon(x2, y1, x2, y2, x1, y2, fill="red", outline="black")

        # Add text for Entrance and Exit
        self.canvas.create_text(x1 + 45, y1 + (rect_height*0.1), text="Entrance", font=("Courier", 12), anchor="center", justify="left", fill="white")
        self.canvas.create_text(x1 + 75, y1 + (rect_height*0.9), text="Exit", font=("Courier", 12), anchor="center", justify="right", fill="white")

        # Set the entrance position
        self.entrance_position = [x1 + rect_width * 0.25, y1 + rect_height * 0.5]

        #LIDSoL
        y1 = self.y_center + (rows * (rect_height + padding) // 2) - rect_height - padding
        y2 = y1 + rect_height
        self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="black", width=2)
        self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text="LIDSoL", font=("Courier", 12), anchor="center", justify="center", fill="white")
        self.lidsol_position = [(x1 + x2) / 2, (y1 + y2) / 2]

    def get_equipment_position(self, equipment_id):
        # Its the entrance
        if equipment_id == -1:
            return self.entrance_position
        # Its LIDSoL
        if equipment_id == -2:
            return self.lidsol_position

        pos = []
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        x_center = width // 2
        y_center = height // 2
        rect_width = 100
        rect_height = 100
        rows = 6
        cols = 10
        padding = 50
        x_top = x_center - (cols * (rect_width + padding) // 2) + rect_width // 2
        y_top = y_center - (rows * (rect_height + padding) // 2) + rect_height // 2

        # Calculate the position of the equipment with the given ID
        row = equipment_id // cols
        col = equipment_id % cols

        pos.append(x_top + col * (rect_width + padding))
        pos.append(y_top + row * (rect_height + padding))

        return pos

    def create_brawny(self, brawny_id, brawny_emoji, x, y, color):
        radius = 20
        brawny = self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color, outline="black"
        )
        label = self.canvas.create_text(
            x, y,
            text=str(brawny_id) + "\n" + brawny_emoji,
            font=("Courier", 10, "bold"),
            fill="white"
        )
        self.brawny_objects[brawny_id] = {"brawny": brawny, "label": label, "x_pos": x, "y_pos": y}

        # Update the brawny count label
        self.brawny_count += 1
        self.brawny_count_label.config(text=f"Brawny in gym: {self.brawny_count}")
        return brawny

    def calculate_brawny_path(self,origin_equipment_id, destination_equipment_id):
        rect_width = 100
        rect_height = 100
        padding = 50

        # Calculate the origin and destiny position based on the equipment ID
        origin = self.get_equipment_position(origin_equipment_id)
        destination = self.get_equipment_position(destination_equipment_id)

        # Calculate the path points
        path_points = []
        path_points.append(origin)

        # Get to a hallway crossing
        path_points.append([origin[0] + (rect_width // 2) + (padding // 2), origin[1] + (rect_height // 2) + (padding // 2)])

        # If it is going left or right
        if origin[0] > destination[0]:
            # Going left
            path_points.append([destination[0] + (rect_width // 2) + (padding // 2), origin[1] + (rect_height // 2) + (padding // 2)])
            # If it is going up or down
            path_points.append([destination[0] + (rect_width // 2) + (padding // 2), destination[1] + (rect_height // 2) + (padding // 2)])
        else:
            # Going right
            path_points.append([destination[0] - (rect_width // 2) - (padding // 2), origin[1] + (rect_height // 2) + (padding // 2)])
            # If it is going up or down
            path_points.append([destination[0] - (rect_width // 2) - (padding // 2), destination[1] + (rect_height // 2) + (padding // 2)])
        # Get to the center of the rectangle
        destination = self.get_equipment_position(destination_equipment_id)
        path_points.append(destination)

        return path_points

    def move_brawny(self, brawny_id, path_points, delete_brawny=True, on_exit=None):
        # Move the brawny along the path points

        # Verify if the brawny exists
        if brawny_id not in self.brawny_objects:
            return

        brawny_obj = self.brawny_objects[brawny_id]
        # Get the brawny object and label
        brawny = brawny_obj["brawny"]
        label = brawny_obj["label"]

        #Animation
        def animate_paths(points, idx=0):
            #If we reached the end of the path remove the brawny and label
            if idx >= len(points) - 1:
                if on_exit:
                    on_exit()
                if delete_brawny:
                    self.canvas.delete(brawny)
                    self.canvas.delete(label)
                    # Remove the brawny from the dictionary
                    del self.brawny_objects[brawny_id]
                    self.brawny_count -= 1
                    #Update the brawny count label
                    self.brawny_count_label.config(text=f"Brawny in gym: {self.brawny_count}")
                return
            
            #Get path distance
            start_x, start_y = points[idx]
            end_x, end_y = points[idx + 1]
            steps = 30
            dx = (end_x - start_x) / steps
            dy = (end_y - start_y) / steps

            def move_step(step):
                if step >= steps:
                    # Move to the next point
                    brawny_obj["x_pos"] = end_x
                    brawny_obj["y_pos"] = end_y
                    self.root.after(10, lambda: animate_paths(points, idx + 1))
                    return
                self.canvas.move(brawny, dx, dy)
                self.canvas.move(label, dx, dy)
                self.root.after(10, lambda: move_step(step + 1))

            move_step(0)

        animate_paths(path_points)

# Function to spawn and start a brawny thread
def spawn_brawnies(gym_gui, num_brawny=10):
    brawnies_count = 0

    def spawn_brawny():
        nonlocal brawnies_count
        if brawnies_count < num_brawny:
            brawny = Brawny(brawnies_count, gym_gui)
            brawny.start()
            brawnies_count += 1
            # Schedule the next spawn
            gym_gui.root.after(random.randint(100, 200), spawn_brawny)

    gym_gui.root.after(1000, spawn_brawny)

def main():
    print("Starting the gym simulation")
    root = tk.Tk()
    gym_gui = GymGUI(root)
    gym_gui.draw_gym()  # Draw the gym after the canvas is ready

    # Start the brawny threads
    spawn_brawnies(gym_gui, num_brawny=300)
    root.mainloop()

if __name__ == "__main__":
    main()