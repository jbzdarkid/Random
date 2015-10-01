#include <sourcemod>
#include <sdkhooks>
#define SPLIT 5
#pragma semicolon 1

public Plugin:myinfo =
{
	name = "Smooth witch damage",
	author = "Darkid",
	description = "Smooths out the damage taken from a witch while incapped.",
	version = "1.5",
	url = "https://github.com/jbzdarkid/Random/witchdamage"
}

new Float:witchDamage;
new Handle:deadWitches;
new Float:startTick;
new bool:lateLoad = false;

public APLRes:AskPluginLoad2(Handle:plugin, bool:late, String:error[], errMax) {
	lateLoad = late;
	return APLRes_Success;
}

public OnPluginStart() {
	if (lateLoad) {
		for (new client=1; client<=MaxClients; client++) {
			if (!IsClientInGame(client)) continue;
			OnClientPostAdminCheck(client);
		}
	}

	decl String:witchDamageString[64];
	GetConVarString(FindConVar("z_witch_damage_per_kill_hit"), witchDamageString, sizeof(witchDamageString));
	HookConVarChange(FindConVar("z_witch_damage_per_kill_hit"), OnWitchDamageChange);
	witchDamage = 1.0*StringToInt(witchDamageString);

	deadWitches = CreateArray(64);

	HookEvent("round_start", round_start);
	HookEvent("witch_killed", witch_killed);
	startTick = 0.0;
}

public OnWitchDamageChange(Handle:cvar, const String:oldVal[], const String:newVal[]) {
	witchDamage = 1.0*StringToInt(newVal);
}

public OnClientPostAdminCheck(client) {
	SDKHook(client, SDKHook_OnTakeDamage, OnTakeDamage);
}

public round_start(Handle:event, const String:name[], bool:dontBroadcast) {
	ClearArray(deadWitches);
}

bool:IsWitch(entity) {
	if (entity <= 0 || !IsValidEntity(entity) || !IsValidEdict(entity)) return false;
	decl String:className[8];
	GetEdictClassname(entity, className, sizeof(className));
	return strcmp(className, "witch") == 0;
}

public Action:OnTakeDamage(victim, &attacker, &inflictor, &Float:damage, &damageType) {
	if (victim <= 0 || victim > MaxClients || !IsClientInGame(victim)) return Plugin_Continue;
	if (!IsWitch(attacker)) return Plugin_Continue;
	if (damage != witchDamage) return Plugin_Continue; // A hack. We assume the first scratch isn't the same damage as an incap scratch.
	if (startTick == 0.0) startTick = GetEngineTime();
	new Handle:data = CreateArray(64);
	PushArrayCell(data, victim);
	PushArrayCell(data, attacker);
	PushArrayCell(data, inflictor);
	PushArrayCell(data, damageType);
	PushArrayCell(data, SPLIT-1);
	// The witch scratch animation is every 1/4 second. Repeat until all the damage is done.
	CreateTimer(0.25, WitchScratch, data, TIMER_REPEAT | TIMER_FLAG_NO_MAPCHANGE);

	// Allow this scratch's damage through, to an appropriate degree.
	damage = witchDamage/SPLIT;
	PrintToChatAll("[%2.3f] Player %d took %3f damage (%d of %d) from witch %d/%d.", GetEngineTime()-startTick, victim, witchDamage/SPLIT, 1, SPLIT, attacker, inflictor);
	return Plugin_Continue;
}

public Action:WitchScratch(Handle:timer, any:data) {
	new victim = GetArrayCell(data, 0);
	// If defibrillator_use_time is less than .25, this may bug out.
	if (!IsPlayerAlive(victim)) return Plugin_Stop;
	new attacker = GetArrayCell(data, 1);
	new inflictor = GetArrayCell(data, 2);
	new damageType = GetArrayCell(data, 3);
	new count = GetArrayCell(data, 4);
	if (count <= 0) return Plugin_Stop;
	new index = FindValueInArray(deadWitches, attacker);
	if (index != -1) return Plugin_Stop;
	SDKHooks_TakeDamage(victim, attacker, inflictor, witchDamage/SPLIT, damageType);
	SetArrayCell(data, 4, count-1);
	return Plugin_Continue;
}

public witch_killed(Handle:event, const String:name[], bool:dontBroadcast) {
	new witch = GetEventInt(event, "witchid");
	PushArrayCell(deadWitches, witch);
}