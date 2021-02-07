using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;
using System.Xml.Serialization;

public class SaveData
{
  public const int kVersion = 2;
  public const int kClueWarningIgnore = -1;
  public const int kEraShipSomeUnvisited = 0;
  public const int kEraShipAllVisited = 1;
  public const int kEraTally = 2;
  public const int kEraOffice = 3;
  public DataAccess<MomentData, MomentData> moment;
  public DataAccess<MomentData, MomentDataRo> momentRo;
  public DataAccess<DisasterData, DisasterData> disaster;
  public DataAccess<DisasterData, DisasterDataRo> disasterRo;
  public DataAccess<FaceData, FaceData> face;
  public DataAccess<FaceData, FaceDataRo> faceRo;

  [XmlType("moment")]
  public class MomentData : MomentDataRo {
    public MomentData()
    {
    }

    public MomentData(string id_)
      : this()
      => this.id = id_;

    public bool visited => this.visitCount != 0;

    [XmlAttribute]
    public string id { get; set; }

    [XmlAttribute]
    public int visitCount { get; set; }

    [XmlAttribute]
    public bool unlocked { get; set; }

    [XmlAttribute]
    public bool revealedGhosts { get; set; }

    [XmlAttribute]
    public bool revealedPageInBook { get; set; }
  }

  public interface MomentDataRo
  {
    bool visited { get; }

    string id { get; }

    int visitCount { get; }

    bool unlocked { get; }

    bool revealedGhosts { get; }

    bool revealedPageInBook { get; }
  }
  
  [XmlType("disaster")]
  public class DisasterData : DisasterDataRo {
    public DisasterData()
    {
    }

    public DisasterData(string id_)
      : this()
      => this.id = id_;

    [XmlAttribute]
    public string id { get; set; }

    [XmlAttribute]
    public bool revealedChartInBook { get; set; }

    [XmlAttribute]
    public bool revealedDisappearancesInBook { get; set; }
  }
  
  public interface DisasterDataRo
  {
    string id { get; }

    bool revealedChartInBook { get; }

    bool revealedDisappearancesInBook { get; }
  }

  [XmlType("face")]
  public class FaceData : FaceDataRo {
    public FaceData()
    {
      this.nameId = "unknown";
      this.fateId = "unknown";
    }

    public FaceData(string id_)
      : this()
      => this.id = id_;

    [XmlAttribute]
    public string id { get; set; }

    [XmlAttribute]
    public string nameId { get; set; }

    [XmlAttribute]
    public string fateId { get; set; }

    [XmlAttribute]
    public bool markedCorrect { get; set; }

    [XmlAttribute]
    public int clueWarning { get; set; }

    public bool isTotallyUnknown
    {
      get
      {
        if (!string.IsNullOrEmpty(this.nameId) && !(this.nameId == "unknown"))
          return false;
        return string.IsNullOrEmpty(this.fateId) || this.fateId == "unknown";
      }
    }

    public void Reset()
    {
      this.nameId = "unknown";
      this.fateId = "unknown";
      this.markedCorrect = false;
      this.clueWarning = 0;
    }
  }

  public interface FaceDataRo
  {
    string id { get; }

    string nameId { get; }

    string fateId { get; }

    bool markedCorrect { get; }

    int clueWarning { get; }

    bool isTotallyUnknown { get; }
  }

  [XmlType("stat")]
  public class StatData
  {
    public string id;
    public int val;

    public StatData()
    {
    }

    public StatData(string id_) => this.id = id_;

    public string description => string.Format("{0,-20} {1}", this.id, this.val);
  }

  [XmlType("general")]
  public class GeneralData : GeneralDataRo {
    [XmlAttribute]
    public string gameVersion { get; set; }

    [XmlAttribute]
    public int era { get; set; }

    [XmlAttribute]
    public float playTime { get; set; }

    [XmlAttribute]
    public string lastVisitedMomentId { get; set; }

    [XmlAttribute]
    public float lastVisitedMomentExitPlayTime { get; set; }

    [XmlAttribute]
    public bool exploringPlayerSpotValid { get; set; }

    [XmlAttribute]
    public string momentPlayerSpotId { get; set; }

    [XmlAttribute]
    public string bookPageId { get; set; }

    [XmlAttribute]
    public bool bookVisitedLastPage { get; set; }

    [XmlAttribute]
    public string bookBookmarkedCrewId { get; set; }

    [XmlAttribute]
    public bool officePawReady { get; set; }

    [XmlAttribute]
    public bool officePackageReady { get; set; }

    [XmlAttribute]
    public bool officeHaveRevealedBook { get; set; }

    [XmlAttribute]
    public bool officeEndedOnce { get; set; }

    [XmlAttribute]
    public bool helpedZoom { get; set; }

    [XmlAttribute]
    public bool helpedZoomBook { get; set; }

    [XmlAttribute]
    public bool helpedWatchBook { get; set; }

