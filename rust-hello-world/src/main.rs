use std::io::Result as R;
type Map = std::collections::HashMap<String, String>;

fn main() -> R<()> {
    let mut args = std::env::args().skip(1);
    let key   = args.next().unwrap_or_default();
    let value = args.next().unwrap_or_default();
    
    let mut db = Database::create()?;
    db.insert(key, value);
    db.write()?;

    Ok(())
}

struct Database {
    map: Map
}

impl Database {
    fn create() -> R<Database> {
        let contents = std::fs::read_to_string("kv.db")?;
        let mut map = Map::new();
        for line in contents.lines() {
            let mut kv = line.split("=");
            let k = kv.next().unwrap_or_default().to_string();
            let v = kv.next().unwrap_or_default().to_string();

            map.insert(k, v);
        }

        return Ok(Database {map: map});
    }

    fn insert(&mut self, key: String, value: String) {
        self.map.insert(key, value);
    }

    fn write(&self) -> R<()> {
        let mut contents = String::new();
        for (key, value) in &self.map {
            contents += &format!("{}={}\n", key, value);
        }
        return std::fs::write("kv.db", contents);
    }
}
