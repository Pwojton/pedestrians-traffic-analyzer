class Pedestrian:
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self, y, ped_id):
        self.y = y
        self.ped_id = ped_id


class PedestriansCounter:
    pedestrians = []
    pedestrians_coming_down = []
    pedestrians_coming_up = []
    y_threshold = 350

    def count_pedestrians(self, pedestrian_id, y):
        # pedestrian = Pedestrian(y, pedestrian_id)
        pedestrian = Pedestrian(y, pedestrian_id)
        if not any(obj.ped_id == pedestrian.ped_id for obj in self.pedestrians):
            print("Pedestrian ped_id", pedestrian.ped_id)
            self.pedestrians.append(pedestrian)

    def count_coming_up_or_down(self, pedestrian_id, y):
        pedestrian = Pedestrian(y, pedestrian_id)

        if any(obj.ped_id == pedestrian.ped_id for obj in self.pedestrians):
            found_pedestrian = next((obj for obj in self.pedestrians if obj.ped_id == pedestrian.ped_id), None)

            if 350 < y < found_pedestrian.y and found_pedestrian.ped_id not in self.pedestrians_coming_down:
                self.pedestrians_coming_down.append(found_pedestrian.ped_id)

            if 350 > y > found_pedestrian.y and found_pedestrian.ped_id not in self.pedestrians_coming_up:
                self.pedestrians_coming_up.append(found_pedestrian.ped_id)
