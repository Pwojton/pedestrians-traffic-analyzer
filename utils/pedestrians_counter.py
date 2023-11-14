import datetime
from typing import List
from database import push_pedestrian_track


class Spot:
    def __init__(self, spot_number, first_point, second_point):
        self.spot_number = spot_number
        self.first_point = first_point
        self.second_point = second_point


spot_1 = Spot(1, (830, 350), (1040, 720))
spot_1b = Spot(1111, (1040, 620), (1280, 720))
spot_2 = Spot(2, (1040, 450), (1280, 620))
spot_3 = Spot(3, (1040, 320), (1280, 450))
spot_12 = Spot(12, (810, 110), (990, 310))
spot_14 = Spot(14, (1000, 40), (1080, 240))
spot_6 = Spot(6, (440, 350), (810, 720))
spot_15 = Spot(15, (180, 40), (260, 240))
spot_13 = Spot(13, (270, 110), (430, 310))
spot_4 = Spot(4, (0, 320), (210, 450))
spot_5 = Spot(5, (0, 450), (210, 620))
spot_7 = Spot(7, (210, 350), (420, 720))
spot_7b = Spot(7777, (0, 620), (210, 720))
spot_11 = Spot(11, (440, 140), (820, 340))


class Pedestrian:
    def __init__(self, x_first, y_first, first_frame, x_last, y_last, last_frame, ped_id, x2_first, y2_first, x2_last,
                 y2_last):
        self.start_time = datetime.datetime.now()
        self.y_first = y_first
        self.x_first = x_first
        self.x2_first = x2_first
        self.y2_first = y2_first
        self.first_frame = first_frame
        self.ped_id = ped_id
        self.y_last = y_last
        self.x_last = x_last
        self.y2_last = y2_last
        self.x2_last = x2_last
        self.last_frame = last_frame
        self.spots = []
        self.alias = []
        self.isAliased = False


class PedestriansCounter:
    all_pedestrians: List[Pedestrian] = []

    def gather_all_pedestrians(self, x, y, frame_number, ped_id, x2, y2):
        if not any(obj.ped_id == ped_id for obj in self.all_pedestrians) and not (560 < x < 670 and 130 < y < 160):
            pedestrian = Pedestrian(x, y, frame_number, x, y, frame_number, ped_id, x2, y2, x2, y2)
            self.all_pedestrians.append(pedestrian)
        else:
            self.__update_pedestrian(x, y, frame_number, ped_id, x2, y2)
            self.__check_pedestrians_doubling(ped_id)
        self.__check_pedestrians_enter_and_exit(frame_number)

    def __update_pedestrian(self, x, y, frame_number, ped_id, x2, y2):
        pedestrian: Pedestrian = next(
            (pedestrian for pedestrian in self.all_pedestrians if pedestrian.ped_id == ped_id), None)
        if pedestrian is not None:
            pedestrian.last_frame = frame_number
            pedestrian.x_last = x
            pedestrian.y_last = y
            pedestrian.x2_last = x2
            pedestrian.y2_last = y2
        else:
            return

    def __check_pedestrians_doubling(self, ped_id):
        pedestrian: Pedestrian = next(
            (pedestrian for pedestrian in self.all_pedestrians if pedestrian.ped_id == ped_id), None)

        for ped in self.all_pedestrians:
            if ped.ped_id == ped_id or pedestrian.isAliased:
                continue
            if pedestrian.last_frame < ped.last_frame:
                continue
            if not pedestrian.last_frame - 30 < ped.last_frame < pedestrian.last_frame - 1:
                continue

            if pedestrian.x_last - 300 < ped.x_last < pedestrian.x_last + 300 and pedestrian.y_last - 300 < ped.y_last < pedestrian.y_last + 300:
                if not any(i == ped_id for i in ped.alias):
                    ped.alias.append(ped_id)
                    ped.isAliased = True

    def __check_pedestrians_enter_and_exit(self, frame_number):
        for pedestrian in self.all_pedestrians:
            spot_nr = check_which_spot_was_crossed(pedestrian.x_last, pedestrian.y_last)
            spot_nr2 = check_which_spot_was_crossed(pedestrian.x2_last, pedestrian.y2_last)

            if pedestrian.x_first >= pedestrian.x_last or pedestrian.y_first <= pedestrian.y_last:
                if spot_nr2 and spot_nr2 not in pedestrian.spots and (
                        len(pedestrian.spots) == 0 or (pedestrian.spots[-1]) and spot_nr2 != pedestrian.spots[-1]):
                    pedestrian.spots.append(spot_nr2)
                if spot_nr and spot_nr not in pedestrian.spots and (
                        len(pedestrian.spots) == 0 or (pedestrian.spots[-1]) and spot_nr != pedestrian.spots[-1]):
                    pedestrian.spots.append(spot_nr)
            else:
                if spot_nr and spot_nr not in pedestrian.spots and (
                        len(pedestrian.spots) == 0 or (pedestrian.spots[-1]) and spot_nr != pedestrian.spots[-1]):
                    pedestrian.spots.append(spot_nr)
                if spot_nr2 and spot_nr2 not in pedestrian.spots and (
                        len(pedestrian.spots) == 0 or (pedestrian.spots[-1]) and spot_nr2 != pedestrian.spots[-1]):
                    pedestrian.spots.append(spot_nr2)

            if frame_number - pedestrian.last_frame > 75:
                push_pedestrian_track(pedestrian.start_time,
                                      datetime.datetime.now(),
                                      pedestrian.ped_id,
                                      pedestrian.spots,
                                      pedestrian.alias
                                      )
                self.all_pedestrians.remove(pedestrian)
                continue


