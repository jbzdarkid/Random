local Ambush = require "necro.game.character.Ambush"
local Currency = require "necro.game.item.Currency"
local CurrentLevel = require "necro.game.level.CurrentLevel"
local Descent = require "necro.game.character.Descent"
local Entities = require "system.game.Entities"
local Event = require "necro.event.Event"
local Flyaway = require "necro.game.system.Flyaway"
local GrooveChain = require "necro.game.character.GrooveChain"
local Health = require "necro.game.character.Health"
local Inventory = require "necro.game.item.Inventory"
local Player = require "necro.game.character.Player"
local RunState = require "necro.game.system.RunState"

-- TODO: Gold/items from things we push down a trapdoor are not saved. I don't know where they live.

local youDied = false -- Tracks if we need to reapply the saved level on restart.

local savedState = nil
Event.levelLoad.add("captureLevelState", {order="entities"}, function(evt)
  -- Debugging hacks.
  if evt.zone == 1 and evt.floor == 1 then
    local Object = require "necro.game.object.Object"
    -- Object.spawn("CursedPotion", 1, 0)
    -- Object.spawn("MiscHeartContainer", -1, 0)
    -- Object.spawn("FamiliarShopkeeper", 1, 0)
    -- Object.spawn("SpellShield", 1, 0)
    Object.spawn("Bomb3", 0, 1)
  end
  
  if youDied then
    print("Restarting level " .. evt.zone .. "-" .. evt.floor .. " after dying")
    loadState(savedState)
    youDied = false -- Reset the flag so we can continue to the next level
  else
    print("Reached new level " .. evt.zone .. "-" .. evt.floor .. ", making new checkpoint")
    savedState = saveState()
    savedState.targetLevel = CurrentLevel.getNumber()
  end
end)

Event.levelComplete.add("replayLevel", {order="nextLevel", sequence=-1}, function(evt)
  if youDied and savedState ~= nil then
    print("Prevented level transition because you died")
    evt.targetLevel = savedState.targetLevel
  end
end)

Event.objectTakeDamage.add("checkDeath", {order="death", sequence=-1, filter="health"}, function(evt)
  if evt.survived or evt.victim ~= Player.getPlayerEntity(1) then
    return
  end

  print("Player was killed by " .. evt.attacker.name)
  -- Stop the player from dying, and instead drop them down a trapdoor so we can restart the level.
  evt.suppressed = true
  evt.damage = 0
  
  if Ambush.isActive() then
    -- If we're replaying an ambush, make sure we don't carry the existing miniboss(es).
    for entity in Entities.entitiesWithComponents({"ambusher"}) do
      entity.ambusher.pending = entity.ambusher.active
    end
    Descent.perform(evt.victim, Descent.Type.TRAPDOOR)
  else
    Descent.perform(evt.victim, Descent.Type.STAIRS)
  end

  -- TODO: A menu? So we can choose... something else?
  Flyaway.create({
    entity = evt.victim,
    text = "! YOU DIED !",
    delay = 0,
    offsetY = -20,
    size = 10,
  })

  youDied = true
end)


function saveState()
  local state = {}
  local player = Player.getPlayerEntity(1)
  
  state.items = {}
  state.followers = {}
  for i, item in ipairs(Inventory.getItems(player)) do
    local itemData = {name = item.name}
    if item.itemStack then
      itemData.quantity = item.itemStack.quantity
    end
    if item.follower ~= nil then
      itemData.follower = item.follower
    end
    if item.spellCooldownKills ~= nil then
      itemData.remainingKills = item.spellCooldownKills.remainingKills
    end

    table.insert(state.items, itemData)
  end

  state.max = 0
  state.red = 0
  state.cursed = 0
  for i, heart in ipairs(Health.getHearts(player)) do
    state.max = state.max + 2
    if heart == Health.Heart.RED_HALF then
      state.red = state.red + 1
    elseif heart == Health.Heart.RED_FULL then
      state.red = state.red + 2
    elseif heart == Health.Heart.CURSED_HALF then
      state.cursed = state.cursed + 1
    elseif heart == Health.Heart.CURSED_FULL then
      state.cursed = state.cursed + 2
    end
  end

  state.gold = Currency.get(player, Currency.Type.GOLD)

  state.combo = player.grooveChain.killCount
  
  -- Shallow copy... maybe this is OK?
  state.runState = {}
  for k, v in pairs(RunState.getState()) do
    state.runState[k] = v
  end
  print("<127>", RunState.getState())
  
  return state
end

function loadState(state)
  local player = Player.getPlayerEntity(1)
  
  Inventory.clear(player)
  for i, item in ipairs(state.items) do
    local granted = Inventory.grant(item.name, player)
    if item.quantity ~= nil then
      granted.itemStack.quantity = item.quantity
    end
    if item.follower ~= nil then
      granted.follower = item.follower
    end
    if item.remainingKills ~= nil then
      granted.spellCooldownKills.remainingKills = item.remainingKills
    end
  end

  -- Wipe out the current health, then replace it with the correct max.
  Health.curseHealth(player, Health.getMaxHealth(player))
  Health.increaseMaxHealth(player, savedState.max, player)

  -- Reverse-engineered from the consumableHeal event
  Health.heal({
    -- allowOverheal=false,
    cursedHealth=savedState.cursed,
    entity=player,
    -- healer=player,
    health=savedState.red,
    -- holder=player,
    -- invincibility=0,
    -- maxHealth=0,
    noParticles=true,
    silent=true,
  })

  Currency.set(player, Currency.Type.GOLD, savedState.gold)

  GrooveChain.drop(player, GrooveChain.Type.DAMAGE)
  for i = 1, state.combo do
    GrooveChain.increase(player)
  end

  RunState.reset({player})
  for k, v in pairs(state.runState) do
    RunState.set(k, v)
  end
  print("<177>", RunState.getState())

end
