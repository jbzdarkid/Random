#include "HPRecType.h"
#include "Util.h"
#include <atomic>
#include <map>

// Thread-safe map (from Andrei Alexandrescu and Maged Michael)
// http://erdani.com/publications/cuj-2004-12.pdf

template<class K, class V>
class WRRMMap {
public:
    using Map = std::map<K, V>;

    void Update(const K& key, const V& value) {
        Map* pNew = nullptr;
        Map* pOld = nullptr;
        do {
            pOld = (Map*)pMap.load();
            if (pNew) delete pNew;
            if (pOld) {
                pNew = new Map(*pOld);
            } else {
                pNew = new Map();
            }
            (*pNew)[key] = value;
            // Note that std::atomic *cannot* guarantee the atomicity of this swap
            // with regards to the contents of the std::maps. All it can guarantee is that
            // the pointers are what expect -- which is why we have to cast the std::maps
            // down to void* before attemping the swap.
        } while (!CAS(pMap, (void*)pOld, (void*)pNew));
        HazardPointer::Retire(pOld);
    }

    bool Lookup(const K& key, V& outValue) const {
        HazardPointer pRec = LoadMap();
        Map* map = (Map*)pRec;
        if (map == nullptr) return false;

        auto search = map->find(key);
        if (search != map->end()) {
            outValue = search->second;
            return true;
        }
        return false;
    }

    size_t Size() const {
        HazardPointer pRec = LoadMap();
        Map* map = (Map*)pRec;
        return (map != nullptr ? map->size() : 0);
    }

private:
    std::atomic<void*> pMap = nullptr;

    // Note: The HazardPointer must be retained until we're done acting on it.
    // Thus, we return a HazardPointer rather than a Map*, to force the
    // enclosing scope to keep the object alive. That said, this isn't really
    // a guarantee. Callers should still be careful.
    HazardPointer LoadMap() const {
        HazardPointer hazardPointer;
        do {
            hazardPointer = pMap.load();
            // Although it may seem extraneous to check the map again, we can
            // potentially get interrupted after calling load, but before
            // assigning to the hazard pointer. In this case, we might think
            // we've acquired pMap, but in fact the object we're looking at
            // has been overwritten and freed, and we would be taking a dead
            // reference.
        } while (pMap.load() != hazardPointer);
        return std::move(hazardPointer);
    }
};
