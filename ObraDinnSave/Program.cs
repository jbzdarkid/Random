using System;
using System.IO;

namespace ObraDinnSave {
  class Program {
    private static string BtoS(bool b) {
      return b.ToString().PadRight(5);
    }

    static void Main(string[] args) {
      if (args.Length < 1) {
        Console.WriteLine("Incorrect calling pattern, you must pass the path to the save you want to view as the first argument. For example: \nObraDinnSave.exe C:/Users/localhost/AppData/LocalLow/3909/ObraDinn/ObraDinnSave-P1.txt");
        return;
      }
      SaveData.Container container = XmlSerializerHelper.DeserializeObject<SaveData.Container>(File.ReadAllText(args[0]));
      SaveData.Data data = container.unencryptedData;

      Console.WriteLine(@$"Inventory: [{string.Join(", ", data.inventory)}]");

      foreach (var disaster in data.disasters) {
        Console.WriteLine($"Chapter: {disaster.id} Started: {BtoS(disaster.revealedChartInBook)} Finished: {BtoS(disaster.revealedDisappearancesInBook)}");
      }
      foreach (var moment in data.moments) {
        Console.WriteLine($"Scene: {moment.id.PadRight(26)}Followed Trail: {BtoS(moment.revealedGhosts)} Completed: {BtoS(moment.revealedPageInBook)} Corpse Shown: {BtoS(moment.unlocked)} Visit Count: {moment.visitCount}");
      }
      foreach (var face in data.faces) {
        Console.WriteLine($"Crew Member: {face.id.PadRight(12)}Cause of Death: {face.fateId.PadRight(30)}Confirmed correct: {BtoS(face.markedCorrect)}");
      }
      foreach (var stat in data.stats) {
        Console.WriteLine($"Stat: {stat.id.PadRight(40)}Value: {stat.val}");
      }

      Console.WriteLine($"Game Version: {data.general.gameVersion}");
      Console.WriteLine(@$"Current bookmark: {data.general.bookBookmarkedCrewId ?? "null"} Current page: {data.general.bookPageId}");
      var eras = new string[]{ "ShipSomeUnvisited", "ShipAllVisited", "Tally", "Office" };
      var playTime = TimeSpan.FromSeconds(data.general.playTime);
      Console.WriteLine($"Current Game State: {eras[data.general.era]} Last Visited Scene: {data.general.lastVisitedMomentId} Playtime: {playTime}");
    }
  }
}
