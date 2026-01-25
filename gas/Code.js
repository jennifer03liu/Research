/**
 * =========================================================================
 *  職涯研究自動化腳本 (GAS_Automation.gs / Code.js)
 *  功能 1: 接收 T1 問卷頁面傳來的 UID (doPost) -> 記錄到受試者名單
 *  功能 2: 處理 T1 表單提交 (Trigger) -> 同步到 Tracking_Log
 *  功能 3: 每天檢查是否滿 28 天，自動寄送 T2 問卷連結
 *  功能 4: 處理 T2 表單提交 (Trigger) -> 回寫完成時間與時長
 * =========================================================================
 * 
 * 使用說明：
 * 1. 在 Google Sheet 開啟「擴充功能」->「Apps Script」。
 * 2. 將此程式碼全部複製貼上，覆蓋原本內容。
 * 3. 修改下方的 CONFIG 設定區。
 * 4. 部署為 Web App (用於接收 T1 點擊)。
 * 5. 設定觸發條件 (Triggers):
 *    - processFormSubmissions -> 來自試算表 -> 提交表單時 (使用 onFormSubmitRouter)
 *    - sendT2FollowUpEmails -> 時間驅動 -> 每天/每小時
 */

// ================= CONFIGURATION (請修改這裡) =================
const CONFIG = {
  // 1. Google Sheet 分頁名稱
  SHEET_NAME_TRACKING_LOG: "Tracking_Log",      // [改名] T1_Log -> Tracking_Log (發信名單)
  SHEET_NAME_PARTICIPANT: "受試者名單",          // [新增] 點擊紀錄
  SHEET_NAME_PHASE1: "第一階段",                // [新增] T1 表單回應
  SHEET_NAME_PHASE2: "第二階段",                // [改名] T2 表單回應 (使用者已改名)

  // 2. 欄位標題關鍵字 (用於自動尋找)
  HEADER_ATTN: "這題請選擇「4」",              // 檢核題關鍵字
  HEADER_EMAIL: "聯絡資訊",                    // Email 關鍵字 (修改為匹配 "13. 聯絡資訊與配對確認")
  HEADER_PHONE: "手機末3碼",                  // 手機欄位關鍵字
  HEADER_BIRTH: "出生月份日期",                // 生日欄位關鍵字 (若分開)
  HEADER_CUSTOM_UID: "Custom_UID",           // 用於 Phase 1 的 BF 欄位名稱 (若沒有標題預設找最後一欄)

  // T2 相關
  HEADER_T2_VERIFY: "配對",                   // T2 的 驗證碼/配對編號 欄位關鍵字

  // 3. T2 問卷產生器網址
  T2_REDIRECT_URL: "https://jennifer03liu.github.io/Research/T2_Survey_Redirect.html",

  // T1 問卷設定 (用於記錄完整網址)
  T1_FORM_URL: "https://docs.google.com/forms/d/e/1FAIpQLScfi6G7InS212ZMIeu5Yx5rEO1OX0bWKGSZo-iVnm1OWQeCPQ/viewform",
  T1_ENTRY_ID: "entry.701942597",

  // 4. Email 寄件設定
  EMAIL_SUBJECT: "【問卷填寫邀請】第二階段 - 職涯發展研究",
  EMAIL_SENDER_NAME: "劉人瑄Jennifer(國立中山大學人管所學術研究)",
  ADMIN_EMAIL: "jennifer03liu@gmail.com,jenniferliu@trendforce.com" // [新增] 用於接收錯誤通知
};

// =============================================================

/**
 * 統一入口：處理所有表單提交 (因為 GAS 一個專案只能綁一個 onFormSubmit Trigger 比較好管理)
 * 請設定 Trigger: 執行 `onFormSubmitRouter` -> 來自試算表 -> 提交表單時
 */
