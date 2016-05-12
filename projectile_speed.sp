#include <sdktools>
#include <sdkhooks>
<<<<<<< Updated upstream
=======
#include <profiler>
#define POLL_FREQ 1.0
>>>>>>> Stashed changes

public Plugin:myinfo =
{
  name = "Entity speed tracker",
  author = "darkid",
  description = "Calculates the speed of a moving entity. Primarily used for http://wiki.tf/Projectiles",
<<<<<<< Updated upstream
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
=======
  version = "0.0.2",
}

new Float:spawnPoint[2048][];
new Handle:profilers[2048];

public OnPluginStart() {
  profiler = CreateProfiler();
  StartProfiling(profiler);
  // XYZ position for a given entity.
  spawnPoint = new Float[2048][3];
  profilers = new Handle[2048];
}

public OnEntityCreated(entity, const String:classname[]) {
  SDKHook(entity, SDKHook_SpawnPost, ProjectileSpawned);
  profilers[entity] = CreateProfiler();
}
public ProjectileSpawned(entity) {
  GetEntPropVector(entity, Prop_Send, "m_vecOrigin", spawnPoint[entity]);
  StartProfiling(profilers[entity]);
}
public OnEntityDestroyed(entity) {
  if (entity < MaxClients || IsValidEntity(entity)) return;
  new Float:position[3];
  GetEntPropVector(entity, Prop_Send, "m_vecOrigin", position);
  StopProfiling(profilers[entity]);
  decl String:classname[256];
  GetEntityClassname(entity, classname, sizeof(classname));

  if (StrEqual(classname, "tf_projectile_stun_ball")) {
    GetProjectileSpeed("Sandman Ball", position, entity);
  } else if (StrEqual(classname, "tf_projectile_stun_ball")) {
    GetProjectileSpeed("Wrap Assassin Ball", position, entity);
  }
}

// Projectiles are effected by gravity, so we ignore the change in Z.
public GetProjectileSpeed(const String:name[], Float:position[], entity) {
  new Float:norm = Pow(position[0]-spawnPoint[entity][0], 2)+Pow(position[1]-spawnPoint[entity][1], 2);
  new Float:time = GetProfilerTime(profilers[entity])
  for (client = 1; client < MaxClients; client++) {
    if (!IsValidClient(client)) continue;
    if (!IsInGame(client)) continue;
    PrintToChat(client, "%s moved at speed %f", name, SquareRoot(norm) / time);
  }
}

// Rockets aren't effected by gravity, so we consider the change in Z.
public GetProjectileSpeed(const String:name[], Float:position[], entity) {
  new Float:norm = Pow(position[0]-spawnPoint[entity][0], 2)+Pow(position[1]-spawnPoint[entity][1], 2)+Pow(position[2]-spawnPoint[entity][2], 2);
  new Float:time = GetProfilerTime(profilers[entity])
  for (client = 1; client < MaxClients; client++) {
    if (!IsValidClient(client)) continue;
    if (!IsInGame(client)) continue;
    PrintToChat(client, "%s moved at speed %f", name, SquareRoot(norm) / time);
  }
>>>>>>> Stashed changes
}
