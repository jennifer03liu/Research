/**
 * 一次性工具：為已存在的資料補上連結
 * 執行即會將所有 Tracking_Log 的 J 欄填上連結
 */
function backfillLinks() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME_TRACKING_LOG);
    if (!sheet) return;

    const data = sheet.getDataRange().getValues();
    // 建立一個與 row 數量相同的空陣列來存連結，避免逐行寫入太慢
    const links = [];

    for (let i = 1; i < data.length; i++) {
        const row = data[i];
        const uid = row[1];
        const email = row[2];
        let matchId = String(row[3]).replace(/^'/, ""); // 去除可能存在的單引號

        // 補零邏輯同步
        if (matchId.length === 6) matchId = "0" + matchId;

        if (uid && email && matchId) {
            const link = `${CONFIG.T2_REDIRECT_URL}?uid=${uid}&email=${encodeURIComponent(email)}&verify=${matchId}`;
            links.push([link]);
        } else {
            links.push([""]); // 若資料不完整則填空
        }
    }

    // 一次寫入 J 欄 (第 2 列開始，長度為 links 數量，寬度為 1)
    if (links.length > 0) {
        sheet.getRange(2, 10, links.length, 1).setValues(links);
        console.log("Backfill Completed!");
    }
}
