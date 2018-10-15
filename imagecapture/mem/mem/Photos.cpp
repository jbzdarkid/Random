#include "pch.h"
#include "Memory.h"
#include <cmath>

void main()
{
	/*
	INPUT ip[2] = { 0 };

	ip[0].type = INPUT_KEYBOARD;
	ip[0].ki.wVk = VK_SNAPSHOT;

	ip[1] = ip[0];
	ip[1].ki.dwFlags |= KEYEVENTF_KEYUP;
	SendInput(2, ip, sizeof(INPUT));
	*/

	Memory memory("witness64_d3d11.exe");

	memory.SetNoclip(true);
	memory.SetAngle(0, -1.57079632679); // -pi/2

	// Loop through positions or something

}
