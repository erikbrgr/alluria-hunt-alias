using(
    calendar="74a21a79-bc4c-4b03-9b21-a16e2b591a89",
    xplib="bd5e6af1-55e9-4c5b-b814-8f9b447091e7",
    logtools="11743454-0aca-46a6-ad73-9b902a65fbeb"
)

char = character()
name = char.name
nl = '\n'
pref = ctx.prefix
al = ctx.alias
cmd = pref + al


# Find suitable monsters for the hunt
def chunk_monsters_by_xp(monsters, data):
    chunks = {}
    for monster in monsters:
        xp = monster[data['header'].index('XP')]
        if xp not in chunks:
            chunks[xp] = []
        chunks[xp].append(monster)
    return chunks


def find_monsters(data, biome, max_xp, is_daytime, max_monsters):
    monsters_in_biome = [
        monster for monster in data['data']
        if (biome in monster[data['header'].index('Biome1')] or biome in monster[data['header'].index('Biome2')]) and
           ((is_daytime and monster[data['header'].index('Daytime')]) or (
                       not is_daytime and monster[data['header'].index('Nighttime')])) and
           monster[data['header'].index('XP')] <= max_xp
    ]

    if not monsters_in_biome:
        return []

    chunks = chunk_monsters_by_xp(monsters_in_biome, data)

    suitable_monsters = []
    total_xp = 0

    # Manually sorting the XP keys in descending order
    xp_values = list(chunks.keys())
    for i in range(len(xp_values)):
        for j in range(i + 1, len(xp_values)):
            if xp_values[i] < xp_values[j]:
                xp_values[i], xp_values[j] = xp_values[j], xp_values[i]

    for xp in xp_values:
        while chunks[xp] and total_xp + xp <= max_xp and len(suitable_monsters) < max_monsters:
            selected_monster = randchoice(chunks[xp])
            suitable_monsters.append(selected_monster)
            total_xp += selected_monster[data['header'].index('XP')]
            chunks[xp].remove(selected_monster)  # Remove the selected monster from the chunk

            if total_xp >= max_xp or len(suitable_monsters) >= max_monsters:
                return suitable_monsters

    return suitable_monsters


def get_emoji_representation(quantity, whole_emoji, half_emoji):
    # Calculate the whole and fractional part of the quantity
    whole_part = int(quantity)
    fractional_part = quantity - whole_part

    # Build the emoji string for the whole part
    emoji_str = whole_emoji * whole_part

    # Add the half emoji if the fractional part is close to 0.5
    if 0.25 <= fractional_part < 0.75:
        emoji_str += half_emoji
    # If the fractional part is equal to or greater than 0.75, add a whole emoji
    elif fractional_part >= 0.75:
        emoji_str += whole_emoji
    return emoji_str


def set_loot_cvar(xp, biome, player_levels_dict):
    # Prepare the data to store
    loot_data = {
        "xp": xp,
        "biome": biome,
        "player_levels_dict": player_levels_dict
    }

    # Convert the data to a JSON string
    loot_json = dump_json(loot_data)

    # Set the cvar with the loot data
    char.set_cvar("loot", loot_json)


def load_monster_behaviour():
    monster_behaviour = load_yaml(get_gvar("2343af56-953c-45f5-ad8e-f7c7eee96280"))
    return monster_behaviour


# Function to determine the time period based on the hour
def get_time_period(hour):
    if 6 <= hour < 11:
        return "6am - 11am Morning"
    elif 11 <= hour < 16:
        return "11am - 4pm Midday"
    elif 16 <= hour < 22:
        return "4pm - 10pm Evening"
    elif 22 <= hour or hour < 6:
        return "10pm - 6am Nighttime"


# Function to parse the behavior based on biome, time period, and creature type
def get_behavior(yaml_data, biome, time_period, creature_type):
    # Get the behavior
    behaviors = yaml_data[biome][time_period][creature_type]

    # Check if behaviors is not a string, indicating it's probably missing or null
    if typeof(behaviors) != "str" or not behaviors:
        return "No specific behavior observed"  # default message for empty or null behavior

    # If behaviors is a non-empty string, we split it by the unique separator and choose a random one
    behavior_list = behaviors.split(", ")
    behavior = randchoice(behavior_list).replace('"', '')

    return behavior