def check_which_spot_was_crossed(pedestrian_x, pedestrian_y):
    if (spot_1.first_point[0] < pedestrian_x < spot_1.second_point[0] and
        spot_1.first_point[1] < pedestrian_y < spot_1.second_point[1]) or (
            spot_1b.first_point[0] < pedestrian_x < spot_1b.second_point[0] and
            spot_1b.first_point[1] < pedestrian_y < spot_1b.second_point[1]
    ):
        return spot_1.spot_number
    if (spot_2.first_point[0] < pedestrian_x < spot_2.second_point[0] and
            spot_2.first_point[1] < pedestrian_y < spot_2.second_point[1]):
        return spot_2.spot_number
    if (spot_3.first_point[0] < pedestrian_x < spot_3.second_point[0] and
            spot_3.first_point[1] < pedestrian_y < spot_3.second_point[1]):
        return spot_3.spot_number
    if (spot_4.first_point[0] < pedestrian_x < spot_4.second_point[0] and
            spot_4.first_point[1] < pedestrian_y < spot_4.second_point[1]):
        return spot_4.spot_number
    if (spot_5.first_point[0] < pedestrian_x < spot_5.second_point[0] and
            spot_5.first_point[1] < pedestrian_y < spot_5.second_point[1]):
        return spot_5.spot_number
    if (spot_6.first_point[0] < pedestrian_x < spot_6.second_point[0] and
            spot_6.first_point[1] < pedestrian_y < spot_6.second_point[1]):
        return spot_6.spot_number
    if (spot_7.first_point[0] < pedestrian_x < spot_7.second_point[0] and
        spot_7.first_point[1] < pedestrian_y < spot_7.second_point[1]) or (
            spot_7b.first_point[0] < pedestrian_x < spot_7b.second_point[0] and
            spot_7b.first_point[1] < pedestrian_y < spot_7b.second_point[1]
    ):
        return spot_7.spot_number
    if (spot_11.first_point[0] < pedestrian_x < spot_11.second_point[0] and
            spot_11.first_point[1] < pedestrian_y < spot_11.second_point[1]):
        return spot_11.spot_number
    if (spot_12.first_point[0] < pedestrian_x < spot_12.second_point[0] and
            spot_12.first_point[1] < pedestrian_y < spot_12.second_point[1]):
        return spot_12.spot_number
    if (spot_13.first_point[0] < pedestrian_x < spot_13.second_point[0] and
            spot_13.first_point[1] < pedestrian_y < spot_13.second_point[1]):
        return spot_13.spot_number
    if (spot_14.first_point[0] < pedestrian_x < spot_14.second_point[0] and
            spot_14.first_point[1] < pedestrian_y < spot_14.second_point[1]):
        return spot_14.spot_number
    if (spot_15.first_point[0] < pedestrian_x < spot_15.second_point[0] and
            spot_15.first_point[1] < pedestrian_y < spot_15.second_point[1]):
        return spot_15.spot_number
