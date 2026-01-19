/**
 * =========================================================================
 *  職涯研究自動化腳本 (GAS_Automation.gs / Code.js)
 *  功能 1: 接收 T1 問卷頁面傳來的 UID (doPost)
 *  功能 2: 每天檢查是否滿 28 天，自動寄送 T2 問卷連結 (sendT2FollowUpEmails)
 * =========================================================================
 * 
 * 使用說明：
 * 1. 在 Google Sheet 開啟「擴充功能」->「Apps Script」。
 * 2. 將此程式碼全部複製貼上，覆蓋原本內容。
 * 3. 修改下方的 CONFIG 設定區 (填入您的網址、Sheet 名稱等)。
 * 4. 部署為 Web App (用於接收 T1 資料)。
 * 5. 設定觸發條件 (Triggers) -> 新增觸發條件 -> 執行 `sendT2FollowUpEmails` -> 時間驅動 -> 每天一次。
 */

// ================= CONFIGURATION (請修改這裡) =================

const CONFIG = {
  // 1. Google Sheet 分頁名稱
  SHEET_NAME_T1_LOG: "T1_Log",  // 存放 T1 點擊紀錄的分頁 (請自行建立)

  // 2. T2 問卷產生器網址 (GitHub Pages 那個)
  T2_REDIRECT_URL: "https://jennifer03liu.github.io/Research/T2_Survey_Redirect.html",

  // 3. Email 寄件設定
  EMAIL_SUBJECT: "【問卷邀請】職涯發展研究 - 第二階段問卷",
  EMAIL_SENDER_NAME: "國立中山大學人管所-劉人瑄"
};

// =============================================================

/**
 * 功能 1: 接收 HTML 傳來的資料 (doPost)
 * 對應 index.html 的 fetch(GAS_API_URL, ...)
 */
function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000);

  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME_T1_LOG);
    if (!sheet) throw new Error("找不到分頁: " + CONFIG.SHEET_NAME_T1_LOG);

    // 解析 JSON 資料
    const data = JSON.parse(e.postData.contents);
    const uid = data.code || "";      // T1 產生的 UUID
    const timestamp = new Date();     // 接收到的時間 (現在)

    // 寫入資料: [時間戳, UUID, 狀態]
    // 建議欄位順序: A:時間, B:UUID, C:Email(若有), D:手機(若有), E:T2已發送(系統用)
    // 注意: T1 index.html 只會傳 uid，所以 C, D 兩欄這時候是空的，後續需要您用 VLOOKUP 從問卷回應表補進去
    sheet.appendRow([timestamp, uid, "", "", "FALSE"]);

    return ContentService.createTextOutput(JSON.stringify({ status: "success" }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService.createTextOutput(JSON.stringify({ status: "error", message: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}

/**
 * 功能 2: 每日檢查是否滿 28 天，並寄送 Email
 * 請設定觸發條件: 每天早上 9:00 - 10:00 執行一次
 */
function sendT2FollowUpEmails() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(CONFIG.SHEET_NAME_T1_LOG);
  if (!sheet) return;

  const data = sheet.getDataRange().getValues();
  // 假設資料結構: 
  // Col A (0): T1填寫時間
  // Col B (1): UID
  // Col C (2): Email (⚠️重要：這欄需要您從問卷資料手動貼過來，或用VLOOKUP自動帶入)
  // Col D (3): 手機/驗證碼 (⚠️重要：同上)
  // Col E (4): T2已發送 (TRUE/FALSE)

  const today = new Date();
  // 清除時間部分，只比對日期
  today.setHours(0, 0, 0, 0);

  // 從第 2 行開始跑 (跳過標題)
  for (let i = 1; i < data.length; i++) {
    const row = data[i];
    const t1Date = new Date(row[0]);
    const uid = row[1];
    const email = row[2];
    const verifySum = row[3]; // 生日+手機合併碼
    const isSent = row[4];

    // 基本檢查
    if (!t1Date || isNaN(t1Date.getTime())) continue; // 日期無效跳過
    if (isSent === true || isSent === "TRUE") continue; // 已經寄過就跳過
    if (!email || !uid) continue; // 資料不全跳過 (如果 Email 空白就不寄)

    // 計算日數差
    // 設定 t1Date 的時間為 0 點，純算天數
    const t1PureDate = new Date(t1Date);
    t1PureDate.setHours(0, 0, 0, 0);

    const diffTime = today - t1PureDate;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    // 檢查是否剛好滿 28 天 (或是超過28天還沒寄，當作補寄)
    if (diffDays >= 28) {

      // 1. 產生個人化連結
      // .../T2.html?uid=xxx&email=xxx&verify=xxx
      const personalizedLink = `${CONFIG.T2_REDIRECT_URL}?uid=${uid}&email=${encodeURIComponent(email)}&verify=${verifySum}`;

      // 2. 寄送 Email
      try {
        MailApp.sendEmail({
          to: email,
          subject: CONFIG.EMAIL_SUBJECT,
          name: CONFIG.EMAIL_SENDER_NAME,
          htmlBody: `
            <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
              <h3 style="color: #2c3e50;">職涯發展研究 - 第二階段問卷 (2/3)</h3>
              <p>親愛的職場夥伴，歡迎回來！</p>
              <p>再次感謝您參與這項關於職涯發展的長期研究。</p>
              <p><strong>【當前進度】 第二階段 (2/3)</strong></p>
              <p>距離完成僅剩最後一步！請記得，需<strong>完整填答三次問卷</strong>方具備 <strong>500元 7-11 禮券</strong> 的抽獎資格。</p>
              <p>此次填答約需 10 分鐘，為了能準確連結您的資料，請務必使用與上次相同的 <strong>Email</strong> 與 <strong>手機末三碼/生日月日共四碼</strong> 驗證。</p>
              <br
              <div style="text-align: center;">
                <a href="${personalizedLink}" style="background-color: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                  填寫第二階段問卷
                </a>
              </div>
              <br>
              <p style="font-size: 14px; color: #666;">(本連結已包含您的專屬辨識碼，點擊後請直接填寫，勿修改「配對編號」欄位)</p>
              <p style="font-size: 14px; color: #666;">若按鈕無法點擊，請複製連結: <br>${personalizedLink}</p>
              <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
              <p style="font-size: 12px; color: #999;">國立中山大學人管所 研究團隊 敬上<br>聯絡信箱：M134050804@student.nsysu.edu.tw</p>
            </div>
          `
        });

        // 3. 標記為已發送
        sheet.getRange(i + 1, 5).setValue("TRUE"); // Col E set to TRUE
        console.log(`Sent to ${email} (UID: ${uid})`);

      } catch (e) {
        console.error(`Failed to send to ${email}: ${e}`);
      }
    }
  }
}
