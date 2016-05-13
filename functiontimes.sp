#include <sdktools>
#include <sdkhooks>

public Plugin:myinfo =
{
  name = "Weapon function times",
  author = "darkid",
  description = "Calculates the speed of projectiles, and firing speed of weapons. Created for the TF2 Wiki.",
  version = "3.1",
}

new deferredEntity = -1;
new deferredEntity2 = -1;
new Float:averageSpeed = 0.0;
new numTrials = 0;
new Float:minSpeed = 9999999.9;
new Float:maxSpeed = 0.0;

public OnEntityCreated(entity, const String:classname[]) {
  if (StrEqual(classname, "instanced_scripted_scene") ||
      StrEqual(classname, "env_spritetrail") ||
      StrEqual(classname, "tf_wearable")
  ) return; // Eliminating some extraneous entities
  deferredEntity = entity;
}

public Action:TF2_CalcIsAttackCritical(client, weapon, String:weaponname[], &bool:result) {
  deferredEntity2 = GetEntPropEnt(client, Prop_Send, "m_hActiveWeapon");
}

public Float:GetSpeed(Float:velocity[3]) {
  return SquareRoot(Pow(velocity[0], 2.0)+Pow(velocity[1], 2.0)+Pow(velocity[2], 2.0));
}

public OnGameFrame() {
  if (deferredEntity2 != -1) {
    new Float:enginetime = GetGameTime();
    PrintToChat(1, "Next Primary Attack: %f", GetEntPropFloat(deferredEntity2, Prop_Send, "m_flNextPrimaryAttack") - enginetime);
    PrintToChat(1, "Next Secondary Attack: %f", GetEntPropFloat(deferredEntity2, Prop_Send, "m_flNextSecondaryAttack") - enginetime);
    PrintToChat(1, "Ammo Loaded: %d", GetEntProp(deferredEntity2, Prop_Send, "m_iClip1")); // Not working for minigun?
    deferredEntity2 = -1;
  }
  if (deferredEntity != -1) {
    decl Float:velocity[3];
    GetEntPropVector(deferredEntity, Prop_Send, "m_vInitialVelocity", velocity);
    new Float:speed = GetSpeed(velocity);
    PrintToChat(1, "Projectile speed: %f", speed);
    averageSpeed += speed;
    numTrials++;
    if (speed < minSpeed) minSpeed = speed;
    if (speed > maxSpeed) maxSpeed = speed;
    PrintToChat(1, "N: %d AVG: %f MIN: %f MAX: %f", numTrials, averageSpeed/numTrials, minSpeed, maxSpeed);
    deferredEntity = -1;
  }
}
