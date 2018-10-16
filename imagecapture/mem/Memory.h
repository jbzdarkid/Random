#pragma once
#include <vector>
#include <windows.h>

// https://github.com/erayarslan/WriteProcessMemory-Example
// http://stackoverflow.com/q/32798185
// http://stackoverflow.com/q/36018838
// http://stackoverflow.com/q/1387064
class Memory
{
public:
	Memory(const std::string& processName);
	~Memory();

	int ANGLE_OFFSET = 0x62D3BC;
	std::vector<float> GetAngle();
	void SetAngle(float theta, float phi);

	int POS_OFFSET = 0x62D490;
	std::vector<float> GetPos();
	void SetPos(float x, float y, float z);

	int NOCLIP_OFFSET = 0x62A598;
	bool GetNoclip();
	void SetNoclip(bool enabled);

private:
	void ThrowError();

	template<class T>
	std::vector<T> ReadData(int offset, int numItems);
	template <class T>
	void WriteData(int offset, const std::vector<T>& data);

	uintptr_t _baseAddress;
	HANDLE _handle;
};