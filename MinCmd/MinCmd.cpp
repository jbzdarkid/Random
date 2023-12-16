#define _CRT_SECURE_NO_WARNINGS 1
#include <cstdlib>

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <crtdbg.h>

// TODO:
// - executable names do not search the path, they must be fully specified
// - Task scheduler runs tasks from System32, so relative anything won't work.

#ifdef _DEBUG
#define show_assert(format, ...) \
  (1 != _CrtDbgReport(_CRT_ASSERT, __FILE__, __LINE__, nullptr, format, ##__VA_ARGS__)) \
  || (__debugbreak(), 0)
#else
#define show_assert(format, ...) __debugbreak()
#endif

DWORD ReadPipe(HANDLE pipe, CHAR* buffer, DWORD bufferSize) {
  DWORD totalBytesAvail = 0;
  DWORD bytesRead = 0;
  PeekNamedPipe(pipe, buffer, bufferSize, &bytesRead, &totalBytesAvail, /*lpBytesLeftThisMessage=*/nullptr);
  if (totalBytesAvail == 0) return 0; // No data to be read

  // Skip the number of bytes we *read*, not the number of bytes left (we might have more than fit into the buffer)
  SetFilePointer(pipe, bytesRead, /*lpDistanceToMoveHigh=*/nullptr, FILE_CURRENT);

  return bytesRead; // Should be nonzero.
}

int __stdcall WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
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
    // Handling basic pipe syntax `>` and `>>`
    if (*ch == '>') {
      bool append = false;

      // Replace with EOF so that the preceeding text looks like a complete command
      *ch = '\0';
      ++ch;
      if (*ch == '>') {append = true; ++ch;} // Check for '>>'
      while (*ch == ' ') ++ch; // Skip whitespace before filename

      LPSTR fileName = ch;
      if (*ch == '\0') show_assert("Invalid command line: Found EOF while trying to read the redirection filename");
      else if (*ch == '"') {
        fileName++; // Skip the opening "
        do {++ch;} while (*ch != '"' && *ch != '\0');
        if (*ch == '\0') show_assert("Invalid command line: Found unterminated string while trying to read the redirection filename");
      } else {
        while (*ch != ' ' && *ch != '\0') ++ch;
      }
      *ch = '\0'; // Terminate the filename

      logFile = CreateFileA(fileName, GENERIC_READ | GENERIC_WRITE, /*dwShareMode=*/NULL, /*lpSecurityAttributes=*/nullptr, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, /*hTemplateFile=*/NULL);
      if (logFile == INVALID_HANDLE_VALUE) show_assert("Failed to create/open file '%s' (0x%X). Be sure to use an absolute path.", fileName, GetLastError());
      if (append) SetFilePointer(logFile, 0, 0, FILE_END); // Seek to end of file

      break; // As of now, we only allow one output file since we don't separate stdout and stderr.
    }
  }

  PROCESS_INFORMATION pi;
  if (!CreateProcessA(nullptr, lpCmdLine, nullptr, nullptr, /*bInheritHandles=*/TRUE, CREATE_NO_WINDOW, nullptr, nullptr, &si, &pi)) {
    show_assert("Got error 0x%X when trying to run\n%s", HRESULT_FROM_WIN32(GetLastError()), lpCmdLine);
    return GetLastError();
  }

  constexpr DWORD bufferSize = 5'000; // 5 KB or so
  CHAR buffer[bufferSize] = {'\0'};
  DWORD exitCode = 0;

  do {
    // If there's a logfile, read while the process is running
    if (logFile) {
      DWORD bytesRead = 0;
      while ((bytesRead = ReadPipe(pipe_out, buffer, bufferSize)) > 0) {
        WriteFile(logFile, buffer, bytesRead, /*lpNumberOfBytesWritten=*/nullptr, /*lpOverlapped=*/nullptr);
      }
    }

    WaitForSingleObject(pi.hProcess, /*dwMilliseconds=*/100);
    GetExitCodeProcess(pi.hProcess, &exitCode);
  } while (exitCode == STILL_ACTIVE);

  // Read any trailing data (written at/near process end), or read the entire data (if we had no logfile).
  DWORD bytesRead = 0;
  while ((bytesRead = ReadPipe(pipe_out, buffer, bufferSize)) > 0) {
    if (logFile) {
      WriteFile(logFile, buffer, bytesRead, /*lpNumberOfBytesWritten=*/nullptr, /*lpOverlapped=*/nullptr);
    }
  }
  if (exitCode != 0) show_assert("Process failed with code %d\n%s", exitCode, buffer);

  // cleanup that's probably not needed
  if (logFile) CloseHandle(logFile);
  CloseHandle(pi.hProcess);
  CloseHandle(pi.hThread);
  CloseHandle(pipe_in);
  CloseHandle(pipe_out);
  return exitCode;
}
