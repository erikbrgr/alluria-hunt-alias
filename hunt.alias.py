<drac2>  #hunt
pref = ctx.prefix
null = ''
nl = '\n'
al = ctx.alias
cmd = pref+al
curr_time = time()

unparsed_arg = &ARGS&
args = argparse(unparsed_arg)

using(
	calendar="74a21a79-bc4c-4b03-9b21-a16e2b591a89",
	hunt="bf305f5e-aada-44ec-9c0d-cd810e0031d7"
)

biomes_list = [
	'Arctic',
	'Coastal',
	'Swamp',
	'Desert',
	'Feywild',
	'Hill',
	'Forest',
	'Grassland',
	'Mountain',
	'Underdark',
	'Haunted',
	'Underwater',
	'Urban'
]
difficulty_list = ['easy', 'medium', 'hard', 'deadly']

eg_cmd = f'{cmd} `{biomes_list[0]}`'

inp = "&*&".lower().replace('"', '')
double_quote_escaped_inp = inp.replace('"', '\\\"')
inp1 = "&1&".lower().replace('"', '')
inp2 = "&2&".lower().replace('"', '')
inp1_title = "&1&".title().replace('"', '')

c = combat()

help_text = f'''
__**Usage**__:
- `{cmd} <location> [difficulty] -levels <comma-separated level values without space>`

__**Usage Examples**__:
- `{cmd} coastal`: Generates an encounter of random difficulty in a *Coastal* biome for all players currently in the combat initiative.
- `{cmd} coastal -levels 2,3,4`: Generates a random difficulty encounter in a *Coastal* biome for three players with levels 2, 3, and 4.
- `{cmd} coastal easy -levels 5,5,5,5`: Generates an *Easy* difficulty encounter in a *Coastal* biome for four players, all level 5.

:warning: **IMPORTANT**: No space between numbers and commas in the `-levels` option.

- `{cmd} auto off`: Disables the automatic addition of monsters to combat initiative and the reminder to use `{pref}auto`.
- `{cmd} end`: Claim your XP after the encounter ends and all monsters' HP is 0 or below. For a single player in the initiative, XP is automatically added to their character. For multiple players, XP distribution is displayed for manual addition.

__**Available Locations**__:
{nl.join(biomes_list)}

__**Available Difficulty Levels**__:
{nl.join(difficulty_list)}
'''


if inp in "help?":
	title = f'{name} needs help hunting!'
	desc = help_text
elif inp1 == 'auto':
	if inp2 == 'off':
		character().set_cvar('auto_hunt', 'off')
		title = f':negative_squared_cross_mark: Auto addition of monsters to combat has been disabled'
		desc = f'The reminder to use `{pref}auto` is also now hidden'
	elif inp2 == 'on':
		character().delete_cvar('auto_hunt')
		title = f':white_check_mark: Auto addition of monsters to combat has been enabled'
		desc = f'The reminder to use `{pref}auto` is also now visible'
	else:
		title = f'Invalid input'
		desc = f'''__Usage Example__:
		To **ENABLE** the auto addition of monsters to combat:
		`{cmd} auto on`

		To **DISABLE** the auto addition of monsters to combat:
		`{cmd} auto off`
		'''
	return (f"""embed -title "{title}" -desc "{desc}" -thumb {image} -color {color} -footer '!{al} help | made by @alpha983 edited by @PineappleShark'""")

elif inp1_title not in biomes_list and inp1 not in 'endcollect':
	title = f'Please check the location you\'ve entered!'
	desc = f'It must be one of the following:\n\n{nl.join(list(biomes_list))}\n\nFor eg:\n' + eg_cmd
