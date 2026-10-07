local Ambush = require "necro.game.character.Ambush"
local Collision = require "necro.game.tile.Collision"
local Currency = require "necro.game.item.Currency"
local CurrentLevel = require "necro.game.level.CurrentLevel"
local Damage = require "necro.game.system.Damage"
local Descent = require "necro.game.character.Descent"
local Entities = require "system.game.Entities"
local Event = require "necro.event.Event"
local Flyaway = require "necro.game.system.Flyaway"
local GrooveChain = require "necro.game.character.GrooveChain"
local Health = require "necro.game.character.Health"
local Inventory = require "necro.game.item.Inventory"
local ItemGeneration = require "necro.game.item.ItemGeneration"
local Object = require "necro.game.object.Object"
local ObjectEvents = require "necro.game.object.ObjectEvents"
local Player = require "necro.game.character.Player"
local RunState = require "necro.game.system.RunState"
local Utilities = require "system.utils.Utilities"

-- Docs are available via https://vortexbuffer.com/synchrony/docs/search/search_index.json
-- The game's Lua is compiled and not readable; don't bother.

-- TODO: Pause menu entry to retry level (in case you can't die?)
-- TODO: Skeleton closets/bat closets are not spawning consistently.

local youDied = false -- Tracks if we need to reapply the saved level on restart.

local savedState = nil
Event.levelLoad.add("captureLevelState", {order="entities"}, function(evt)
  -- Debugging hacks.
  if evt.zone == 1 and evt.floor == 1 then
    local Object = require "necro.game.object.Object"
    -- Object.spawn("CursedPotion", 1, 0)
    Object.spawn("MiscMap", 1, 0)
    -- Object.spawn("MiscHeartContainer", -1, 0)
    -- Object.spawn("FamiliarShopkeeper", 1, 0)
    -- Object.spawn("SpellShield", 1, 0)
    -- Object.spawn("Bomb3", 0, 1)

    -- Object.spawn("Crate", -1, 0)
    -- Object.spawn("Crate2", -1, 0)
    -- Object.spawn("Crate3", -1, 0)
    -- Object.spawn("Crate5", -1, 0)
    
    Object.spawn("Trapdoor", -2, 0)
  end
  
  if youDied then
    print("Restarting level " .. evt.zone .. "-" .. evt.floor .. " after dying")
    loadState(savedState)
    savedState.randomEntityIndex = 0
  else
    print("Reached new level " .. evt.zone .. "-" .. evt.floor .. ", making new checkpoint")
    savedState = saveState()
    savedState.randomEntities = {}
    savedState.targetLevel = CurrentLevel.getNumber()
  end
end)

Event.objectSpawn.add("captureRNG", {order="random", sequence=1, filter="random"}, function(evt)
  if youDied then
    local seed = savedState.randomEntities[savedState.randomEntityIndex]
    savedState.randomEntityIndex = savedState.randomEntityIndex + 1
    evt.entity.random = seed.rng
  elseif savedState == nil then
    -- not actually doing a run
  else
    table.insert(savedState.randomEntities, {name=evt.entity.name, rng=evt.entity.random})
  end
end)

Event.objectDescentArrive.add("spawnTrapdoorItems", {order="damage", sequence=1, filter="controllable"}, function(evt)
  if youDied then
    loadTrapdoorItems(savedState)
  end

  -- This is the last handler (for now) so it's where we clear this flag.
  youDied = false
end)

Event.levelComplete.add("replayLevel", {order="nextLevel", sequence=-1}, function(evt)
  if youDied and savedState ~= nil then
    print("Prevented level transition because you died")
    evt.targetLevel = savedState.targetLevel
  end
end)

Event.gameStateLevel.add("captureAmbushers", {order="createAmbush", sequence=1}, function(evt)
  if savedState == nil then
    return -- Invalid state
  elseif savedState.ambushers ~= nil then
    return -- Keep the first arrival's ambushers across replays.
  end
  savedState.ambushers = {}
  for entity in Entities.entitiesWithComponents({"ambusher"}) do
    if entity.ambusher.active then
      table.insert(savedState.ambushers, entity.name)
    end
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
  
  if #savedState.ambushers > 0 then
    -- When you drop down a trapdoor, the game determines if it should spawn an ambush based on the live minibosses.
    -- To get the same ambush, we need to clear the current miniboss, and spawn the one from the saved ambush.
    for entity in Entities.entitiesWithComponents({"ambusher"}) do
      entity.ambusher.pending = false
    end
    for i, name in ipairs(savedState.ambushers) do
      Object.spawn(name, -100, -100, {ambusher = {pending = true}})
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
  
  -- Per-run globals (e.g. "have you killed freddy")
  state.runState = Utilities.deepCopy(RunState.getState())

  -- Item spawns depend on what you've already seen
  state.seenItems = {}
  for item, count in pairs(ItemGeneration.getSeenCounts()) do
    state.seenItems[item] = count
  end
  
  state.trapdoorItems = {}
  for entity in Entities.entitiesWithComponents({"descent"}) do
    if entity.descent.active and string.sub(entity.name, 1, 5) == "Crate" then
      local item = {
        name = entity.name,
        health = entity.health.health,
        maxHealth = entity.health.maxHealth,
        contents = {},
        x = entity.descentPositionOffset.offsetX,
        y = entity.descentPositionOffset.offsetY,
      }
      if entity.storage ~= nil then
        for i, itemName in pairs(entity.storage.items) do
          table.insert(item.contents, itemName)
        end
      end
      table.insert(state.trapdoorItems, item)
    end
  end
  
  return state
end

function loadState(state)
  local player = Player.getPlayerEntity(1)
  
  Inventory.clear(player)
  if #state.items > 0 then
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
  if state.combo > 0 then
    for i = 1, state.combo do
      GrooveChain.increase(player)
    end
  end

  RunState.reset({player})
  for key, value in pairs(state.runState) do
    RunState.set(key, Utilities.deepCopy(value))
  end

  -- getSeenCounts returns a reference we can modify
  local mutableCounts = ItemGeneration.getSeenCounts()
  for item in pairs(mutableCounts) do
    mutableCounts[item] = state.seenItems[item] -- Will be nil if we haven't seen it before
  end
  
  -- Wipe out anything that dropped through a trapdoor so it's not there on restart
  for entity in Entities.entitiesWithComponents({"descent"}) do
    if entity.descent.active and string.sub(entity.name, 1, 5) == "Crate" then
      Object.delete(entity)
    end
  end
end

-- The trapdoor items are deferred until the player has landed, otherwise they can overlap.
function loadTrapdoorItems(state)
  for i, item in pairs(state.trapdoorItems) do
    local crate = Object.spawn(item.name, item.x, item.y, {
      health = {health = item.health, maxHealth = item.maxHealth},
      storage = {items = item.contents},
      spawnInvincibility = {active = false},
      soundDeath = nil,
    })
    Damage.inflict({
      victim = crate,
      damage = 3,
      type = Damage.Flag.EXPLOSIVE, -- Matches the real damage type
    })
  end  
end