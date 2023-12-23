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

  HANDLE logFile = NULL;

  for (char* ch = lpCmdLine; *ch != '\0'; ++ch) {
    if (*ch == '>') {
      // Separate the command line at the redirection

      bool append = false;
      char* prev = ch - 1;
      if (*prev == ' ') *prev = '\0';

      ++ch;
      if (*ch == '>') {append = true; ++ch;}

      while (*ch == ' ') ++ch; // Skip to next argument
      char* fileName = ch;

      if (*ch == '\0') show_assert("Invalid command line: Found EOF while trying to read the redirection filename");
      else if (*ch == '"') {
        fileName++; // Skip the opening "
        do {++ch;} while (*ch != '"' && *ch != '\0');
        if (*ch == '\0') show_assert("Invalid command line: Found unterminated string while trying to read the redirection filename");
      } else {
        while (*ch != ' ' && *ch != '\0') ++ch;
      }
      *ch = '\0'; // Terminate the filename

      logFile = CreateFileA(fileName, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, /*lpSecurityAttributes=*/nullptr, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, /*hTemplateFile=*/NULL);
      if (logFile == INVALID_HANDLE_VALUE) show_assert("Failed to create/open file '%s' (0x%X). Be sure to use an absolute path.", fileName, GetLastError());
      if (append) SetFilePointer(logFile, 0, 0, FILE_END); // Seek to end of file

      break; // As of now, we only allow one output file since we don't separate stdout and stderr.
    }
  }

  PROCESS_INFORMATION pi;
  if (!CreateProcessA(nullptr, lpCmdLine, nullptr, nullptr, /*bInheritHandles=*/TRUE, CREATE_NO_WINDOW, nullptr, nullptr, &si, &pi)) {
    show_assert("Got error 0x%X when trying to run\n%s", HRESULT_FROM_WIN32(GetLastError()), lpCmdLine);
  }

  WaitForSingleObject(pi.hProcess, INFINITE);

  // First, check to see if we're at EOF. (otherwise we wait forever in ReadFile)
  DWORD available = 0;
  PeekNamedPipe(pipe_out, /*lpBuffer=*/nullptr, /*nBufferSize=*/0, /*lpBytesRead=*/nullptr, &available, /*lpBytesLeftThisMessage=*/nullptr);

  CHAR output[5'000] = {'\0'}; // 5 KB or so
  DWORD length;

  // Then, if there is data to read, we can actually fetch it.
  if (available > 0) {
    BOOL eof = ReadFile(pipe_out, output, sizeof(output) / sizeof(output[0]) - 5, &length, NULL);
    if (eof == FALSE) {
      output[++length] = '.';
      output[++length] = '.';
      output[++length] = '.';
    }
    output[length] = '\0';

    if (logFile) {
      WriteFile(logFile, output, length, /*lpNumberOfBytesWritten=*/nullptr, /*lpOverlapped=*/nullptr);
      CloseHandle(logFile);
    }
  }

  DWORD exitCode;
  GetExitCodeProcess(pi.hProcess, &exitCode);
  if (exitCode != 0) show_assert("Process failed with code %d\n%s", exitCode, output);
  return exitCode;
}
