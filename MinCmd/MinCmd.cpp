#define _CRT_SECURE_NO_WARNINGS 1
#include <cstdlib>

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <crtdbg.h>

#define show_assert(format, ...) \
  (1 != _CrtDbgReport(_CRT_ASSERT, __FILE__, __LINE__, nullptr, format, ##__VA_ARGS__)) \
  || (__debugbreak(), 0)

// Adapted from https://stackoverflow.com/a/66147288
int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
  HANDLE pipe_out, pipe_in;

  SECURITY_ATTRIBUTES attrs = {sizeof(SECURITY_ATTRIBUTES), /*lpSecurityDescriptor=*/nullptr, /*bInheritHandle=*/TRUE};
  CreatePipe(&pipe_out, &pipe_in, &attrs, 0);
  SetHandleInformation(pipe_out, HANDLE_FLAG_INHERIT, 0);

  STARTUPINFOA si;
  ZeroMemory(&si, sizeof(si));
  si.cb = sizeof(si);
  si.hStdError = pipe_in;
  si.hStdOutput = pipe_in;
  si.dwFlags |= STARTF_USESTDHANDLES;

  PROCESS_INFORMATION pi;
  if (!CreateProcessA(nullptr, lpCmdLine, nullptr, nullptr, /*bInheritHandles=*/TRUE, CREATE_NO_WINDOW, nullptr, nullptr, &si, &pi)) {
    show_assert("Got error 0x%X when trying to run\n%s", HRESULT_FROM_WIN32(GetLastError()), lpCmdLine);
  }

  WaitForSingleObject(pi.hProcess, INFINITE);
  DWORD exitCode;
  GetExitCodeProcess(pi.hProcess, &exitCode);
  if (exitCode == 0) return 0;

  CHAR output[5'000]; // 5 KB or so
  DWORD length;
  ReadFile(pipe_out, output, sizeof(output) / sizeof(output[0]), &length, NULL);
  output[length] = '\0';

  show_assert("Process failed with code %d\n%s", exitCode, output);
  return exitCode;
}
