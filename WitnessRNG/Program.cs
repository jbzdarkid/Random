﻿using System;
using System.Collections.Generic;
using System.Diagnostics;

namespace WitnessRNG {
  class Program {
    static Dictionary<int, int> tests = new Dictionary<int, int> {
      {0x00000000, 0x6F4EE991},
      {0x7E9F198C, 0x7F467745},
      {0x7F467745, 0x6B40944A},
      {0x30B54D65, 0x4EEC3ADE},
      {0x4EEC3ADE, 0x770CED4C},
      {0x39CEB361, 0x3162C2ED},
      {0x4AEB6EEF, 0x26C03356},
      {0x146A66FA, 0x558EB18E},
      {0x02C254EC, 0x2455535E},
      {0x2455535E, 0x5DD452F4},
      {0x4C1961B0, 0x165C90D8},
      {0x165C90D8, 0x17296060},
      {0x136B3ACA, 0x64E0ADBB},
      {0x64E0ADBB, 0x5AAE03BA},
      {0x5B2B502E, 0x789D2AC4},
      {0x789D2AC4, 0x1662E7B9},
      {0x16E085CC, 0x6E701FCF},
      {0x6E701FCF, 0x033887AE},
      {0x66923B80, 0x0A80851C},
      {0x279E0D8B, 0x798B34FE},
      {0x798B34FE, 0x22444E09},
      {0x5BB34364, 0x560D8944},
      {0x560D8944, 0x12AEFB7F},
      {0x73069146, 0x342BC5A9},
      {0x342BC5A9, 0x25BDF501},
      {0x4DC4C570, 0x317E63F3},
      {0x60D3FFE7, 0x7E45C85A},
      {0x1764CD7A, 0x5AEE1095},
      {0x4AF19EE8, 0x3CF7B7C8},
      {0x3CF7B7C8, 0x2B42CABD},
      {0x25D18684, 0x5ED65781},
      {0x5ED65781, 0x4A0B06CB},
      {0x591CD356, 0x7376E0CE},
      {0x7376E0CE, 0x1A12F9B},
      {0x563EB84B, 0x2FB57029},
      {0x2FB57029, 0x30D6AC37},
      {0x15FCAE94, 0x002981D3},
      {0x002981D3, 0x250A43BA},
      {0x3B147EB8, 0x3E8B8055},
      {0x3E8B8055, 0x38966C87},
      {0x5B134979, 0x4F3CD5A5},
      {0x4F3CD5A5, 0x22EE6C47},
      {0x36F5F6EE, 0x4E269F72},
      {0x4E269F72, 0x49AE1D73},
      {0x6C09D1E0, 0x78B20089},
      {0x47E84D1F, 0x641F531A},
      {0x641F531A, 0x44890350},
      {0x48B258F5, 0x34EE621C},
      {0x34EE621C, 0x0E6B376A},
      {0x17ED52D5, 0x5DD92A38},
      {0x5C62F2AA, 0x6429A648},
      {0x6A63F457, 0x483EB252},
      {0x74AD8180, 0x2B113658},
      {0x2B113658, 0x7706E17E},
      {0x3E202585, 0x307F5EA0},
      {0x307F5EA0, 0x7A1D733F},
      {0x568C9CC6, 0x2988B78E},
      {0x2988B78E, 0x4ECAE0EF},
      {0x6D19934F, 0x2A165F7E},
      {0x471CBDBD, 0x2FECE7C4},
      {0x2FECE7C4, 0x6A640D70},
      {0x1603A8AB, 0x4A367DD7},
      {0x4A367DD7, 0x3F7FD451},
      {0x15B7C07F, 0x52BEDCFC},
      {0x52BEDCFC, 0x709E4ED4},
      {0x473B7C70, 0x1266C199},
      {0x1266C199, 0x18302D3F},
      {0x3B744AC0, 0x4FD7A1BE},
      {0x4FD7A1BE, 0x55BBE9E5},
      {0x09FC62B0, 0x18B315EF},
      {0x18B315EF, 0x15650A94},
      {0x394F0AE2, 0x745398D2},
      {0x1C563EA8, 0x622B9620},
      {0x1B8D413A, 0x56B554F7},
      {0x47338A38, 0x08B7870D},
    };

    static int m_prime = 0x7FFFFFFF; // 2^31 - 1, a mersenne prime

    static int advance_rng(int current_rng) {
      if (current_rng == 0) {
        current_rng = 111111;
      }
      // This first operation is relatively low entropy, since the multiplicand is close to -2^31 (-2'147'483'648)
      // Thus, this operation is approximately (int32_t)((float)this._current_rng / -2.053f);
      int nextRng = (int)(current_rng * -2092037281L / 0x1_0000_0000L);
      nextRng = (current_rng + nextRng) / 0x1_0000;
      // This is also kind of weird. It takes a different action if nextRng is even or odd.
      // This operation is also expressible as (nextRng % 2 == 0 : -nextRng ? 2^31 - nextRng)
      nextRng = -nextRng * m_prime;
      nextRng = nextRng + current_rng * 16807; // 16807 == 7^5
      if (nextRng <= 0) { // Rarely true in practice
        nextRng = nextRng + m_prime; // Makes the result positive, even though the output is unsigned.
      }
      return nextRng;
    }

    static void Main(string[] args) {
      foreach (var test in tests) {
        var actual = advance_rng(test.Key);
        if (actual != test.Value) {
          Debug.WriteLine($"Actual:   {actual}\nExpected: {test.Value}\n");
        }
      }

      HashSet<int> foundValues = new HashSet<int>();
      int rng = advance_rng(0);
      while (true) {
        if (foundValues.Contains(rng)) break;
        if (foundValues.Count >= 100_000_000) break;
        foundValues.Add(rng);
        rng = advance_rng(rng);
      }
      Console.WriteLine($"RNG loops after {foundValues.Count} iterations");
      Console.ReadLine();
    }
  }
}
