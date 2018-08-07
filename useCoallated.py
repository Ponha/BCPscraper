import datetime
import dateparser
import json
from bokeh.plotting import figure, output_file, show
from collections import Counter
from math import pi
import pandas as pd
from bokeh.io import output_file, show
from bokeh.palettes import Category20c
from bokeh.plotting import figure, ColumnDataSource
from bokeh.transform import cumsum

from collections import defaultdict


def filter_events(events, from_date=datetime.date(1, 1, 1), to_date=datetime.date(9000, 1, 1), min_rounds=0, max_rounds=100):
    if (from_date == datetime.date(1, 1, 1)
            and to_date == datetime.date(9000, 1, 1)
            and min_rounds == 0
            and max_rounds == 100):
        return events
    else:
        return [x for x in events
                if from_date < dateparser.parse(x["date"]).date() < to_date
                and min_rounds <= x["rounds"] <= max_rounds
                ]


def itc_faction(data, fact_key):
    # print(factKey)
    data = data.strip()
    for k, v in fact_key.items():
        if data in v:
            # print("hit")
            return k
    # print("miss")
    print("Unknown faction: " + data)
    return data


def number_of_games_per_faction(events):
    fact_key = {};
    with open("factKey.json", "r") as f:
        fact_key = json.load(f)
    faction_games = {}
    for event in events:
        for player in event["results"]:
            nr_of_games = len(player["wins"]) + len(player["draws"]) + len(player["losses"])
            itc_fact = itc_faction(player["faction"], fact_key)
            if itc_fact != "Unknown":
                try:
                    faction_games[itc_fact] += nr_of_games
                except:
                    faction_games[itc_fact] = nr_of_games
    return faction_games


def win_ratio_per_faction(events):
    fact_key = {}
    with open("factKey.json", "r") as f:
        fact_key = json.load(f)
    faction_winrate = {}
    for event in events:
        for player in event["results"]:
            wins = len(player["wins"])
            losses = len(player["losses"])
            itc_fact = itc_faction(player["faction"], fact_key)
            if itc_fact != "Unknown":
                if itc_fact in faction_winrate.keys():
                    faction_winrate[itc_fact][0] += wins
                    faction_winrate[itc_fact][1] += losses
                else:
                    faction_winrate[itc_fact] = [wins, losses]
    by_percent={}
    for k, v in faction_winrate.items():
        by_percent[k] = 100 * (v[0]/(v[0]+v[1]))
    return by_percent


def representation_per_faction(games_per_faction):
    total_games = 0
    percent_representation = {}
    for k, v in games_per_faction.items():
        total_games += v
    for k, v in games_per_faction.items():
        percent_representation[k] = 100 * (v/total_games)
    return percent_representation

def order_data_into_months(events):
    #print(events[0]["date"])
    #current_date = dateparser.parse(events[0]["date"]).date()
    #current_month = current_date.replace(day=1)
    events_by_month = {}
    cntr = 0
    for event in events:
        event_date = dateparser.parse(event["date"]).date()
        event_month = str(event_date.replace(day=1))
        if event_month in events_by_month.keys():
            events_by_month[event_month].append(event)
        else:
            events_by_month[event_month] = []
            events_by_month[event_month].append(event)
            cntr+=1

    return events_by_month
    #print("Months: " + str(cntr))
    #return json.dumps(events_by_month, indent=4, sort_keys=True, default=str)


def representation_per_faction_per_month(games_per_faction_per_month):
    rates_by_month = {}
    for month in sorted(games_per_faction_per_month.keys()):
        rates_by_month[month] = representation_per_faction(games_per_faction_per_month[month])
    #print(json.dumps(rates_by_month, indent=4, default=str, sort_keys=True))
    return rates_by_month


def games_played_per_faction_per_month(events_by_month):
    games_by_month = {}
    for month in sorted(events_by_month.keys()):
        games_by_month[month] = number_of_games_per_faction(events_by_months[month])
    # print(json.dumps(games_by_month, indent=4, default=str, sort_keys=True))
    return games_by_month


def win_ratio_per_faction_per_month(events_by_month):
    ratios_by_month = {}
    for month in sorted(events_by_month.keys()):
        ratios_by_month[month] = win_ratio_per_faction(events_by_months[month])
    # print(json.dumps(ratios_by_month, indent=4, default=str, sort_keys=True))
    return ratios_by_month


def print_bar_graph(data_, filename="outputBar.html", title_="default", y_lable="", top=40):
    output_file(filename)
    data_sorted = sorted(data_.items(), key=lambda x:x[1], reverse=True)
    keys = []
    values = []
    for item in data_sorted:
        keys.append(item[0])
        values.append(item[1])

    sauce = ColumnDataSource(data=dict(
        x=keys,
        y=values,
    ))

    p = figure(x_range=keys, plot_height = 520, plot_width = 1000, title=title_,
               toolbar_location="right", tools="", tooltips="@x : @y")

    p.vbar(x='x', top='y', width=0.9, source=sauce)

    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    p.x_range.range_padding = 0.02
    p.xaxis.major_label_orientation = 1
    if y_lable != "":
        p.yaxis.axis_label = y_lable

    show(p)


