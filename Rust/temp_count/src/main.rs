pub struct TempCountStruct {
    pub temperature: f32,
    pub count: i32
}

pub trait TempAvg {
    fn set(&self, temp: f32, cnt: i32);
    fn add(&self, temp: f32, cnt: i32);
    fn get(&self) -> f32;
}

impl TempCountStruct {
    fn set(temp: f32, cnt: i32) -> Self{
        Self {
            count: cnt,
            temperature: temp * (cnt as f32)
        }
    }
    fn init() -> Self{
        Self {
            count: 0,
            temperature: 0.0
        }
    }
    fn add(&mut self, temp: f32, cnt: i32) {
        self.count += cnt;
        self.temperature += temp * (cnt as f32);
    }

    fn get(&self) -> f32 {
        return self.temperature / (self.count as f32)
    }
}

fn main() {
    println!("Hello, world!");
}


#[test]
fn avg_1() {
    let mut t1 = TempCountStruct::init();
    t1.add(14.0, 10);
    t1.add(12.0, 10);
    assert_eq!(13.0, t1.get());
}
#[test]
fn avg_2() {
    let mut t1 = TempCountStruct::set(10.0, 20);
    t1.add(14.0, 10);
    t1.add(12.0, 10);
    assert_eq!(11.5, t1.get());
}
#[test]
fn avg_3() {
    let mut t1 = TempCountStruct::init();
    for i in 0..100 {
        t1.add(i as f32, i * 7 % 13);
    }
    assert_eq!(49.85932, t1.get());
}