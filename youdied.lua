local Ambush = require "necro.game.character.Ambush"
local Currency = require "necro.game.item.Currency"
local Descent = require "necro.game.character.Descent"
local Entities = require "system.game.Entities"
local Event = require "necro.event.Event"
local Flyaway = require "necro.game.system.Flyaway"
local Health = require "necro.game.character.Health"
local Inventory = require "necro.game.item.Inventory"
local Object = require "necro.game.object.Object"
local Player = require "necro.game.character.Player"
local Tile = require "necro.game.tile.Tile"

-- TODO: Gold/items from things we push down a trapdoor are not saved. I don't know where they live.
-- TODO: Maintain the beat count (e.g. multiplier)
-- TODO: Maintain spell status
-- TODO: Maintain zone (not just floor)

local youDied = false -- Tracks if we need to reapply the saved level on restart.

local savedItems = nil
local savedHealth = nil
local savedFloor = nil
local savedGold = nil
Event.levelLoad.add("captureLevelState", {order="entities"}, function(evt)
  -- Debugging hacks.
  -- if evt.zone == 1 and evt.floor == 1 then
  --   Object.spawn("MiscPotion", 1, 0)
  --   Object.spawn("Bomb3", 0, 1)
  -- end
  
  local player = Player.getPlayerEntity(1) -- Should I use Player.getPlayerEntities()?
  if youDied then
    print("Restarting level " .. evt.zone .. "-" .. evt.floor .. " after dying")

    if #savedItems > 0 then
      Inventory.clear(player)
      for item, quantity in pairs(savedItems) do
        local granted = Inventory.grant(item, player)
        if quantity > 1 then
          granted.itemStack.quantity = quantity
        end
      end
    end

    local currentHealth = getHealth(player)
    Health.increaseMaxHealth(player, savedHealth.max - currentHealth.max, player)
    heal(player, savedHealth.red - currentHealth.red, savedHealth.cursed - currentHealth.cursed)

    Currency.set(player, Currency.Type.GOLD, savedGold)

    youDied = false -- Reset the flag so we can continue to the next level... if we don't die.
  else
    print("Reached new level " .. evt.zone .. "-" .. evt.floor .. ", making new checkpoint")

    savedItems = {}
    for i, item in ipairs(Inventory.getItems(player)) do
      if item.itemStack then
        savedItems[item.name] = item.itemStack.quantity
      else
        savedItems[item.name] = 1
      end
    end
    
    savedHealth = getHealth(player)

    savedGold = Currency.get(player, Currency.Type.GOLD)

    savedFloor = evt.floor
  end
end)

Event.objectTakeDamage.add("checkDeath", {order="death", sequence=-1, filter="health"}, function(evt)
  if evt.victim == Player.getPlayerEntity(1) and not evt.survived then
    print("Player was killed by " .. evt.attacker.name)
    evt.suppressed = true
    evt.damage = 0
    showPopup(evt.victim, "! YOU DIED !") -- TODO: A menu? So we can choose... something else?
    if Ambush.isActive() then
      -- If we're replaying an ambush, make sure we don't carry the existing miniboss.
      for entity in Entities.entitiesWithComponents({"ambusher"}) do
        entity.ambusher.pending = entity.ambusher.active
      end
      Descent.perform(evt.victim, Descent.Type.TRAPDOOR)
    else
      Descent.perform(evt.victim, Descent.Type.STAIRS)
    end
    youDied = true
  end
end)

Event.levelComplete.add("replayLevel", {order="nextLevel", sequence=-1}, function(evt)
  if youDied then
    print("You died, restarting level")
    evt.targetLevel = savedFloor
  end
end)

-- Reverse-engineered from the consumableHeal event
function heal(entity, red, cursed)
  Health.heal({
    -- allowOverheal=false,
    cursedHealth=cursed,
    entity=entity,
    -- healer=entity,
    health=red,
    -- holder=entity,
    -- invincibility=0,
    -- maxHealth=0,
    noParticles=true,
    silent=true,
  })
end

function getHealth(entity)
  local counts = {max = 0, red = 0, cursed = 0}
  for i, heart in ipairs(Health.getHearts(entity)) do
    counts.max = counts.max + 2
    if heart == Health.Heart.RED_HALF then
      counts.red = counts.red + 1
    elseif heart == Health.Heart.RED_FULL then
      counts.red = counts.red + 2
    elseif heart == Health.Heart.CURSED_HALF then
      counts.cursed = counts.cursed + 1
    elseif heart == Health.Heart.CURSED_FULL then
      counts.cursed = counts.cursed + 2
    end
  end
  return counts
end

function showPopup(entity, text)
  Flyaway.create({
    entity = entity,
    text = text,
    delay = 0,
    offsetY = -20,
    size = 10,
  })
end