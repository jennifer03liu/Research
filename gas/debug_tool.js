/**
 * 進階除錯工具：找出哪一筆 T2 回應沒有對應到 Tracking_Log
 */
function findMissingSubmission() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheetT2 = ss.getSheetByName(CONFIG.SHEET_NAME_PHASE2);
    const sheetLog = ss.getSheetByName(CONFIG.SHEET_NAME_TRACKING_LOG);

    if (!sheetT2 || !sheetLog) { console.error("找不到工作表"); return; }

    const t2Data = sheetT2.getDataRange().getValues();
    const logData = sheetLog.getDataRange().getValues();

    console.log(`T2 資料總筆數: ${t2Data.length - 1}`);
    console.log(`Log 資料總筆數: ${logData.length - 1}`);

    // 1. 建立 Tracking_Log 的索引 (已填寫名單)
    // Key: Email (小寫), Value: Row Index
    const logMap = new Map();
    // 同時建立 MatchID 索引作為備用
    const logMatchIdMap = new Map();

    for (let i = 1; i < logData.length; i++) {
        const row = logData[i];
        // 檢查是否已填寫 (F欄 Index 5)
        // 注意：有些可能是手動刪除日期但代表已填寫？這裡嚴格檢查 F 欄是否有值
        const isFilled = (row[5] && String(row[5]).trim() !== "");

        if (isFilled) {
            const email = String(row[2]).trim().toLowerCase();
            const matchId = String(row[3]).replace(/\D/g, ""); // 只留數字

            if (email) logMap.set(email, i + 1);
            if (matchId) logMatchIdMap.set(matchId, i + 1);
        }
    }

    console.log(`Log 中已標記完成的 Email 數量: ${logMap.size}`);

    // 2. 逐筆檢查 T2 回應
    const headers = t2Data[0];

    // [修正] 依照使用者回報指定欄位
    // AO 欄 = Index 40
    let colEmailIdx = 40;
    // AN 欄 = Index 39 (生日+手機)
    let colMatchIdIdx = 39;

    console.log(`使用指定欄位索引 - Email: ${colEmailIdx} (AO), 配對編號: ${colMatchIdIdx} (AN)`);

    const missingList = [];

    // 新增：檢查 T2 內部是否有重複填寫
    const seenEmails = new Map(); // Key: Email, Value: Row Index
    const duplicates = [];

    for (let i = 1; i < t2Data.length; i++) {
        const row = t2Data[i];
        // 安全檢查
        const rawEmail = (row[colEmailIdx] !== undefined) ? row[colEmailIdx] : "";
        const email = String(rawEmail).trim().toLowerCase();

        // 檢查重複
        if (email && seenEmails.has(email)) {
            duplicates.push({
                email: email,
                originalRow: seenEmails.get(email),
                duplicateRow: i + 1
            });
        } else if (email) {
            seenEmails.set(email, i + 1);
        }

        let matchId = "";
        if (colMatchIdIdx > -1) {
            const rawMatchId = (row[colMatchIdIdx] !== undefined) ? row[colMatchIdIdx] : "";
            matchId = String(rawMatchId).replace(/\D/g, "");
        }

        // 檢查 1: Email 是否存在於已完成名單？
        let found = logMap.has(email);

        // 檢查 2: 若 Email 沒找到，試試看 Match ID
        if (!found && matchId) {
            found = logMatchIdMap.has(matchId);
            if (found) console.log(`Row ${i + 1} Email 不符但 MatchID 由此找回: ${email} / ${matchId}`);
        }

        if (!found) {
            missingList.push({
                row: i + 1,
                email: email,
                matchId: matchId,
                timestamp: row[0]
            });
        }
    }

    // 輸出重複填寫者
    if (duplicates.length > 0) {
        console.log("------------------------------------------------");
        console.log(`發現 ${duplicates.length} 筆 重複填寫 (同一人填多次)：`);
        duplicates.forEach(d => {
            console.log(`Email: ${d.email} | 出現在 Row ${d.originalRow} 和 Row ${d.duplicateRow}`);
        });
        console.log("👉 這就是原因！重複填寫會覆蓋 Log 紀錄，導致 Log 總數比 回應總數少。");
    } else {
        console.log("沒有發現重複填寫 (根據 Email)。");
    }

    // 3. 輸出原本的遺漏檢查結果
    if (missingList.length > 0) {
        console.log("------------------------------------------------");
        console.log(`發現 ${missingList.length} 筆 T2 回應 未被標記為完成：`);
        missingList.forEach(m => {
            console.log(`[T2 Row ${m.row}] Time: ${m.timestamp} | Email: ${m.email} | MatchID: ${m.matchId}`);
        });
        console.log("------------------------------------------------");
        console.log("可能原因：");
        console.log("1. Tracking_Log 中沒有這個人 (UID/Email 都不對)");
        console.log("2. Tracking_Log 中有這個人，但 F 欄是空的 (程式寫入失敗或被清空)");
    } else {
        console.log("檢查完畢，T2 的每一筆回應都有對應到 Log 中的完成紀錄。");
    }
}
