#include <sdktools>
#include <sdkhooks>

public Plugin:myinfo =
{
  name = "Entity speed tracker",
  author = "darkid",
  description = "Calculates the speed of a moving entity. Primarily used for http://wiki.tf/Projectiles",
  version = "1.3",
}

// XYZ position for each entity.
new Float:lastPosition[2048][3];
// Prevent
new bool:doubleHookCall[2048];

public OnEntityCreated(entity, const String:classname[]) {
  if (
  // Mad Milk
   	StrEqual(classname, "tf_projectile_jar_milk") ||
  // Sandman
   	StrEqual(classname, "tf_projectile_stun_ball") ||
  // Wrap Assassin
  	StrEqual(classname, "tf_projectile_ball_ornament") ||
  // All rocket launchers, Monoculus
  	StrEqual(classname, "tf_projectile_rocket") ||
  // All flame throwers
  	StrEqual(classname, "tf_flame") ||
  // Flare Gun and Detonator
  	StrEqual(classname, "tf_projectile_flare") ||
  // All grenade launchers
  	StrEqual(classname, "tf_projectile_pipe") ||
  // All stickybomb launchers
  	StrEqual(classname, "tf_projectile_pipe_remote") ||
  // Sandvich, Buffalo Steak Sandvich
  	StrEqual(classname, "item_healthkit_medium") ||
  // Dalokohs Bar, Fishcake
  	StrEqual(classname, "item_healthkit_small") ||
  // Rescue Ranger
  	StrEqual(classname, "tf_projectile_arrow") ||
  // Sentry Gun rockets
  	StrEqual(classname, "tf_projectile_sentryrocket") ||
  // Crusader's Crossbow
  	StrEqual(classname, "tf_projectile_syringe") ||
  // Any syringe gun
  	StrEqual(classname, "tf_projectile_healing_bolt") ||
  // Huntsman
  	StrEqual(classname, "tf_projectile_arrow") ||
  // Jarate
  	StrEqual(classname, "tf_projectile_jar")
  ) {
    // Wait for the projectile to finish spawning
    SDKHook(entity, SDKHook_Spawn, ProjectileSpawned);
  }
}

public ProjectileSpawned(entity) {
  if (doubleHookCall[entity]) return;
  doubleHookCall[entity] = true;
  GetEntPropVector(entity, Prop_Send, "m_vecOrigin", lastPosition[entity]);
  // Two game frames
  CreateTimer(0.3, GetSpeed, entity, TIMER_REPEAT | TIMER_FLAG_NO_MAPCHANGE);
}

public Action:GetSpeed(Handle:timer, any:entity) {
  doubleHookCall[entity] = false;
  if (!IsValidEntity(entity)) return Plugin_Stop;
  decl Float:position[3];
  GetEntPropVector(entity, Prop_Send, "m_vecOrigin", position);
  // Ignore Z axis movement to avoid the influence of gravity
  new Float:norm = Pow(position[0]-lastPosition[entity][0], 2.0)+Pow(position[1]-lastPosition[entity][1], 2.0);
  lastPosition[entity] = position;
  for (new client = 1; client <= MaxClients; client++) {
    if (!IsClientInGame(client)) continue;
    if (IsFakeClient(client)) continue;
    PrintToChat(client, "%d: %f hu/s", entity, SquareRoot(norm) / 0.3);
  }
  return Plugin_Continue;
}
