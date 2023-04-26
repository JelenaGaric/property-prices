import os

import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from constants import CSV_PATH

city_expert = pd.read_csv(os.path.join(CSV_PATH, 'city_expert_properties_2023-04-12_14-04-47.csv'))
print(city_expert.shape)

prices_per_location = city_expert[['location', 'price_per_size']]\
    .groupby('location').agg('mean').reset_index().sort_values(by="price_per_size", ascending=False)
# prices_per_location.plot(x="location", y="price_per_size", kind="bar", rot=60, fontsize=7)
# plt.show()


nekretnine_rs = pd.read_csv(os.path.join(CSV_PATH, 'nekretnine_rs_properties_2023-04-13_13-11-32.csv'))
print(nekretnine_rs.shape)

prices_per_location = nekretnine_rs[['location', 'price_per_size']]\
    .groupby('location').agg('mean').reset_index().sort_values(by="price_per_size", ascending=False)
# prices_per_location.plot(x="location", y="price_per_size", kind="bar", rot=60, fontsize=7)
# plt.show()


cetiri_zida = pd.read_csv(os.path.join(CSV_PATH, 'cetiri_zida_properties_2023-04-15_15-30-15.csv'))
print(cetiri_zida.shape)

prices_per_location = cetiri_zida[['location', 'price_per_size']]\
    .groupby('location').agg('mean').reset_index().sort_values(by="price_per_size", ascending=False)
prices_per_location.plot(x="location", y="price_per_size", kind="bar", rot=60, fontsize=7)
plt.show()


total = pd.concat((city_expert, nekretnine_rs, cetiri_zida))
prices_per_location = total[['location', 'price_per_size']]\
    .groupby('location').agg('mean').reset_index().sort_values(by="price_per_size", ascending=False)
prices_per_location.plot(x="location", y="price_per_size", kind="bar", rot=85, fontsize=7)
plt.show()



total['date_published']= pd.to_datetime(total['date_published'], format='ISO8601')
# remove the time zone information from all datetimes
total['date_published'] = total['date_published'].apply(lambda x: x.replace(tzinfo=None))
total.rename(columns={'date_published': 'date_time_published'}, inplace=True)
total['date_published'] = total['date_time_published'].dt.date
prices_per_date = total[['date_published', 'price_per_size']].groupby('date_published').agg('mean')

start_date = datetime.datetime.strptime('2023-01-01', '%Y-%m-%d').date()
prices_per_date = prices_per_date[prices_per_date.index >= start_date]

prices_per_date.plot(y='price_per_size', figsize=(10, 5))

plt.title('Price Per m^2 Over Time')
plt.xlabel('Date')
plt.ylabel('Price')

plt.show()

def remove_outliers(df: pd.DataFrame):
    # IQR
    Q1 = np.percentile(df['price_per_size'], 45, method='midpoint')
    Q3 = np.percentile(df['price_per_size'], 75, method='midpoint')
    IQR = Q3 - Q1
    # Upper bound
    upper = Q3 + 1.5 * IQR
    upper_array = np.array(df['price_per_size'] >= upper)
    # Lower bound
    lower = Q1 - 1.5 * IQR
    lower_array = np.array(df['price_per_size'] <= lower)
    # Removing the outliers
    df.drop(df[df.price_per_size <= lower].index, inplace=True)
    df.drop(df[df.price_per_size >= upper].index, inplace=True)


def plot_time_df_without_outliers(prices_per_date: pd.DataFrame):
    prices_per_date = prices_per_date.dropna()
    window_size = int(0.2 * len(prices_per_date))
    prices_per_date_outliers = pd.DataFrame()

    # Sliding window over ts + IQR
    for window in range(0, len(prices_per_date), window_size):
        df = prices_per_date.iloc[window: window + window_size]
        remove_outliers(df)
        prices_per_date_outliers = pd.concat([prices_per_date_outliers, df])

    prices_per_date.plot(y='price_per_size', figsize=(10, 5))

    plt.title('Price Per m^2 Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price')

    plt.show()