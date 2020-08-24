#include "HPRecType.h"
#include "Util.h"
#include <set>
#include <vector>

using namespace std;

atomic<HazardPointer::HPRecType*> HazardPointer::pHead;
atomic<int> HazardPointer::listLen;

thread_local std::vector<void*> retiredList;

void HazardPointer::Retire(void* pOld) {
    retiredList.push_back(pOld);
    if (retiredList.size() >= 100) { // Maximum retired list size
        Scan();
    }
}

void HazardPointer::Scan() {
    // Stage 1: Scan the hazard pointers list, collecting all nonnull ptrs
    std::set<void*> hazardPointers;
    for (HazardPointer::HPRecType* head = HazardPointer::pHead.load(); head != nullptr; head = head->pNext) {
        if (head->pHazard) hazardPointers.insert(head->pHazard);
    }

    // Stage 2 (sort the list) isn't required when using std::set.

    // Stage 3: Search for them!
    for (auto it = retiredList.begin(); it != retiredList.end(); ) {
        if (hazardPointers.find(*it) != hazardPointers.end()) {
            delete *it;
            it = retiredList.erase(it);
        } else {
            ++it;
        }
    }
}

HazardPointer::HazardPointer() {
    // Try to reuse a retired HP record
    for (HazardPointer::HPRecType* p = pHead.load(); p != nullptr; p = p->pNext) {
        if (!CAS(active, false, true)) continue;
        hpRec = p;
        return;
    }

    // Else, increment the list length
    int oldLen;
    do {
        oldLen = listLen.load();
    } while (!CAS(listLen, oldLen, oldLen + 1));

    // Allocate a new HPRec, and push it on the front
    HazardPointer::HPRecType* p = new HazardPointer::HPRecType();
    HazardPointer::HPRecType* old = pHead.load();
    do {
        p->pNext = old;
    } while (!CAS(pHead, old, p));
    hpRec = p;
    return;
}

HazardPointer::HazardPointer(HazardPointer&& other) noexcept {
    std::exchange(hpRec, other.hpRec);
}

HazardPointer::~HazardPointer() {
    if (hpRec) {
        hpRec->pHazard = nullptr;
        active = false;
    }
}

HazardPointer& HazardPointer::operator=(HazardPointer&& other) noexcept {
    std::exchange(hpRec, other.hpRec);
    return other;
}
