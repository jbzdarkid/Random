#pragma once
#include <atomic>

class HazardPointer final {
public:
    HazardPointer();
    HazardPointer(const HazardPointer& other) = delete; // Copy Constructor
    HazardPointer(HazardPointer&& other) noexcept; // Move Constructor

    ~HazardPointer();
    HazardPointer& operator=(const HazardPointer& other) = delete; // Copy Assignment
    HazardPointer& operator=(HazardPointer&& other) noexcept; // Move Assignment

    static void Retire(void* pOld);

    template<typename T>
    operator T() {
        return (T)hpRec->pHazard;
    }

    template<typename T>
    bool operator==(const T& other) const {
        return (T)hpRec->pHazard == other;
    }

    void operator=(void* value) {
        hpRec->pHazard = value;
    }

private:
    class HPRecType final {
    public:
        void* pHazard = nullptr;
        HPRecType* pNext = nullptr;
    };

    static void Scan();
    static std::atomic<HPRecType*> pHead;
    static std::atomic<int> listLen;

    std::atomic<bool> active = true;
    HPRecType* hpRec;
};

template<typename T>
bool operator!=(const T& lhs, const HazardPointer& rhs)
{
    return !(rhs == lhs);
}

template<typename T>
bool operator==(const T& lhs, const HazardPointer& rhs)
{
    return rhs == lhs;
}
