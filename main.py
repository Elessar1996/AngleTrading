
from VWAPTrader import Trader
import pandas as pd
import matplotlib.pyplot as plt
p = 0
# p=2

rates_frame = pd.read_csv('TSLA_General.csv')[p*390:(p+1)*390]
print(rates_frame)

proceed = input("Wish To Proceed?(Y/N): ")

risk = -5
reward = 5

if proceed == "Y" or proceed == "y":

    trader = Trader(df=rates_frame, leverage=5, unit=100, window_size=20, lot_size=1, reward=reward, risk=risk)

    for idx, _ in enumerate(trader.price_list):

        print(f'idx={idx} -- price: {trader.price_list[idx]}')
        trader.trade(idx)
        print(f'action: {trader.action}')
        print(f'profit: {trader.profit_track[-1]}')
        print(f'property: {trader.property_track[-1]}')

        print(f'total reward: {trader.total_reward}')
        print('----------------------------------------')


    print(f'final profit: {trader.total_reward + trader.property_track[-1] - trader.initial_money} $')
    print(f'final profit: {((trader.total_reward + trader.property_track[-1] - trader.initial_money)/trader.initial_money)*100} %')

    print(f'len(go long): {len(trader.go_long_indexes)}')
    print(f'len(close long): {len(trader.close_long_indexes)}')
    print(f'len(go short): {len(trader.go_short_indexes)}')
    print(f'len(close short): {len(trader.close_short_indexes)}')

    figure, axis = plt.subplots(2,1)
    axis[0].plot(trader.window_vwap, color='blue')
    axis[0].plot(trader.abs_vwap, color='cyan')
    axis[0].scatter(trader.go_long_indexes, [trader.window_vwap[i] for i in trader.go_long_indexes], color='red')
    axis[0].scatter(trader.close_long_indexes, [trader.window_vwap[i] for i in trader.close_long_indexes], color='green')
    axis[0].scatter(trader.go_short_indexes, [trader.window_vwap[i] for i in trader.go_short_indexes], color='orange')
    axis[0].scatter(trader.close_short_indexes, [trader.window_vwap[i] for i in trader.close_short_indexes], color='purple')
    axis[0].set_title('Price/VWAP')

    axis[1].plot(trader.profit_track, color='black')
    axis[1].scatter(trader.go_long_indexes, [trader.profit_track[i] for i in trader.go_long_indexes], color='red')
    axis[1].scatter(trader.close_long_indexes, [trader.profit_track[i] for i in trader.close_long_indexes], color='green')
    axis[1].scatter(trader.go_short_indexes, [trader.profit_track[i] for i in trader.go_short_indexes], color='orange')
    axis[1].scatter(trader.close_short_indexes, [trader.profit_track[i] for i in trader.close_short_indexes], color='purple')
    axis[1].set_title('PROFIT')


    plt.show()