def format_encounter_details(suitable_monsters, biome, difficulty_roll, chosen_difficulty, xp_value,
                             player_levels_dict):
    if not suitable_monsters:
        title = "No suitable monsters found for the encounter."
        return title, ""

    # Map biomes to emojis
    biome_emojis = {
        'Arctic': '❄️',
        'Coastal': '🌊',
        'Swamp': '🐍',
        'Desert': '🏜️',
        'Feywild': '🧚',
        'Hill': '🌄',
        'Forest': '🌲',
        'Grassland': '🌾',
        'Mountain': '⛰️',
        'Underdark': '🕳️',
        'Haunted': '👻',
        'Underwater': '🐟',
        'Urban': '🏙️'
    }

    biome_emoji = biome_emojis.get(biome, '🏞️')  # Default emoji for unknown/other biomes

    # Encounter title with an emoji for flair
    title = f'{biome_emoji} {name} goes hunting in The {biome}! {biome_emoji}'

    # Initialize dictionaries for counting
    monster_counts = {}
    total_monster_xp = 0

    # Initialize total counts
    # total_materials = 0
    # total_magical_materials = 0

    # Get the current time
    current_hour = calendar.hours  # Using the user-provided 'calendar' object for the current hour
    time_period = get_time_period(current_hour)

    # Building the monster details section and aggregating information
    for monster in suitable_monsters:
        creature, cr, xp, creature_type, biome1, biome2, size, appears_day, appears_night = monster
        total_monster_xp += (xp / 5)
        active_time_emoji = ":partly_sunny:/:crescent_moon: " if appears_day and appears_night else (
            ":partly_sunny:" if appears_day else ":crescent_moon: ")

        # Get the behavior from the YAML data based on the current time period
        yaml_data = load_monster_behaviour()
        behavior = get_behavior(yaml_data, biome, time_period, creature_type)

        # Aggregate monster counts
        if creature in monster_counts:
            monster_counts[creature]['count'] += 1
            monster_counts[creature]['total_xp'] += xp
        else:
            monster_counts[creature] = {
                'count': 1,
                'cr': cr,
                'total_xp': xp,
                'xp': xp,
                'active_time_emoji': active_time_emoji,
                'behavior': behavior,
                # 'materials_count': materials,  # store the per-monster materials
                # 'magical_materials_count': magical_materials  # store the per-monster magical materials
            }

    # Construct the monster details output
    monster_details = ""

    for creature, info in monster_counts.items():
        count = info['count']
        # materials_for_this_type = info['materials_count'] * count
        # magical_materials_for_this_type = info['magical_materials_count'] * count

        # materials_emoji = ':hammer_pick:' * materials_for_this_type
        # magical_materials_emoji = get_emoji_representation(magical_materials_for_this_type, ':star2:', ':star:')

        # Calculate the individual and total XP
        individual_xp = ((info['xp']) / 5)  # assuming 'xp' is the XP for one creature
        total_xp_for_this_creature = individual_xp * count

        # Construct strings for materials and magical materials
        # materials_str = f"{materials_for_this_type} Material" if materials_for_this_type == 1 else f"{materials_for_this_type} Materials"
        # magical_materials_str = f"{magical_materials_for_this_type} Magical Material" if magical_materials_for_this_type == 1 else f"{magical_materials_for_this_type} Magical Materials"

        # Prepare the monster details string
        monster_info = f"""**{creature} (CR{info['cr']}** x{count} ({individual_xp}XP each = {total_xp_for_this_creature}XP total)
* *{info['behavior']}*
"""

        monster_details += monster_info
        # Calculate total materials and magical materials
        # total_materials += materials_for_this_type
        # total_magical_materials += magical_materials_for_this_type

    # Store this information in the character's cvar
    set_loot_cvar(total_monster_xp, biome, player_levels_dict)

    # Difficulty and XP details
    difficulty_details = f"No. of Players: {len(player_levels_dict)}\n{difficulty_roll} - Challenge: {chosen_difficulty} (XP: {xp_value})\n" \
                         f"Encounter XP: {total_monster_xp}/{xp_value}"

    # Constructing the final message, escaping double quotes
    encounter_details = f"""__Current Conditions__: {calendar.timeOfDay}

__Encounter__:
{monster_details}
__Rewards__:
:trophy: {total_monster_xp} XP

__Challenge__:
{difficulty_details}
"""
    encounter_details = encounter_details.replace('"', '\\"')

    return title, encounter_details


