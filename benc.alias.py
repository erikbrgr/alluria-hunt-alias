embed
<drac2> # benc

color = "#CF142B"
footer = "made by @erikbrgr"

curr_time = time()
inp1_title = "Forest"
input_difficulty = "hard"

using(
    calendar="74a21a79-bc4c-4b03-9b21-a16e2b591a89",
    hunt="593dbe17-b0dc-4d32-9c65-9fb9f2c00098"
)

def main(unparsed_args) -> tuple(str, str, str, str, str):
    '''

    '''
    args = argparse(unparsed_args)

    player_levels_dict = {}
    if not player_levels_dict:
        player_levels_dict = {name: level}
        max_monsters = 4

    if args.last('levels'):
        player_levels_string = args.last('levels')
        if hunt.is_number_or_comma_separated_numbers(player_levels_string):
            player_levels_list = [int(x.strip()) for x in player_levels_string.strip("[]").split(",")]

            player_levels_dict = {}
            level_count = {}

            for level in player_levels_list:
                if level in level_count:
                    level_count[level] += 1
                    key = f"Player Level {level} ({level_count[level]})"
                else:
                    level_count[level] = 0
                    key = f"Player Level {level}"
                player_levels_dict[key] = level
        else:
            return "Invalid input", f"Input: {unparsed_arg}", color, "", footer

    # Count the number of players above level 7
    players_above_level_7 = sum(1 for level in player_levels_dict.values() if level > 7)

    # Calculate the base max_monsters
    base_max_monsters = floor(len(player_levels_dict) * 1.5) if len(player_levels_dict) > 3 else 4

    # Adjust max_monsters based on players above level 7
    max_monsters = base_max_monsters + (3 * players_above_level_7)

    difficulty_roll, chosen_difficulty, xp_value = hunt.determine_challenge(player_levels_dict, input_difficulty)

    is_daytime = calendar.is_daytime(curr_time)

    monster_yaml1 = get_gvar("c9a5d4db-0fe4-4934-b417-405e92d5d88f")
    monster_yaml2 = get_gvar("7b2f041a-e187-4f4b-b484-c323afd3cf83")
    monster_data = load_yaml(monster_yaml1+monster_yaml2)

    suitable_monsters = hunt.find_monsters(monster_data, inp1_title, xp_value, is_daytime, max_monsters)
    if not suitable_monsters:
        return "No suitable monsters found", "Please try again.", color, "", footer

    title, desc = hunt.format_encounter_details(suitable_monsters, inp1_title, difficulty_roll, chosen_difficulty, xp_value, player_levels_dict)

    return title, desc, color, "", footer

title, body, color, thumb, footer = main(&ARGS&)


</drac2>
-title "{{title}}"
-desc "{{body}}"
-color "{{color}}"
-thumb "{{thumb}}"
-footer "{{footer}}"
