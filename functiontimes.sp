#include <sdktools>
#include <sdkhooks>

public Plugin:myinfo =
{
  name = "Weapon function times",
  author = "darkid",
  description = "Calculates the speed of projectiles, and firing speed of weapons. Created for the TF2 Wiki.",
  version = "3.2",
}

new deferredEntity = -1;
new deferredEntity2 = -1;

public OnPluginStart() {
  RegConsoleCmd("sm_setspell", SetSpell);
}

public Action:SetSpell(client, args) {
  if (args == 0) {
    ReplyToCommand(client, "Usage: sm_setspell <id>\n\
0\tFireball\n\
1\tBall O' Bats\n\
2\tUber Heal\n\
3\tPumpkin MIRV\n\
4\tBlast Jump\n\
5\tStealth\n\
6\tTeleport\n\
7\tBall O' Lightning\n\
8\tMinify\n\
9\tMeteor Storm\n\
10\tSummon MONOCULUS\n\
11\tSummon Skeletons (Spawns 3)\n\
12\tBoxing Rocket\n\
13\tB.A.S.E. Jump\n\
14\tUber Heal (Bumper Cars version)\n\
15\tBombinomicon Head\n\
");
  }
  new String:arg[16];
  GetCmdArg(1, arg, sizeof(arg));
  new spellbook = FindEntityByClassname(0, "tf_weapon_spellbook");
  SetEntProp(spellbook, Prop_Send, "m_iSelectedSpellIndex", StringToInt(arg));
  SetEntProp(spellbook, Prop_Send, "m_iSpellCharges", 999999);
  return Plugin_Handled;
}

public OnEntityCreated(entity, const String:classname[]) {
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
  if (deferredEntity != -1 && IsValidEntity(deferredEntity)) {
    new offset = GetEntSendPropOffs(deferredEntity, "m_vInitialVelocity");
    if (offset == -1) { // Not a projectile, since it doesn't have velocity.
      deferredEntity = -1;
      return;
    }

    static Float:averageSpeed = 0.0;
    static numTrials = 0;
    static Float:minSpeed = 9999999.9;
    static Float:maxSpeed = 0.0;

    decl Float:velocity[3];
    GetEntDataVector(deferredEntity, offset, velocity);
    new Float:speed = GetSpeed(velocity);
    if (speed == 0.0) return;
    PrintToChat(1, "Projectile speed: %f", speed);
    averageSpeed += speed;
    numTrials++;
    if (speed < minSpeed) minSpeed = speed;
    if (speed > maxSpeed) maxSpeed = speed;
    PrintToChat(1, "N: %d AVG: %f MIN: %f MAX: %f", numTrials, averageSpeed/numTrials, minSpeed, maxSpeed);
    deferredEntity = -1;
  }
}