def conclude_combat(combat):
    # Check if all non-player combatants are dead
    all_monsters_dead = True
    for combatant in combat.combatants:
        if combatant.type == "combatant" and combatant.hp > 0 and combatant.creature_type is not None and combatant.monster_name is not None:
            all_monsters_dead = False
            break  # If any monster is still alive, we exit the check

    if all_monsters_dead:
        # Retrieve the loot data from the cvar
        loot_json = char.get_cvar("loot")
        if loot_json:
            loot_data = load_json(loot_json)
            # materials = loot_data.get("materials", 0)
            # magical_materials = loot_data.get("magical_materials", 0)
            xp_gained = loot_data.get("xp", 0)
            biome = loot_data.get("biome", 'Wild')
            player_levels_dict = loot_data.get("player_levels_dict")
            if len(player_levels_dict) > 1:
                char.delete_cvar("loot")

                # Calculate the total level of all players
                total_level = sum(player_levels_dict.values())

                # Initialize a string to display XP distribution
                xp_distribution_str = ":trophy: XP Distribution:\n"

                # Calculate and append the proportional XP for each player to the string
                for player_name, player_level in player_levels_dict.items():
                    player_share = (player_level / total_level) * xp_gained if total_level else 0
                    xp_distribution_str += f"- {player_name}: {int(player_share)} XP\n"

                title = f'{char.name} concludes the combat!'
                summary = f"\n{xp_distribution_str}"
            else:

                # Log the XP gain
                xplib.modify_xp(xp_gained, f'+{xp_gained}XP gained from `{cmd}`-ing in The {biome}.')
                # Clear the loot cvar after claiming the loot
                char.delete_cvar("loot")

                # Provide a summary of the loot claimed
                title = f'{char.name} claims their rewards!'
                rewards_list = [
                    f":trophy: {xp_gained} XP" if xp_gained else None
                ]
                summary = "__Rewards claimed__:\n" + "\n".join([reward for reward in rewards_list if reward]) + f"""

**Recommended Aliases:**
- New XP: `{pref}xp` ([Workshop Link](https://avrae.io/dashboard/workshop/618b77bd5c51fd18fe5356a0))


**Additional Commands:**
- `{pref}xp log` (View all XP earned from `{cmd}`)

"""
#- Loot/Skin/Harvest (2000+ Monsters): `{pref}skin` ([Workshop Link](https://avrae.io/dashboard/workshop/6207758610bae65359791268))
#- `{pref}skin` (Use after battles)

        else:
            title = f'{name} tries to claim their rewards!'
            summary = f"No rewards to claim. {name} did not add their own discovered monsters to the encounter or has already claimed their rewards."
    else:
        title = f"Not all monsters are defeated!"
        summary = f"Please claim rewards after defeating all monsters."
    return title, summary


# def add_materials_to_cc(materials, magical_materials):
#     # Add materials to character's material counter
#     materials_cc_name = 'Materials'
#     char.create_cc_nx(name=materials_cc_name, minVal=0, title=materials_cc_name)
#     materials_curr_value = char.cc(materials_cc_name).value
#     materials_new_value = materials_curr_value + materials
#     char.cc(materials_cc_name).set(materials_new_value)
#
#     # Add magical materials to character's magical material counter
#     mag_materials_cc_name = 'Magical Materials'
#     char.create_cc_nx(name=mag_materials_cc_name, minVal=0, title=mag_materials_cc_name)
#     mag_materials_curr_value = char.cc(mag_materials_cc_name).value
#     mag_materials_new_value = mag_materials_curr_value + magical_materials
#     char.cc(mag_materials_cc_name).set(mag_materials_new_value)


