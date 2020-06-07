"""Extract links for competitions using JSON files. Script is idempotent."""

import json
import os
import re
import requests
import time

for file in os.listdir("./file"):
    file_path = os.path.join("./file", file)
    try:
        with open(file_path, 'r+', encoding="utf-8") as f:
            json_file = json.load(f)

            season = file.split('-')[-1].split('.')[0][:2]
            season = "20{}".format(season)

            for competition in json_file["competitions"]:
                # tier = 1  #competition["tier"]

                for comp in competition["links"]:
                    comp_dict = {
                        "germany_id": comp["id"],
                        "competition_name": comp["name"],
                        "state_name": comp["state_name"],
                        "area_name": comp["area_name"],
                        "season_id": season,
                        "tier_id": competition["tier"]
                    }

                    with open('database_insertions.sql', 'a+') as f:
                        insertion_string = "INSERT INTO germany_competitions (state_name, area_name, competition_name, germany_id, season_id, tier_id) VALUES(\"{}\", \"{}\", \"{}\", \"{}\", \"{}\", \"{}\");\n"
                        f.write(insertion_string.format(comp_dict['state_name'], comp_dict['area_name'], comp_dict['competition_name'], comp_dict['germany_id'], season, comp_dict['tier_id']))

    except Exception as e:
        print(file_path)