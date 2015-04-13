#include <sourcemod>
public Plugin:Info =
{
	name = "No Sniper to Mid",
	description = "Prevents players from playing sniper until the middle control point is captured at the beginning of the round.",
	author = "darkid",
	version = "1.1",
	url = "www.sourcemod.net"
};
new numSnipers = 1; // Normal number of snipers
new bool:midCapped = false;
new bool:newGame = true;
// All listed functions happen approximately in order.
public OnPluginStart() {
	HookEvent("teamplay_point_captured", Event_CappedPoint);
	HookEvent("teamplay_round_start", Event_RoundStart);
	HookEvent("tf_game_over", Event_GameOver);
}
// When we start the map, we're in pre-game. Anyone can snipe during this time.
public OnMapStart() {
	midCapped = false;
	newGame = true; // This makes sure that the start of round is not confused.
}
// Once the round starts, if it is a new game, it's handled by the above.
// Otherwise, dis-allow snipers.
public Event_RoundStart(Handle:event, const String:name[], bool:dontBroadcast) {
	if (newGame) {
		SetConVarInt(FindConVar("tf_tournament_classlimit_sniper"), numSnipers);
		newGame = false;
	} else { // A normal round loaded.
		SetConVarInt(FindConVar("tf_tournament_classlimit_sniper"), 0);
	}
	midCapped = false;
}
// If a point is capped, and it's the first point of the round, it's mid. Allow snipers afterwords.
public Event_CappedPoint(Handle:event, const String:name[], bool:dontBroadcast) {
	if (midCapped == true) {
		return;
	}
	midCapped = true;
	SetConVarInt(FindConVar("tf_tournament_classlimit_sniper"), numSnipers);
}
// If a game ends, reset the number of snipers but don't flag "newgame", that's only for map changes.
public Event_GameOver(Handle:event, const String:name[], bool:dontBroadcast) {
	midCapped = false;
	SetConVarInt(FindConVar("tf_tournament_classlimit_sniper"), numSnipers);
}