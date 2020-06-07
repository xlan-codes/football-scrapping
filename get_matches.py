import requests
from bs4 import BeautifulSoup
import mysql.connector
import re
import json



#marrja e emrit te skuadres
def get_team(url):
    res = requests.get(url)
    team_page = BeautifulSoup(res.text, 'html.parser')
    team_div = team_page.find(class_='stage-profile-content container')
    team_name = team_div.h2.text
    return team_name

# skuadrat
def add_team(id, name):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="eni"
    )
    mycursor = mydb.cursor()
    sql = "INSERT INTO germany_teams (`germany_id`, `name`) VALUES (%s, %s)"
    val = (id, name)
    mycursor.execute(sql, val)
    mydb.commit()

#marrim emerin e nje lojtari te bazuar ne skuader
def get_players_by_team(link):
    res = requests.get(link)
    player_page = BeautifulSoup(res.text, 'html.parser')
    player = player_page.find(class_='profile-name')
    player_name = player.text
    return player_name

def analyze_game(url):
    res = requests.get(url)
    game_page = BeautifulSoup(res.text, 'html.parser')
    # analyze_game_substitutes(game_page) # analizo nderrimet
    # analyze_game_goals(game_page) # analizo golat
    # return

    # pitches region
    stage_header_div = game_page.find(class_='stage-header')
    pitches = stage_header_div.find(class_='location')
    pitches_name = re.sub(r"[\n\t]*", '', pitches.text)
    pitches_url = pitches['href']
    print(pitches_name + '\n' + pitches_url)
    add_pitches(pitches_name, pitches_url)
    # end pitches region

    # game region
    datetime_recieve = game_page.find(class_='input-subject')['value'][-16:]
    temp_date_time = datetime_recieve.split(' ')
    date = temp_date_time[0].split('.')

    #data kur eshte luajtur loja
    datetime_object = date[2] + '-' + date[1] + '-' + date[0] + ' ' + temp_date_time[1]+':00'

    #analizo scriptin dhe merr informacionet per lojen
    t = game_page.find_all(text=re.compile("CDATA"))[5]
    t1 = re.sub(r"[\n\t]*", '', t)
    test = t1.replace(' ', '')
    test1 = test.replace("/*<![CDATA[*/", '')
    test2 = test1.replace("/*]]>*/", '')
    test3 = test2.replace("if(window.location.href.indexOf('#_=_')>0){window.location=window.location.href.replace(/#.*/,'');}", '')
    test4 = test3.replace(";", ',')
    test5 = test4.split(',')
    test5 = test5[:-1]
    dictonary = dict()
    for s in test5:
        d = s.split('=')
        dictonary[d[0]] = d[1].replace('\'','');

    game_id = url.split('/')[-1]
    home_team = dictonary.get('edHeimmannschaftId')
    away_team = dictonary.get('edGastmannschaftId')
    game_date = datetime_object
    pitches_id = ''
    competition_id = dictonary.get('edSpielklasseId')
    finished = 1  # if game has finished or not
    print(competition_id)


def analyze_game_goals(game):
    # goals_html = game.findAll(True, {"class":'hexagon', 'class':'green'})

    goals_html = game.find(id='rangescontainer')
    events = goals_html['data-match-events']
    events = events.replace('\'', '"')
    data = json.loads(events);
    game_id = ''
    home_team_id = ''
    away_team_id = ''
    for event in data['first-half']['events']:
        if event['type'] == 'goal':
            if event['team'] == 'home':
                player_id = get_goals_player(game, event['time'])
                # print(event['time'])
            elif event['team'] == 'away':
                print('')

            #insert result to table

    print(data)


def analyze_game_substitutes(game):
    goals_html = game.find(id='rangescontainer')
    if len(goals_html) > 0:
        events = goals_html['data-match-events']
        events = events.replace('\'', '"')
        data = json.loads(events);
        game_id = ''
        home_team_id = ''
        away_team_id = ''
        for event in data['first-half']['events']:
            if event['type'] == 'substitute':
                if event['team'] == 'home':
                    get_players(game, event['time'])
                    # print(event['time'])
                elif event['team'] == 'away':
                    print('')

#get player
def get_players(game, minute):
    events = game.find_all(class_='events')
    for ev in events:
        rows = ev.find_all(class_='row-event')
        for row in rows:
            time = row.find(class_='column-time').text.replace('’', '')
            if int(time) == int(minute):
                players = row.find(class_='column-player')
                player_in = players.find('a')['href'].split('/')[-1]
                player_out = players.find(class_='substitute').find(class_='substitute').find("a")['href'].split('/')[-1]
                return [player_in, player_out]

    return [None, None]

def get_goals_player(game, minute):
    # half = game.find(class_='first-half')
    events = game.find_all(class_='events')
    for ev in events:
        rows = ev.find_all(class_='row-event')
        for row in rows:
            time = row.find(class_='column-time').text.replace('’', '')
            if int(time) == int(minute):
                player = row.find(class_='column-player')
                player_id = player.find('a')['href'].split('/')[-1]
                return player_id

    return None


def add_pitches(pitche_name, pitch_link):
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="eni"
    )
    mycursor = mydb.cursor()
    stadium_type_german = pitche_name.split(',')[0]
    # stadium_type = None
    if stadium_type_german == 'Kunstrasenplatz':
        stadium_type = 'artificial'
    elif stadium_type_german == 'Rasenplatz':
        stadium_type = 'natural'
    else:
        stadium_type = None

    sql = "INSERT INTO germany_pitches ( `name`, `google_maps_link`, `type`) VALUES (%s, %s, %s)"
    val = (pitche_name, pitch_link, stadium_type)
    mycursor.execute(sql, val)
    mydb.commit()


def main():
    response = requests.get("http://www.fussball.de/spieltagsuebersicht/bfv-verbandsliga-baden-verbandsliga-herren-saison1819-baden/-/staffel/023QQDQ23O00000JVS54898EVV9PO6D7-G#!/section/matches")
    soup = BeautifulSoup(response.text, 'html.parser')

    matches_table = soup.find(class_='table table-striped table-full-width thead')
    matches_table_body = matches_table.find('tbody')
    matches_table_rows = matches_table_body.find_all('tr')
    for row in matches_table_rows:
        td = row.find_all(class_='column-club')
        colum_detail = row.find(class_='column-detail')

        if len(td) > 0:
            tda1 = td[0].find(class_='club-wrapper')['href'] # skuadra e c cila luan ne fushen e vete
            tda2 = td[1].find(class_='club-wrapper')['href'] #skuandara kundershtare
            tda1_id = tda1.split('/')[-1]
            tda2_id = tda2.split('/')[-1]
            add_team(tda1_id, get_team(tda1))
            add_team(tda2_id, get_team(tda2))
            # print()
            # print(get_team(tda2))

        if colum_detail is not None:
            analyze_game(colum_detail.a['href']) #analizo lojen
    # print(matches_table_row)

if __name__ == '__main__':
    main()
