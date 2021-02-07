using System;
using System.Text;

public class TeaEncryptor
{
  private readonly string _cryptoKey;
  private static UTF8Encoding _encoding = new UTF8Encoding();

  public TeaEncryptor(string cryptoKey)
  {
    int length = cryptoKey.Length;
    if (length > 16)
      cryptoKey = cryptoKey.Substring(0, 16);
    else if (length < 16)
      cryptoKey = cryptoKey.PadRight(16, ' ');
    this._cryptoKey = cryptoKey;
  }

  public string Encrypt(string text)
  {
    uint[] longs1 = this.ToLongs(this.GetByteForEncryption(text));
    uint[] longs2 = this.ToLongs(_encoding.GetBytes(this._cryptoKey.Substring(0, 16)));
    uint length = (uint) longs1.Length;
    uint num1 = longs1[length - 1U];
    uint num2 = longs1[0];
    uint num3 = 2654435769;
    uint num4 = 6U + 52U / length;
    uint num5 = 0;
    while (num4-- > 0U)
    {
      num5 += num3;
      uint num6 = num5 >> 2 & 3U;
      uint num7;
      for (num7 = 0U; num7 < length - 1U; ++num7)
      {
        uint num8 = longs1[num7 + 1U];
        num1 = longs1[num7] += (uint) (((int) (num1 >> 5) ^ (int) num8 << 2) + ((int) (num8 >> 3) ^ (int) num1 << 4) ^ ((int) num5 ^ (int) num8) + ((int) longs2[num7 & 3U ^ num6] ^ (int) num1));
      }
      uint num9 = longs1[0];
      num1 = longs1[length - 1U] += (uint) (((int) (num1 >> 5) ^ (int) num9 << 2) + ((int) (num9 >> 3) ^ (int) num1 << 4) ^ ((int) num5 ^ (int) num9) + ((int) longs2[num7 & 3U ^ num6] ^ (int) num1));
    }
    return Convert.ToBase64String(this.ToBytes(longs1));
  }

  private byte[] GetByteForEncryption(string text)
  {
    byte[] numArray1 = _encoding.GetBytes(text);
    if (numArray1.Length < 6)
    {
      byte[] numArray2 = new byte[6];
      for (int index = 0; index < numArray2.Length; ++index)
        numArray2[index] = 0;
      Buffer.BlockCopy(numArray1, 0, numArray2, 0, numArray1.Length);
      numArray1 = numArray2;
    }
    return numArray1;
  }

  public string Decrypt(string encrypted)
  {
    if (encrypted.Length == 0)
      return string.Empty;
    try
    {
      uint[] longs1 = this.ToLongs(Convert.FromBase64String(encrypted));
      uint[] longs2 = this.ToLongs(_encoding.GetBytes(this._cryptoKey.Substring(0, 16)));
      if (longs1.Length == 0)
        return null;
      uint length = (uint) longs1.Length;
      uint num1 = longs1[length - 1U];
      uint num2 = longs1[0];
      uint num3 = 2654435769;
      uint num4 = (6U + 52U / length) * num3;
      for (; num4 != 0U; num4 -= num3)
      {
        uint num5 = num4 >> 2 & 3U;
        uint num6;
        for (num6 = length - 1U; num6 > 0U; --num6)
        {
          uint num7 = longs1[num6 - 1U];
          num2 = longs1[num6] -= (uint) (((int) (num7 >> 5) ^ (int) num2 << 2) + ((int) (num2 >> 3) ^ (int) num7 << 4) ^ ((int) num4 ^ (int) num2) + ((int) longs2[num6 & 3U ^ num5] ^ (int) num7));
        }
        uint num8 = longs1[length - 1U];
        num2 = longs1[0] -= (uint) (((int) (num8 >> 5) ^ (int) num2 << 2) + ((int) (num2 >> 3) ^ (int) num8 << 4) ^ ((int) num4 ^ (int) num2) + ((int) longs2[num6 & 3U ^ num5] ^ (int) num8));
      }
      return _encoding.GetString(this.ToBytes(longs1)).TrimEnd(new char[1]);
    }
    catch
    {
    }
    return null;
  }

  private uint[] ToLongs(byte[] s)
  {
    uint[] numArray = new uint[(int) Math.Ceiling(s.Length / 4M)];
    for (int index = 0; index < numArray.Length; ++index)
      numArray[index] = (uint) (s[index * 4] + (index * 4 + 1 < s.Length ? s[index * 4 + 1] << 8 : 0) + (index * 4 + 2 < s.Length ? s[index * 4 + 2] << 16 : 0) + (index * 4 + 3 < s.Length ? s[index * 4 + 3] << 24 : 0));
    return numArray;
  }

  private byte[] ToBytes(uint[] l)
  {
    byte[] numArray = new byte[l.Length * 4];
    for (int index = 0; index < l.Length; ++index)
    {
      numArray[index * 4] = (byte) (l[index] & byte.MaxValue);
      numArray[index * 4 + 1] = (byte) (l[index] >> 8);
      numArray[index * 4 + 2] = (byte) (l[index] >> 16);
      numArray[index * 4 + 3] = (byte) (l[index] >> 24);
    }
    return numArray;
  }
}
