#include <sourcemod>
public Plugin:myinfo =
{
	name = "dsp_volume tracker",
	author = "darkid",
	description = "Prints to chat every time dsp_volume is changed.",
	version = "1.3",
	url = "http://www.steamcommunity.com/id/jbzdarkid"
}

public OnPluginStart() {
	CreateTimer(0.1, ConvarWatcher, _, TIMER_REPEAT);
}

public Action:ConvarWatcher(Handle:timer) {
	new Handle:g_dsp_volume = FindConVar("dsp_volume");
	decl String:dsp_volume[16];
	decl String:last_dsp_volume[16];
	GetConVarString(g_dsp_volume, dsp_volume, sizeof(dsp_volume))
	
	if (strcmp(dsp_volume, last_dsp_volume) != 0) {
		decl String:output[128] = "dsp_volume changed from ";
		StrCat(output, sizeof(output), last_dsp_volume);
		StrCat(output, sizeof(output), " to ");
		StrCat(output, sizeof(output), dsp_volume);
		PrintToChat(1, output);
	}
	strcopy(last_dsp_volume, sizeof(last_dsp_volume), dsp_volume)
	return Plugin_Continue;
}