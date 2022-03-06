#define _CRT_SECURE_NO_WARNINGS 1
#include <cstdlib>

#define WIN32_LEAN_AND_MEAN
#include <windows.h>

int APIENTRY WinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance, LPSTR lpCmdLine, int nCmdShow) {
  WinExec(lpCmdLine, SW_HIDE);
}