elif inp1_title in biomes_list:
	monster_yaml1 = get_gvar("c9a5d4db-0fe4-4934-b417-405e92d5d88f")
	monster_yaml2 = get_gvar("7b2f041a-e187-4f4b-b484-c323afd3cf83")

	monster_data = load_yaml(monster_yaml1+monster_yaml2)

	player_levels_dict = {}
	is_daytime = calendar.is_daytime(curr_time)
	if c:
		combatants = c.combatants
		player_levels_dict = {player.name: player.levels.total_level for player in combatants if player.creature_type == None and player.monster_name == None}
        
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
			title = f'Please check the levels you have entered!'
			desc = f'''
__Input Entered__:
`{cmd} {double_quote_escaped_inp}`

__Example Usage__:
`{cmd} forest -levels 3,5,2`

The above represents one player of level 3, another player of level 5 and the final player being level 2 and so on...
'''
			return (f"""embed -title "{title}" -desc "{desc}" -thumb {image} -color {color} -footer '!{al} help | made by @alpha983 edited by @PineappleShark'""")


	level = sum(player_levels_dict.values())
	# Count the number of players above level 7
	players_above_level_7 = sum(1 for level in player_levels_dict.values() if level > 7)

	# Calculate the base max_monsters
	base_max_monsters = floor(len(player_levels_dict) * 1.5) if len(player_levels_dict) > 3 else 4

	# Adjust max_monsters based on players above level 7
	max_monsters = base_max_monsters + (3 * players_above_level_7)

	input_difficulty = inp2.title() if inp2 in difficulty_list else None
	difficulty_roll, chosen_difficulty, xp_value = hunt.determine_challenge(level, input_difficulty)

	suitable_monsters = hunt.find_monsters(monster_data, inp1_title, level, xp_value, is_daytime, max_monsters)
	if not suitable_monsters:
		title = f'No monsters found in this biome.'
		desc = f'Please try again later.'
		return (f"""embed -title "{title}" -desc "{desc}" -thumb {image} -color {color} -footer '!{al} help | made by @alpha983 edited by @PineappleShark'""")


	title, desc = hunt.format_encounter_details(suitable_monsters, inp1_title, difficulty_roll, chosen_difficulty, xp_value, player_levels_dict)

	# Step 1: Aggregate Monster Quantities
	monster_quantities = {}
	for monster in suitable_monsters:
		monst = monster[0]  # The name of the monster
		if monst in monster_quantities:
			monster_quantities[monst] += 1
		else:
			monster_quantities[monst] = 1

	# Step 2: Generate Commands
	monst_list = []
	for monst, qty in monster_quantities.items():
		if exists('auto_hunt'):
			madd_cmd = f'{pref}i madd ' + '\\\"' + f'{monst}' + '\\\"' + f' -n {qty}'
		else:
			madd_cmd = f'{pref}i madd ' + '\"' + f'{monst}' + '\"' + f' -n {qty}'
		monst_list.append(madd_cmd)
	combatants = list(c.combatants) if c else []

	if exists('auto_hunt'):
		cmd_box = f'{pref}multiline\n{pref}i begin\n{nl.join(monst_list)}'
		desc += f'''

		Copy paste the below to instantly add all monsters to combat:
		```{cmd_box}```
		'''
		return (f"""embed -title "{title}" -desc "{desc}" -thumb {image} -color {color} -footer '!{al} help | made by @alpha983 edited by @PineappleShark'""")
	else:

		l1 = f'embed -title "{title}" -desc "'+desc+f'" -thumb {image} -color {color} -footer "!{al} help | made by @alpha983 edited by @PineappleShark"'
		auto_helper_title = f"Recommended Action: Use `{pref}auto` for Monster AI"
		auto_helper_desc = f"""`{pref}auto`

	If you haven\'t enabled `{pref}auto` yet, click the below link to visit the workshop page:
	[🤖 Auto Monster AI](https://avrae.io/dashboard/workshop/617805d1137cd863517bc42c)
	(Please ignore if a Game Master is available to run combat)

	:warning: IMPORTANT: After defeating all monsters, use `{cmd} end` to automatically add the XP you've earned from the combat."""

		l4 = f'!embed -title "{auto_helper_title}" -desc "'+auto_helper_desc+f'" -color {color} -footer "!{al} help | made by @alpha983 edited by @PineappleShark"'
		if c:
			l2 = f'{pref}i join' if not c.me else ''
			l3 = ''
		else:
			l2 = f'{pref}i begin'
			l3 = f'{pref}i join'
		command_list = [l1, l2, l3] + monst_list + [l4]
		command = f"""multiline{nl}"""
		command += nl.join(command_list)
		return command
elif inp1_title in 'Endcollect':
	title, desc = hunt.conclude_combat(c)

return f"""embed -title "{title}" -desc "{desc}" -thumb {image} -color {color} -footer '!{al} help | made by @alpha983 edited by @PineappleShark'"""
</drac2>