def print_line_chart(data_, filename="outputLine.html", title_="default", y_lable="", top=40):
    output_file(filename)

    dc = {}
    keys = sorted(data_.keys())
    for x in keys:
        for k, v in data_[x].items():
            if k in dc.keys():
                dc[k][0].append(dateparser.parse(x).date())  # x) #
                dc[k][1].append(v)
            else:
                dc[k] = [[dateparser.parse(x).date()],[v]]  #[ [x],[v]]#
    #print(json.dumps(dc, indent=4, default=str))

    p = figure(plot_width=1200, plot_height=800, x_axis_type="datetime",
               title=title_)  # , tooltips=list(dc.keys()))

    for i, k in enumerate(dc.keys()):
        dc[k].append(Category20c[20][i%20])

    for k, v in dc.items():
        p.line(v[0], v[1], legend=k, line_color=v[2])

    p.legend.click_policy="hide"
    if y_lable != "":
        p.yaxis.axis_label = y_lable

    show(p)

def print_pie_chart(data_, filename="outputPie.html", title_="default", top=19):
    for k, v in data_.items():
        data_[k] = round(v, 1)

    output_file(filename)
    data_sorted = sorted(data_.items(), key=lambda x:x[1], reverse=True)

    if len(data_) > top+1 :
        misc = 0
        while len(data_sorted) > top:
            misc += float(data_sorted.pop()[1])
        data_sorted.append(("misc", round(misc,1)))
        print(" cut len down to: " + str(len(data_)))
    print (data_sorted)
    data_ = Counter(data_sorted)

    data = pd.DataFrame.from_dict(dict(data_), orient='index').reset_index().rename(index=str, columns={0:'value', 'index':'country'})
    data['angle'] = data['value']/sum(data_.values()) * 2*pi
    data['color'] = Category20c[len(data_)]

    p = figure(plot_height=520, plot_width = 1000, title=title_, toolbar_location="left",
               tools="hover", tooltips="@country: @value")

    p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend='country', source=data)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None

    show(p)

if __name__ == "__main__":
    print ("run useCoallated as __main__")
    events = []
    with open("eventsCoallated.json", "r") as f:
        events = json.load(f)

    """
    =============================================
    Below are functions for printing clear text statistics to the terminal
    =============================================
    """
    """
    games_played_faction = sorted(number_of_games_per_faction(events).items(), key=lambda x:x[1], reverse=True)
    total_wins_faction = sorted(win_ratio_per_faction(events).items(), key=lambda x:x[1], reverse=True)
    percent_representation = sorted(representation_per_faction(games_played_faction).items(), key=lambda x:x[1], reverse=True)

    print("\n Games played in total for factions: \n ==============================")
    for k, v in games_played_faction:
        print(k + ": " + str(v))
    print("\n Win ratio for factions: \n ==============================")        
    for k, v in total_wins_faction:
        print(k + ": " + str(round(v,1)))
    print("\n Representation for factions (percent): \n ============================")
    for k, v in percent_representation:
        print(k + ": " + str(round(v,1)))
    """

    """
    =============================================
    Below are functions for printing line graphs to files
    =============================================
    """

    events_by_months = order_data_into_months(events)
    wrpfpm = win_ratio_per_faction_per_month(events_by_months)
    gppfpm = games_played_per_faction_per_month(events_by_months)
    rpfpm = representation_per_faction_per_month(gppfpm)

    #print_line_chart(wrpfpm, title_= "Winratio for factions each month (click legend to hide lines)", y_lable="Percent", filename="LineGraphWinRatioOverTime.html")
    #print_line_chart(rpfpm, title_= "Representation for factions each month (click legend to hide lines)", y_lable="Percent", filename="LineGrapRepresentationOverTime.html")

    """
    =============================================
    Below are functions for printing bar graphs to files
    =============================================
    """
    currentMonth = datetime.date.today().month
    print(currentMonth)
    games_played_faction = number_of_games_per_faction(events)
    percent_representation = representation_per_faction(games_played_faction)
    total_wins_faction = win_ratio_per_faction(events)


    #print_bar_graph(total_wins_faction, y_lable = "Percent", title_= "Winrate of each faction 12 months", filename="BarGraphWinrate12Months.html")
    #print_bar_graph(percent_representation, y_lable = "Percent", title_= "Representation of each faction 12 months", filename="BarGraphRepresentation12Months.html")
  
    events = filter_events(events, datetime.date(2018, currentMonth-6, 1))
    games_played_faction = number_of_games_per_faction(events)
    percent_representation = representation_per_faction(games_played_faction)
    total_wins_faction = win_ratio_per_faction(events)
    #print_bar_graph(total_wins_faction, y_lable = "Percent", title_= "Winrate of each faction 6 months", filename="BarGraphWinrate6Months.html")
    #print_bar_graph(percent_representation, y_lable = "Percent", title_= "Representation of each faction 6 months", filename="BarGraphRepresentation6Months.html")

    events = filter_events(events, datetime.date(2018, currentMonth-3, 1))
    games_played_faction = number_of_games_per_faction(events)
    percent_representation = representation_per_faction(games_played_faction)
    total_wins_faction = win_ratio_per_faction(events)
    #print_bar_graph(total_wins_faction, y_lable = "Percent", title_= "Winrate of each faction 3 months", filename="BarGraphWinrate3Months.html")
    #print_bar_graph(percent_representation, y_lable = "Percent", title_= "Representation of each faction 3 months", filename="BarGraphRepresentation3Months.html")

    events = filter_events(events, datetime.date(2018, currentMonth-1, 1))
    games_played_faction = number_of_games_per_faction(events)
    percent_representation = representation_per_faction(games_played_faction)
    total_wins_faction = win_ratio_per_faction(events)
    #print_bar_graph(total_wins_faction, y_lable = "Percent", title_= "Winrate of each faction 1 month", filename="BarGraphWinrate1Month.html")
    print_bar_graph(percent_representation, y_lable = "Percent", title_= "Representation of each faction 1 month", filename="BarGraphRepresentation1Month.html")
