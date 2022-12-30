

class Trader:

    def __init__(self, df, line_regression_size=5, window_size=3, leverage=1, lot_size=1,
                 initial_money=10000, unit=1, reward=5, risk=-5):

        self.unit = unit
        self.df = df
        self.leverage = leverage
        self.initial_money = initial_money
        self.lot_size = lot_size
        self.price_list = df['open'].values
        self.volume_list = df['volume'].values
        self.bid_list = df['bid_open'].values
        self.ask_list = df['ask_open'].values
        self.first_time = True
        self.current_money = initial_money
        # for idx, spread in enumerate(df['spread'].values):
        #     self.bid_list.append(self.price_list[idx] + spread * 0.00001)
        #     self.ask_list.append(self.price_list[idx] - spread * 0.00001)
        self.line_regression_size = line_regression_size
        self.window_size = window_size
        self.abs_vwap = []

        sum_vxp = 0
        sum_vol = 0
        for price, volume in zip(self.price_list, self.volume_list):
            sum_vxp += price * volume
            sum_vol += volume

            self.abs_vwap.append(sum_vxp / sum_vol)
        self.window_vwap = []
        self.slopes = []
        self.property_track = [self.initial_money]
        self.profit_track = [0]
        self.have_bought = False
        self.have_sold = False
        self.total_shares = 0
        self.margin = None
        self.free_margin = None
        self.is_dynamic = True
        self.unit_list = [unit]
        self.total_reward = 0
        self.action = None
        self.go_long_indexes = []
        self.close_long_indexes = []
        self.go_short_indexes = []
        self.close_short_indexes = []
        self.rv = 0
        self.average_volume = 0
        self.first_time = True
        self.take_reward_indexes = []
        self.stop_bleeding_indexes = []
        self.short_term_vector = []
        self.criteria_signal = None
        self.risk = risk
        self.reward = reward
        self.bleeding_flag = False
        self.reward_flag = False




    def take_reward(self, idx):

        if self.profit_track[-1] >= self.reward:

            print(f'profit taking is happening Because profit={self.profit_track[-1]}')

            if self.have_bought:
                self.close_long(idx)
            if self.have_sold:
                self.close_short(idx)
            self.take_reward_indexes.append(idx)
            print(f'at take_reward, after closing the position: {self.profit_track[-1]}')
            taken_reward = self.current_money*(self.profit_track[-1]/100)
            print(f'taken reward: {taken_reward}')
            self.current_money -= taken_reward

            # self.profit_track.append(0)

            self.reward_flag = True

            self.total_reward += taken_reward

    def stop_bleeding(self, idx):

        if self.profit_track[-1] <= self.risk:

            if self.have_bought:
                self.close_long(idx)
            if self.have_sold:
                self.close_short(idx)
            self.take_reward_indexes.append(idx)

            self.bleeding_flag = True



    def go_back_market(self, idx):

        if self.price_list[idx] >= self.abs_vwap[idx] or self.price_list[idx] <= self.abs_vwap[idx]:

            self.bleeding_flag = False




    def calculate_window_vwap(self):

        price_volume = list(zip(self.price_list, self.volume_list))

        for idx, (price, volume) in enumerate(price_volume):

            sum_vol = 0
            sum_vxp = 0

            if idx + 1 < self.window_size:
                self.window_vwap.append(price)
            else:
                sum_vol += volume
                sum_vxp += price * volume

                for m in range(1, self.window_size):
                    sum_vol += price_volume[idx - m][1]
                    sum_vxp += price_volume[idx - m][0] * price_volume[idx - m][1]
                self.window_vwap.append(sum_vxp / sum_vol)


    def calculate_profit(self, idx):

        if idx == 0:
            return 0
        else:
            return ((self.property_track[-1] - self.initial_money) / self.initial_money) * 100

    def calculate_money(self, idx):
        if not self.have_bought and not self.have_sold:
            return self.current_money
        elif self.have_bought and not self.have_sold:
            m = self.bid_list[
                    idx] * self.total_shares - self.margin * self.leverage + self.free_margin + self.margin
            return m
        elif self.have_sold and not self.have_bought:
            m = -1 * self.ask_list[
                idx] * self.total_shares + self.margin * self.leverage + self.margin + self.free_margin
            return m

        else:
            raise Exception("Something is seriously wrong with algo")

    def unit_updater(self):

        if self.is_dynamic:
            diff = self.property_track[-1] - self.property_track[-2]
            change = diff / 10000
            self.unit += change
            self.unit = 100 if self.unit > 100 else self.unit
            self.unit = 0.01 if self.unit < 0.01 else self.unit
            self.unit_list.append(self.unit)

    def hold(self, idx):

        self.property_track.append(self.calculate_money(idx))
        self.profit_track.append(self.calculate_profit(idx))
        self.action = 'hold'

        return 'hold'

    def go_long(self, idx):

        self.margin = (self.unit * self.lot_size / self.leverage) * self.ask_list[idx]
        self.free_margin = self.current_money - self.margin
        self.total_shares += (self.margin * self.leverage / self.ask_list[idx])
        self.have_bought = True
        self.property_track.append(self.calculate_money(idx))
        self.profit_track.append(self.calculate_profit(idx))
        self.go_long_indexes.append(idx)
        self.action = 'go_long'

        return self.action

    def close_long(self, idx):

        self.have_bought = False
        self.current_money = self.bid_list[
                                 idx] * self.total_shares - self.margin * self.leverage + self.free_margin + self.margin

        self.total_shares = 0
        self.property_track.append(self.current_money)
        self.profit_track.append(self.calculate_profit(idx))

        self.close_long_indexes.append(idx)

        self.action = 'close_short'

        return self.action

    def go_short(self, idx):

        self.margin = (self.unit * self.lot_size / self.leverage) * self.bid_list[idx]
        self.free_margin = self.current_money - self.margin
        self.total_shares = self.margin * self.leverage / self.bid_list[idx]

        self.have_sold = True
        self.go_short_indexes.append(idx)
        self.property_track.append(self.calculate_money(idx))
        self.profit_track.append(self.calculate_profit(idx))

        self.action = "go_short"

        return self.action

    def close_short(self, idx):

        self.have_sold = False
        self.current_money = -self.ask_list[
            idx] * self.total_shares + self.margin * self.leverage + self.margin + self.free_margin
        self.total_shares = 0

        self.property_track.append(self.current_money)
        self.profit_track.append(self.calculate_profit(idx))
        self.close_short_indexes.append(idx)
        self.action = "close_short"

        return self.action


    def trade(self, idx):

        if self.first_time:
            self.first_time = False
            self.calculate_window_vwap()

        if idx <= 10:
            self.hold(idx)
            return

        if not self.bleeding_flag:


            if self.reward_flag:
                self.reward_flag = False



            consecutive_action = False
            if self.window_vwap[idx] > self.abs_vwap[idx]:
                if self.have_sold:
                    self.close_short(idx)
                    consecutive_action=True

                if self.have_bought:
                    self.hold(idx)
                else:
                    self.go_long(idx)
                if consecutive_action:
                    self.profit_track.pop()
                    self.property_track.pop()

            elif self.window_vwap[idx] < self.abs_vwap[idx]:

                if self.have_bought:

                    self.close_long(idx)
                    consecutive_action=True

                if self.have_sold:
                    self.hold(idx)
                else:
                    self.go_short(idx)

                if consecutive_action:
                    self.profit_track.pop()
                    self.property_track.pop()
            else:
                self.hold(idx)


            print(f'at idx={idx} after all is done, profit is {self.profit_track[-1]}')
            print(f'have_bought={self.have_bought}')
            print(f'have_sold={self.have_sold}')

            if idx > 1:

                self.take_reward(idx)

                if self.reward_flag:
                    return

                self.stop_bleeding(idx)

                if self.bleeding_flag:
                    return
        else:
            self.hold(idx)