function onFormSubmitRouter(e) {
  // 如果是手動執行 debugLastRow，可能沒有 e，所以在 debugLastRow 會手動傳
  if (!e || !e.range) return;

  const sheet = e.range.getSheet();
  const name = sheet.getName();

  if (name === CONFIG.SHEET_NAME_PHASE1) {
    processPhase1Submit(e);
  } else if (name === CONFIG.SHEET_NAME_PHASE2) {
    processPhase2Submit(e);
  }
}

/**
 * 功能 1: 接收連結點擊 (doPost)
 * 寫入「受試者名單」(僅記錄點擊)
 */
function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000);

  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME_PARTICIPANT);
    if (!sheet) throw new Error("找不到分頁: " + CONFIG.SHEET_NAME_PARTICIPANT);

    let data;
    try {
      data = JSON.parse(e.postData.contents);
    } catch (err) {
      data = {};
    }

    const uid = data.code || Utilities.getUuid();
    const timestamp = new Date();

    // 產生完整 T1 問卷連結
    // 格式: FormURL?usp=pp_url&entry.xxxx=uid
    const recordLink = `${CONFIG.T1_FORM_URL}?usp=pp_url&${CONFIG.T1_ENTRY_ID}=${uid}`;

    // 寫入: [A:時間, B:姓名(空), C:UID, D:連結, E:回填時間(空)]
    sheet.appendRow([timestamp, "", uid, recordLink, ""]);

    return ContentService.createTextOutput(JSON.stringify({ status: "success", uid: uid }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

/**
 * 輔助函式：找標題所在的 index (0-based)
 */
function findHeaderIndex(headers, keyword) {
  if (!headers) return -1;
  return headers.findIndex(h => h && String(h).indexOf(keyword) > -1);
}

/**
 * 功能 2: 處理 T1 表單提交 (被 Router 呼叫)
 */
function processPhase1Submit(e) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) return;

  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheetPhase1 = ss.getSheetByName(CONFIG.SHEET_NAME_PHASE1);
    const sheetTracking = ss.getSheetByName(CONFIG.SHEET_NAME_TRACKING_LOG);

    if (!sheetPhase1 || !sheetTracking) {
      console.error("找不到工作表 (Phase 1 or Tracking)");
      MailApp.sendEmail(CONFIG.ADMIN_EMAIL, "GAS 自檢錯誤", `找不到工作表: ${CONFIG.SHEET_NAME_PHASE1} 或 ${CONFIG.SHEET_NAME_TRACKING_LOG}`);
      return;
    }

    let range = e.range;
    let rowIdx = range.getRow();

    // 防呆：如果是首列標題列，不處理
    if (rowIdx === 1) return;

    const headers = sheetPhase1.getRange(1, 1, 1, sheetPhase1.getLastColumn()).getValues()[0];
    const rowValues = sheetPhase1.getRange(rowIdx, 1, 1, sheetPhase1.getLastColumn()).getValues()[0];

    // Debug Log
    console.log(`Processing Phase 1 Row ${rowIdx}`);

    // 1. 固定 Custom UID
    let colUidIdx = findHeaderIndex(headers, CONFIG.HEADER_CUSTOM_UID);
    // 若找不到標題，嘗試找 "BF" (第58欄 -> index 57) 
    if (colUidIdx === -1) colUidIdx = 57;

    const cellUid = sheetPhase1.getRange(rowIdx, colUidIdx + 1);
    let uidVal = cellUid.getValue();

    if (String(uidVal).trim() === "") {
      cellUid.setFormula('=REPLACE(DEC2HEX(RANDBETWEEN(0, 4294967295), 8), 5, 0, "-")');
      SpreadsheetApp.flush();
      uidVal = cellUid.getValue();
    }

    if (cellUid.getFormula() !== "") {
      cellUid.setValue(uidVal);
    }

    // 2. 篩選
    let colEmailIdx = findHeaderIndex(headers, CONFIG.HEADER_EMAIL);
    const email = (colEmailIdx > -1) ? rowValues[colEmailIdx] : "";

    let colAttnIdx = findHeaderIndex(headers, CONFIG.HEADER_ATTN);
    const attnVal = (colAttnIdx > -1) ? rowValues[colAttnIdx] : "4";

    // Log screening values
    console.log(`Email found: ${email}, Attn Check Val: ${attnVal}`);

    if (!email || String(attnVal).trim() !== "4") {
      console.log(`Row ${rowIdx} 篩選未通過`);
      return;
    }

    // 3. 檢查重複與寫入
    const trackingData = sheetTracking.getDataRange().getValues();
    const existUids = trackingData.map(r => r[1]); // Col B in Tracking = UID
    if (existUids.includes(uidVal)) {
      console.log(`UID ${uidVal} 已存在`);
      return;
    }

    // 組合 Match ID (修正：避免同一個欄位合併兩次)
    let colPhoneIdx = findHeaderIndex(headers, CONFIG.HEADER_PHONE);
    let colBirthIdx = findHeaderIndex(headers, CONFIG.HEADER_BIRTH);
    let matchId = "";

    if (colPhoneIdx > -1 && colPhoneIdx === colBirthIdx) {
      // 代表是同一欄 (合併題)
      matchId = String(rowValues[colPhoneIdx]).replace(/\D/g, "");
    } else {
      // 分開的欄位
      let phoneStr = (colPhoneIdx > -1) ? String(rowValues[colPhoneIdx]) : "";
      let birthStr = (colBirthIdx > -1) ? String(rowValues[colBirthIdx]) : "";
      matchId = (birthStr + phoneStr).replace(/\D/g, "");
    }

    // 寫入 Tracking_Log
    const timestamp = rowValues[0] || new Date(); // 若抓不到時間就用現在時間
    sheetTracking.appendRow([
      timestamp,
      uidVal,
      email,
      matchId,
      false, // E: Sent
      "",    // F: T2 Time
      "",    // G: Duration
      ""     // H: Error
    ]);
    console.log("Successfully synced to Tracking_Log");

  } catch (e) {
    console.error("T1 Process Error: " + e.toString());
    MailApp.sendEmail(CONFIG.ADMIN_EMAIL, "GAS 錯誤: processPhase1Submit", e.toString());
  } finally {
    lock.releaseLock();
  }
}

