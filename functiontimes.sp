#include <sdktools>
#include <sdkhooks>

public Plugin:myinfo =
{
  name = "Weapon function times",
  author = "darkid",
  description = "Calculates the speed of projectiles, and firing speed of weapons. Created for the TF2 Wiki.",
  version = "2.8",
}

new deferredEntity = -1;
new String:deferredEntityName[64];
new deferredEntity2 = -1;
new Float:averageSpeed = 0.0;
new numTrials = 0;
new Float:minSpeed = 9999999.9;
new Float:maxSpeed = 0.0;

public OnEntityCreated(entity, const String:classname[]) {
  if (StrEqual(classname, "instanced_scripted_scene") ||
      StrEqual(classname, "env_spritetrail")
  ) return;

  deferredEntity = entity;
  strcopy(deferredEntityName, sizeof(deferredEntityName), classname);
  PrintToChat(1, deferredEntityName);
}

public Action:TF2_CalcIsAttackCritical(client, weapon, String:weaponname[], &bool:result) {
  deferredEntity2 = GetEntDataEnt2(client, FindSendPropInfo("CTFPlayer", "m_hActiveWeapon"));
}

public Float:GetSpeed(Float:velocity[3]) {
  return SquareRoot(Pow(velocity[0], 2.0)+Pow(velocity[1], 2.0)+Pow(velocity[2], 2.0));
}

public OnGameFrame() {
  if (deferredEntity2 != -1) {
    new Float:enginetime = GetGameTime();
    PrintToChat(1, "Next Primary Attack: %f", GetEntDataFloat(deferredEntity2, FindSendPropInfo("CBaseCombatWeapon", "m_flNextPrimaryAttack")) - enginetime);
    PrintToChat(1, "Next Secondary Attack: %f", GetEntDataFloat(deferredEntity2, FindSendPropInfo("CBaseCombatWeapon", "m_flNextSecondaryAttack")) - enginetime);
    PrintToChat(1, "Ammo Loaded: %d", GetEntData(deferredEntity2, FindSendPropInfo("CBaseCombatWeapon", "m_iClip1"))); // Not working for minigun?
    deferredEntity2 = -1;
  }
  if (deferredEntity != -1) {
    decl Float:velocity[3];
    // https://forums.alliedmods.net/showthread.php?p=1349107
    // CTFFlameRocket
    // CTFProjectile_Throwable
    if (StrEqual(deferredEntityName, "tf_projectile_rocket")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_Rocket", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_pipe")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFGrenadePipebombProjectile", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_healing_bolt")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_HealingBolt", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_flare")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_Flare", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_stun_ball")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFStunBall", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_cleaver")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_Cleaver", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_ball_ornament")) {
     GetEntDataVector(deferredEntity, FindSendPropInfo("CTFBall_Ornament", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_jar_milk")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_JarMilk", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_jar")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_Jar", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_sentryrocket")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_SentryRocket", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_arrow")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_Arrow", "m_vInitialVelocity"), velocity);
    } else if (StrEqual(deferredEntityName, "tf_projectile_energy_ball")) {
      GetEntDataVector(deferredEntity, FindSendPropInfo("CTFProjectile_EnergyBall", "m_vInitialVelocity"), velocity);
    } else return;
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