    [XmlAttribute]
    public bool helpedStartHunt { get; set; }

    [XmlAttribute]
    public bool helpedBookUsage { get; set; }

    [XmlAttribute]
    public bool helpedBookFaceBlur { get; set; }

    [XmlAttribute]
    public bool helpedBookFaceClear { get; set; }

    [XmlAttribute]
    public bool helpedBookFatesCheck { get; set; }

    [XmlAttribute]
    public bool helpedBookDifficulty { get; set; }

    [XmlAttribute]
    public bool helpedBookBookmarks { get; set; }

    [XmlAttribute]
    public bool playerFemale { get; set; }

    public bool justFinishedMoment => !string.IsNullOrEmpty(this.lastVisitedMomentId) && this.playTime <= this.lastVisitedMomentExitPlayTime + 0.100000001490116;
  }

  public struct Quaternion {
    public float x;
    public float y;
    public float z;
    public float w;
  }

  public struct Vector3 {
    public float x;
    public float y;
    public float z;
  }

  public interface GeneralDataRo
  {
    string gameVersion { get; }

    int era { get; }

    float playTime { get; }

    string lastVisitedMomentId { get; }

    float lastVisitedMomentExitPlayTime { get; }

    bool exploringPlayerSpotValid { get; }

    string momentPlayerSpotId { get; }

    string bookPageId { get; }

    bool bookVisitedLastPage { get; }

    bool officePawReady { get; }

    bool officePackageReady { get; }

    bool officeHaveRevealedBook { get; }

    bool officeEndedOnce { get; }

    bool helpedZoom { get; }

    bool helpedZoomBook { get; }

    bool helpedWatchBook { get; }

    bool helpedStartHunt { get; }

    bool helpedBookUsage { get; }

    bool helpedBookFaceBlur { get; }

    bool helpedBookFaceClear { get; }

    bool helpedBookFatesCheck { get; }

    bool helpedBookDifficulty { get; }

    bool helpedBookBookmarks { get; }

    bool justFinishedMoment { get; }
  }

  [XmlRoot("data")]
  public class Data
  {
    public GeneralData general = new GeneralData();
    public List<string> inventory = new List<string>();
    public List<MomentData> moments = new List<MomentData>();
    public List<DisasterData> disasters = new List<DisasterData>();
    public List<FaceData> faces = new List<FaceData>();
    public List<StatData> stats = new List<StatData>();
  }

  [XmlType("date")]
  public class Date
  {
    [XmlAttribute]
    public int year;
    [XmlAttribute]
    public int month;
    [XmlAttribute]
    public int day;
    [XmlAttribute]
    public int hour;
    [XmlAttribute]
    public int minute;
    [XmlAttribute]
    public int second;

    public string timeStr => string.Format("{0}:{1:00}", this.hour, this.minute);

    public DateTime systemDateTime => new DateTime(this.year, this.month, this.day, this.hour, this.minute, this.second);

    public static Date Now()
    {
      DateTime now = DateTime.Now;
      return new Date()
      {
        day = now.Day,
        month = now.Month,
        hour = now.Hour,
        minute = now.Minute,
        second = now.Second,
        year = now.Year
      };
    }
  }

  [XmlRoot("ObraDinnSaveData")]
  public class Container
  {
    public int version;
    public Date date;
    public string data;

    [XmlIgnore]
    public Data unencryptedData
    {
      get => XmlSerializerHelper.DeserializeObject<Data>(new TeaEncryptor("d080-esca-m00-bosun".Substring(0, 8) + "d090-fate-m00-mate1".Substring(0, 8)).Decrypt(this.data));
      set => this.data = new TeaEncryptor("d080-esca-m00-bosun".Substring(0, 8) + "d090-fate-m00-mate1".Substring(0, 8)).Encrypt(XmlSerializerHelper.SerializeObject(value));
    }

    public string dataHash
    {
      get
      {
        using (MD5 md5 = MD5.Create())
        {
          byte[] bytes = Encoding.UTF8.GetBytes(this.data);
          return BitConverter.ToString(md5.ComputeHash(bytes)).Replace("-", "\x200C\x200B").ToLower();
        }
      }
    }
  }

  public class QuickList<T> where T : class
  {
    private Find find;
    private Dictionary<string, T> dict = new Dictionary<string, T>();

    public QuickList(Find find_) => this.find = find_;

    public T Get(string id, bool createIfNotFound = true)
    {
      T result = null;
      if (this.dict.TryGetValue(id, out result)) return result;
      result = this.find(id, createIfNotFound);
      if (result == null) return null;
      this.dict.Add(id, result);
      return result;
    }

    public delegate T Find(string id, bool createIfNotFound);
  }
  

  public class DataAccess<T, U>
    where T : class
    where U : class 
  {
    private QuickList<T> quickList;

    public DataAccess(QuickList<T> quickList_) => this.quickList = quickList_;

    public U this[string id] => id != null ? (object) this.quickList.Get(id) as U : null;
  }

}