def determine_challenge(player_levels_dict, input_difficulty=None):
    difficulty_levels = {
        1: {"Easy": 25, "Medium": 50, "Hard": 75, "Deadly": 100},
        2: {"Easy": 50, "Medium": 100, "Hard": 150, "Deadly": 200},
        3: {"Easy": 75, "Medium": 150, "Hard": 225, "Deadly": 400},
        4: {"Easy": 125, "Medium": 250, "Hard": 375, "Deadly": 500},
        5: {"Easy": 250, "Medium": 500, "Hard": 750, "Deadly": 1100},
        6: {"Easy": 300, "Medium": 600, "Hard": 900, "Deadly": 1400},
        7: {"Easy": 350, "Medium": 750, "Hard": 1100, "Deadly": 1700},
        8: {"Easy": 450, "Medium": 900, "Hard": 1400, "Deadly": 2100},
        9: {"Easy": 550, "Medium": 1100, "Hard": 1600, "Deadly": 2400},
        10: {"Easy": 600, "Medium": 1200, "Hard": 1900, "Deadly": 2800},
        11: {"Easy": 800, "Medium": 1600, "Hard": 2400, "Deadly": 3600},
        12: {"Easy": 1000, "Medium": 2000, "Hard": 3000, "Deadly": 4500},
        13: {"Easy": 1100, "Medium": 2200, "Hard": 3400, "Deadly": 5100},
        14: {"Easy": 1250, "Medium": 2500, "Hard": 3800, "Deadly": 5700},
        15: {"Easy": 1400, "Medium": 2800, "Hard": 4300, "Deadly": 6400},
        16: {"Easy": 1600, "Medium": 3200, "Hard": 4800, "Deadly": 7200},
        17: {"Easy": 2000, "Medium": 3900, "Hard": 5900, "Deadly": 8800},
        18: {"Easy": 2100, "Medium": 4200, "Hard": 6300, "Deadly": 9500},
        19: {"Easy": 2400, "Medium": 4900, "Hard": 7300, "Deadly": 10900},
        20: {"Easy": 2800, "Medium": 5700, "Hard": 8500, "Deadly": 12700}
    }

    player_level = sum(player_levels_dict.values())

    if player_level > 20:
        base_value = 500 * (player_level - 20)  # Base calculation formula for difficulty levels
        difficulty_levels[player_level] = {
            "Easy": (2800 + base_value),
            "Medium": (5700 + base_value * 2),
            "Hard": (8500 + base_value * 3),
            "Deadly": (12700 + base_value * 4.5)
        }

    # Map roll to difficulty
    difficulty_list = ['Easy', 'Medium', 'Hard', 'Deadly']

    # Check if a difficulty is provided
    if input_difficulty and input_difficulty.capitalize() in difficulty_list:
        chosen_difficulty = input_difficulty.capitalize()
        difficulty_roll = f"Chosen by player: {chosen_difficulty}"
    else:
        # Simulate a d4 roll for random difficulty
        difficulty_roll = vroll("d4")
        chosen_difficulty = difficulty_list[difficulty_roll.total - 1]

    # Retrieve the XP value from the difficulty levels dictionary
    xp_value = int(difficulty_levels[player_level][chosen_difficulty])

    return difficulty_roll, chosen_difficulty, xp_value


def is_number_or_comma_separated_numbers(s):
    # Split the string by commas
    elements = s.split(',')

    # Check each element
    for element in elements:
        element = element.strip()  # Remove any leading/trailing whitespace
        if not element.isdigit():  # Check if the element is a number
            return False

    return True
