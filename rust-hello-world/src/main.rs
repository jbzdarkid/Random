use std::io::Result;

fn main() -> Result<()> {
    let mut args = std::env::args().skip(1);
    let key   = args.next().unwrap_or_default();
    let value = args.next().unwrap_or_default();
    
    write_db(key, value)?;

    Ok(())
}

fn write_db(key: String, value: String) -> Result<()> {
    return std::fs::write("kv.db", format!("{}={}", key, value));
}
