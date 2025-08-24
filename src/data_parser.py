import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


def load_data(file_path):
    """Loads data from a CSV file."""
    try:
        df = pd.read_csv(file_path, low_memory=False)
        return df
    except FileNotFoundError:
        print(f"File not found at: {file_path}")
        return None


def prepare_data(df):
    """Cleans and prepares the data for analysis."""

    rename_map = {
        'datum': 'date',
        'hodina': 'hour',
        'den_v_tydnu': 'day_of_week',
    }
    df = df.rename(columns=rename_map)
    if 'hour' in df.columns:
        df = df.loc[df['hour'].between(0, 23)].copy()

    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    if 'day_of_week' in df.columns:
        days_mapping = {
            'pondělí': 'Weekday',
            'úterý': 'Weekday',
            'středa': 'Weekday',
            'čtvrtek': 'Weekday',
            'pátek': 'Weekday',
            'sobota': 'Weekend',
            'neděle': 'Weekend',
        }
        df['day_type'] = df['day_of_week'].map(days_mapping)

        days_czech_to_english = {
            'pondělí': 'Monday', 'úterý': 'Tuesday', 'středa': 'Wednesday',
            'čtvrtek': 'Thursday', 'pátek': 'Friday', 'sobota': 'Saturday',
            'neděle': 'Sunday'
        }
        df['day_of_week'] = df['day_of_week'].map(days_czech_to_english)

    if 'date' in df.columns:
        def determine_season(month):
            if month in [12, 1, 2]:
                return 'Winter'
            elif month in [3, 4, 5]:
                return 'Spring'
            elif month in [6, 7, 8]:
                return 'Summer'
            else:
                return 'Autumn'

        df['season'] = df['date'].dt.month.apply(determine_season)


    return df


def plot_weekday_vs_weekend(df):
    """Plots the number of accidents for weekdays vs. weekends."""
    plt.figure()
    weekday_weekend_counts = df['day_type'].value_counts()
    weekday_weekend_counts.plot(kind='bar')
    plt.title('Number of Accidents: Weekdays vs. Weekend', fontsize=12, pad=15)
    plt.xlabel('Type of Day', fontsize=12)
    plt.ylabel('Total Number of Accidents', fontsize=12)
    plt.xticks(rotation=0, fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.show()
    plt.close()


def plot_accidents_by_day(df):
    """Plots the number of accidents for each day of the week."""
    plt.figure()
    daily_accident_counts = df['day_of_week'].value_counts()
    days_order_english = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_accident_counts.reindex(days_order_english).plot(kind='bar')
    plt.title('Number of Accidents by Day of the Week', fontsize=16, pad=20)
    plt.xlabel('Day of the Week', fontsize=12)
    plt.ylabel('Total Number of Accidents', fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.show()
    plt.close()


def plot_accidents_by_season(df):
    """Plots the number of accidents for each season."""
    plt.figure()
    season_accident_counts = df['season'].value_counts()
    seasons_order = ['Spring', 'Summer', 'Autumn', 'Winter']
    season_accident_counts.reindex(seasons_order).plot(kind='bar')
    plt.title('Number of Accidents by Season', fontsize=16, pad=20)
    plt.xlabel('Season', fontsize=12)
    plt.ylabel('Total Number of Accidents', fontsize=12)
    plt.xticks(rotation=0, fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.show()
    plt.close()


def plot_hourly_trend(df):
    """Plots the trend of accidents throughout the day."""
    fig, ax = plt.subplots(figsize=(14, 8))
    accidents_by_hour = df.groupby(['day_type', 'hour']).size().unstack(level=0)
    accidents_by_hour.plot(kind='line', marker='o', linewidth=2.5, ax=ax)
    ax.set_title('Comparison of Accident Counts by Hour of the Day', fontsize=18, pad=20)
    ax.set_xlabel('Hour of the Day', fontsize=12)
    ax.set_ylabel('Number of Accidents', fontsize=12)
    ax.set_xticks(range(0, 24))
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend(title='Type of Day', fontsize='large')
    plt.tight_layout()
    plt.show()
    plt.close(fig)


def perform_t_test(df):
    """Performs an independent t-test and prints the results."""
    
    #Group accidents by dates 
    daily_counts = df.groupby(df['date'].dt.date).size()

    #split into two groups by index 
    index_datumov = pd.to_datetime(daily_counts.index)
    workdays = daily_counts[index_datumov.dayofweek < 5]
    weekdays = daily_counts[index_datumov.dayofweek >= 5]

    mean_workday = workdays.mean()
    mean_weekday = weekdays.mean()

    t_stat, p_value = stats.ttest_ind(workdays, weekdays, equal_var=False)

    print("Hypotéza: Líši sa priemerný denný počet nehôd medzi pracovnými dňami a víkendom?\n")
    print(f"Priemerný počet nehôd (pracovné dni): {mean_workday}")
    print(f"Priemerný počet nehôd (víkend): {mean_weekday:}\n")
    print(f"Vypočítaná t-štatistika: {t_stat:}")
    print(f"P-hodnota (p-value): {p_value}\n")

    significance_level = 0.05

    if p_value < significance_level:
        print(f"P-hodnota je menšia ako nami zvolená hladina významnosti α ({significance_level}).")
        print("Preto nulovú hypotézu (H₀) zamietame.")
        print("Záver: Rozdiel v priemernom počte nehôd je štatisticky významný.")
    else:
        print(f"P-hodnota je väčšia ako nami zvolená hladina významnosti α ({significance_level}).")
        print("Preto nulovú hypotézu (H₀) nezamietame.")
        print("Záver: Nepodarilo sa preukázať štatisticky významný rozdiel.")


def main():
    file_path = '../data/data.csv'
    file_data = load_data(file_path)
    if file_data is not None:
        df_prepared = prepare_data(file_data.copy())
        plot_weekday_vs_weekend(df_prepared)
        plot_accidents_by_day(df_prepared)
        plot_accidents_by_season(df_prepared)
        plot_hourly_trend(df_prepared)
        perform_t_test(df_prepared)


if __name__ == "__main__":
    main()