/**
 * 功能 3: 每日寄信 (優化版)
 */
function sendT2FollowUpEmails() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME_TRACKING_LOG);
  if (!sheet) return;

  // 優化 1: 迴圈外只抓一次額度
  let quota = MailApp.getRemainingDailyQuota();
  if (quota < 10) {
    MailApp.sendEmail(CONFIG.ADMIN_EMAIL, "GAS 額度警報", `今日額度不足 (${quota})，停止寄送。`);
    return;
  }

  const data = sheet.getDataRange().getValues();
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  // i=1 start
  for (let i = 1; i < data.length; i++) {
    // 優化 2: 用本地變數判斷，不重複呼叫 API
    if (quota <= 1) {
      console.log(`今日額度用盡 (剩餘 ${quota})，停止發送。目前停在第 ${i} 筆資料，下次排程會接續執行。`);
      break;
    }

    const row = data[i];

    // 優化 3: 快速過濾無效列 (大幅節省時間)
    if (!row[0] || !row[1] || !row[2]) continue;

    const t1Date = new Date(row[0]);
    const uid = row[1];
    const email = row[2];
    const matchId = row[3];
    const isSent = row[4]; // E

    if (!t1Date || isNaN(t1Date.getTime())) continue;
    if (String(isSent).toLowerCase() === "true") continue;

    const t1PureDate = new Date(t1Date);
    t1PureDate.setHours(0, 0, 0, 0);
    const diffTime = today - t1PureDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays >= 28) {
      const link = `${CONFIG.T2_REDIRECT_URL}?uid=${uid}&email=${encodeURIComponent(email)}&verify=${matchId}`;

      try {
        MailApp.sendEmail({
          to: email,
          subject: CONFIG.EMAIL_SUBJECT,
          name: CONFIG.EMAIL_SENDER_NAME,
          htmlBody: `
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
              <h3 style="color: #2c3e50;">職涯發展研究 - 第二階段問卷 (2/3)｜加油，填完這次旅程即過半！</h3>
              <p>親愛的職場夥伴，歡迎回來！</p>
              <p>再次感謝您參與這項關於職涯發展的長期研究。</p>
              
              <p><span style="background-color: #fef08a; font-weight: bold; padding: 2px 5px;">本研究共需完整填答三次。這是第 2 次，完成本次問卷後，再完成 28 天後的最後一次追蹤，即具備 500元 7-11 禮券 抽獎資格！</span></p>
              <p>此次填答約需 10-15 分鐘，為了能準確連結您的資料，請務必使用與上次相同的 <strong>Email</strong> 與 <strong>手機末三碼/生日月日共七碼</strong> 驗證。</p>
              <p>匿名與保密：本問卷採嚴格匿名制，所有數據僅供學術統計分析使用，絕不對外公開或用於任何商業用途，請您依照真實感受安心填答。</p>
              <br>
              <div style="text-align: center;">
                <a href="${link}" style="background-color: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                  填寫第二階段問卷
                </a>
              </div>
              <br>
              <p style="font-size: 14px; color: #666;">(本連結已包含您的專屬辨識碼，點擊後請直接填寫，勿修改「配對編號」欄位)</p>
              <p style="font-size: 14px; color: #666;">若按鈕無法點擊，請複製連結：<br>${link}</p>
              <br>
              <p>謝謝您的填寫，並祝福您馬年行大運!</p>
              <br>
              <div style="text-align: right;">
                國立中山大學人力資源管理研究所<br>
                指導教授：王豫萱 博士<br>
                研究生：劉人瑄 敬上
              </div>
            </div>
          `
        });

        // Update
        sheet.getRange(i + 1, 5).setValue(true);
        sheet.getRange(i + 1, 8).setValue(""); // Clear Error
        console.log(`Sent: ${email}`);

        // 成功發送才扣除
        quota--;

      } catch (e) {
        console.error(`Failed ${email}: ${e}`);
        sheet.getRange(i + 1, 8).setValue("失敗: " + e.toString());
      }
    }
  }
}

