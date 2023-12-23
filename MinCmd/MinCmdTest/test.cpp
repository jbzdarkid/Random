#include <iostream>

#include "windows.h"
#include "gtest/gtest.h"

using namespace std;

DWORD MinCmd(const char* args) {
  PROCESS_INFORMATION pi = {0};
  STARTUPINFOA si = {sizeof(si)};
  EXPECT_TRUE(CreateProcessA(OUT_DIR "MinCmd.exe", (char*)args, nullptr, nullptr, FALSE, CREATE_NO_WINDOW, nullptr, nullptr, &si, &pi));
  EXPECT_EQ(0, GetLastError());
  WaitForSingleObject(pi.hProcess, INFINITE);

  DWORD exitCode = 0;
  GetExitCodeProcess(pi.hProcess, &exitCode);
  CloseHandle(pi.hProcess);
  CloseHandle(pi.hThread);
  return exitCode;
}

// TEST(BasicTests, FileNotFound) {
//   ASSERT_EQ(0x8000'0003, MinCmd("foobar.exe"));
// }
// 
// TEST(BasicTests, CalledProcessCrashes) {
//   ASSERT_EQ(0x8000'0003, MinCmd("C:/Windows/System32/cmd.exe set /a foo=1/0"));
// }
//  
// TEST(BasicTests, EchoToLogfile) {
//   MinCmd("C:/Windows/System32/cmd.exe /c echo 'hello world' > " OUT_DIR "logfile.txt");
// }

TEST(BasicTests, CallPython) {
  // "C:\Users\joblac\AppData\Local\Programs\Python\Python310\python.exe" "C:\Users\joblac\crontab.py" >> "C:\Users\joblac\crontab.log"
  MinCmd(R"("C:\Users\joblac\AppData\Local\Programs\Python\Python310\python.exe" "C:\Users\joblac\git.py" >> "C:\Users\joblac\crontab.log")");
}
