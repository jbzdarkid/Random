using System;
using System.IO;
using System.Text;
using System.Xml;
using System.Xml.Serialization;

public class XmlSerializerHelper
{
  public static string SerializeObject(object obj)
  {
    try
    {
      MemoryStream memoryStream = new MemoryStream();
      XmlSerializer xmlSerializer = new XmlSerializer(obj.GetType());
      Encoding encoding = Encoding.GetEncoding("ISO-8859-1");
      XmlTextWriter xmlTextWriter = new XmlTextWriter(memoryStream, encoding);
      xmlSerializer.Serialize(xmlTextWriter, obj);
      MemoryStream baseStream = (MemoryStream) xmlTextWriter.BaseStream;
      return encoding.GetString(baseStream.ToArray());
    }
    catch (Exception)
    {
      return null;
    }
  }

  public static T DeserializeObject<T>(string xml)
  {
    try
    {
      return (T) new XmlSerializer(typeof (T)).Deserialize(new MemoryStream(Encoding.GetEncoding("ISO-8859-1").GetBytes(xml)));
    }
    catch (Exception)
    {
      return default;
    }
  }

  public static byte[] StringToByteArray(string s)
  {
    byte[] numArray = new byte[s.Length];
    for (int index = 0; index < s.Length; ++index)
      numArray[index] = (byte) s[index];
    return numArray;
  }

  public static string ByteArrayToString(byte[] b)
  {
    string empty = string.Empty;
    for (int index = 0; index < b.Length; ++index)
      empty += (string) (object) (char) b[index];
    return empty;
  }
}