/**
 * 功能 4: 處理 T2 表單提交 (被 Router 呼叫)
 * 三選一比對 + 計算 Duration
 */
function processPhase2Submit(e) {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(30000)) return;

  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheetT2 = ss.getSheetByName(CONFIG.SHEET_NAME_PHASE2);
    const sheetTracking = ss.getSheetByName(CONFIG.SHEET_NAME_TRACKING_LOG);

    if (!sheetT2 || !sheetTracking) {
      console.log("找不到 T2 回應表或 Tracking_Log");
      return;
    }

    let range = e.range;
    let rowIdx = range.getRow();
    const rowValues = sheetT2.getRange(rowIdx, 1, 1, sheetT2.getLastColumn()).getValues()[0];
    const headers = sheetT2.getRange(1, 1, 1, sheetT2.getLastColumn()).getValues()[0];

    console.log(`Processing T2 Row ${rowIdx}`);

    // 1. 找 Email 欄位
    let colEmailIdxT2 = findHeaderIndex(headers, CONFIG.HEADER_EMAIL);
    if (colEmailIdxT2 === -1) colEmailIdxT2 = findHeaderIndex(headers, "Email"); // Fallback
    const emailT2 = (colEmailIdxT2 > -1) ? rowValues[colEmailIdxT2] : "";

    // 2. 找驗證碼/配對碼 欄位
    let colVerifyIdx = findHeaderIndex(headers, CONFIG.HEADER_T2_VERIFY);
    const verifyCode = (colVerifyIdx > -1) ? rowValues[colVerifyIdx] : rowValues[2]; // Fallback to C

    console.log(`T2 Data - Email: ${emailT2}, VerifyCode: ${verifyCode}`);

    // 解析 Verify Code: UID_Timestamp
    let uidFromCode = "";
    let clickTimestamp = 0;

    if (verifyCode && String(verifyCode).includes("_")) {
      const parts = String(verifyCode).split("_");
      uidFromCode = parts[0];
      clickTimestamp = Number(parts[1]);
    } else if (verifyCode) {
      // 如果使用者可能有刪掉後面的 _Timestamp，只留 UID
      uidFromCode = String(verifyCode).split("_")[0];
    }

    // 計算 Duration
    const submitTime = new Date(rowValues[0]); // A欄
    let durationSec = 0;
    if (clickTimestamp > 0) {
      durationSec = (submitTime.getTime() / 1000) - clickTimestamp;
    }

    // 格式化 Duration (例如: 5分30秒)
    const mins = Math.floor(durationSec / 60);
    const secs = Math.floor(durationSec % 60);
    const durationStr = `${mins}分${secs}秒`;

    // 三合一比對 Tracking_Log
    const trackingData = sheetTracking.getDataRange().getValues();
    // Tracking: A:Time, B:UID, C:Email, D:MatchID ...

    let matchedRowIndex = -1;

    for (let i = 1; i < trackingData.length; i++) {
      const tRow = trackingData[i];
      const tUid = String(tRow[1]);
      const tEmail = String(tRow[2]);

      let isMatch = false;
      // 比對 UID
      if (uidFromCode && tUid && uidFromCode.trim() === tUid.trim()) isMatch = true;
      // 比對 Email
      if (!isMatch && emailT2 && tEmail && emailT2.trim() === tEmail.trim()) isMatch = true;

      if (isMatch) {
        matchedRowIndex = i + 1; // 1-based index
        // 檢查是否已經填寫過了？目前邏輯是重複填寫會覆蓋更新
        console.log(`T2 Match Found at Row ${matchedRowIndex}`);
        break;
      }
    }

    if (matchedRowIndex > -1) {
      // F: T2完成時間, G: Duration
      sheetTracking.getRange(matchedRowIndex, 6).setValue(submitTime);
      sheetTracking.getRange(matchedRowIndex, 7).setValue(durationStr);
      console.log(`Updated Tracking_Log Row ${matchedRowIndex} with Duration ${durationStr}`);
    } else {
      console.log("No match found in Tracking_Log");
    }

  } catch (e) {
    console.error("T2 Process Error: " + e.toString());
    MailApp.sendEmail(CONFIG.ADMIN_EMAIL, "GAS 錯誤: processPhase2Submit", e.toString());
  } finally {
    lock.releaseLock();
  }
}

