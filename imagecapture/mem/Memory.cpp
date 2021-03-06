#include "pch.h"
#include "Memory.h"
#include <psapi.h>
#include <tlhelp32.h>
#include <iostream>

int main(int argc, char** argv) {
	Memory memory = Memory("witness64_d3d11.exe");
	if (strcmp(argv[1], "pos") == 0) {
		if (argc == 5) {
			memory.SetPos(strtof(argv[2], nullptr), strtof(argv[3], nullptr), strtof(argv[4], nullptr));
		} else {
			std::vector<float> pos = memory.GetPos();
			std::cout << pos[0] << " " << pos[1] << " " << pos[2] << std::endl;
		}
	} else if (strcmp(argv[1], "angle") == 0) {
		if (argc == 4) {
			memory.SetAngle(strtof(argv[2], nullptr), strtof(argv[3], nullptr));
		} else {
			std::vector<float> angle = memory.GetAngle();
			std::cout << angle[0] << " " << angle[1] << std::endl;
		}
	} else if (strcmp(argv[1], "noclip") == 0) {
		if (argc == 3) {
			memory.SetNoclip(strcmp(argv[2], "1") == 0);
		} else {
			bool noclip = memory.GetNoclip();
			std::cout << (noclip ? "1" : "0") << std::endl;
		}
	}
}

#undef PROCESSENTRY32
#undef Process32Next

Memory::Memory(const std::string& processName) {
	// First, get the handle of the process
	PROCESSENTRY32 entry;
	entry.dwSize = sizeof(entry);
	HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
	while (Process32Next(snapshot, &entry)) {
		if (processName == entry.szExeFile) {
			_handle = OpenProcess(PROCESS_ALL_ACCESS, FALSE, entry.th32ProcessID);
			if (!_handle) {
				std::cerr << "Couldn't find " << processName.c_str() << ". Is it open?" << std::endl;
				exit(EXIT_FAILURE);
			}
			break;
		}
	}

	// Next, get the process base address
	DWORD numModules;
	std::vector<HMODULE> moduleList(1024);
	EnumProcessModulesEx(_handle, &moduleList[0], static_cast<DWORD>(moduleList.size()), &numModules, 3);

	std::string name(64, 0);
	for (DWORD i = 0; i < numModules / sizeof(HMODULE); i++) {
		GetModuleBaseNameA(_handle, moduleList[i], &name[0], sizeof(name));

		// TODO: Filling with 0s still yeilds name.size() == 64...
		if (strcmp(processName.c_str(), name.c_str()) == 0) {
			_baseAddress = (uintptr_t)moduleList[i];
			break;
		}
	}
	if (_baseAddress == 0) {
		std::cerr << "Couldn't find base address!" << std::endl;
		exit(EXIT_FAILURE);
	}
}

Memory::~Memory() {
	CloseHandle(_handle);
}

std::vector<float> Memory::GetAngle() {
	return ReadData<float>(ANGLE_OFFSET, 2);
}

void Memory::SetAngle(float theta, float phi) {
	WriteData<float>(ANGLE_OFFSET, {theta, phi});
}

std::vector<float> Memory::GetPos() {
	return ReadData<float>(POS_OFFSET, 3);
}

void Memory::SetPos(float x, float y, float z) {
	WriteData<float>(POS_OFFSET, {x, y, z});
}

bool Memory::GetNoclip() {
	return ReadData<int>(NOCLIP_OFFSET, 1)[0] == 1;
}

void Memory::SetNoclip(bool enabled) {
	WriteData<int>(NOCLIP_OFFSET, {enabled ? 1 : 0});
}

// Private methods

void Memory::ThrowError() {
    wchar_t message[256];
    FormatMessageW(4096, NULL, GetLastError(), 1024, message, 256, NULL);
	std::cerr << message << std::endl;
    exit(EXIT_FAILURE);
}

template<class T>
std::vector<T> Memory::ReadData(int offset, int numItems) {
	std::vector<T> data;
	data.resize(numItems);
    if (!ReadProcessMemory(_handle, (LPVOID)(_baseAddress + offset), &data[0], sizeof(T) * numItems, NULL)) {
        ThrowError();
    }
	return data;
}

template <class T>
void Memory::WriteData(int offset, const std::vector<T>& data) {
    if (!WriteProcessMemory(_handle, (LPVOID)(_baseAddress + offset), &data[0], sizeof(T) * data.size(), NULL)) {
		ThrowError();
    }
}
