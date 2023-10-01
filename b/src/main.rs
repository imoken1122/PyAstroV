extern crate chrono;

use chrono::{DateTime, Utc, TimeZone};

fn format_jst_time_with_milliseconds(datetime: DateTime<Utc>) -> String {
    // タイムゾーンを日本時間に変更
    let jst = chrono::FixedOffset::east(9 * 3600); // 日本標準時のオフセット

    // 指定されたUTC時刻を日本時間に変換
    let jst_time = datetime.with_timezone(&jst);

    // 日本時間をミリ秒まで文字列にフォーマット
    let formatted_time = jst_time.format("%Y-%m-%d %H:%M:%S%.3f").to_string();

    formatted_time
}

fn main() {
    // 現在のUTC時刻を取得
    let utc_now: DateTime<Utc> = Utc::now();

    // format_jst_time_with_millisecondsメソッドを使用して日本時間にフォーマット
    let jst_time_str = format_jst_time_with_milliseconds(utc_now);

    println!("現在の日本時間 (ミリ秒まで): {}", jst_time_str);
}