/**
 * 除錯專用：指定列數測試 Phase 1
 */
function debugSpecificRow() {
  const targetRow = 479;
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.SHEET_NAME_PHASE1);
  if (!sheet) return;

  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  console.log("P1 Header: " + JSON.stringify(headers));

  console.log(`Testing P1 Row: ${targetRow}...`);
  const e = {
    range: sheet.getRange(targetRow, 1, 1, sheet.getLastColumn()),
    source: ss
  };
  processPhase1Submit(e);
}

/**
 * 除錯專用：指定列數測試 Phase 2
 * 請先確認 SHEET_NAME_PHASE2 名稱正確，並將 targetRow 改為您要測的 T2 回應列
 */
function debugT2SpecificRow() {
  const targetRow = 2; // <--- T2 回應的第幾列
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(CONFIG.SHEET_NAME_PHASE2);

  if (!sheet) {
    console.log("找不到 T2 Sheet: " + CONFIG.SHEET_NAME_PHASE2);
    return;
  }

  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  console.log("T2 Header: " + JSON.stringify(headers));

  console.log(`Testing T2 Row: ${targetRow}...`);
  const e = {
    range: sheet.getRange(targetRow, 1, 1, sheet.getLastColumn()),
    source: ss
  };
  processPhase2Submit(e);
}
