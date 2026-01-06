function doPost(e) {
  // 取得一個公共鎖，避免同時寫入衝突
  var lock = LockService.getScriptLock();
  try {
    // 等待最多 30 秒來獲取鎖定權
    lock.waitLock(30000); 

    var ss = SpreadsheetApp.openById('1WvMarcAHDP6-GKarleQBe1VK55uXDUXZKyirrT0jeGY');
    var sheet = ss.getSheetByName('受試者名單');
    
    var data = JSON.parse(e.postData.contents);
    // Modified back to correct structure: [Date, Empty, Code, Url] (Writes to Col 3)
    sheet.appendRow([new Date(), "", data.code, data.url]);
    
    return ContentService.createTextOutput("Success");
  } catch (error) {
    return ContentService.createTextOutput("Error").setMimeType(ContentService.MimeType.TEXT);
  } finally {
    // 釋放鎖，讓下一筆資料可以進來
    lock.releaseLock();
  }
}


// // Google Apps Script (Code.gs)

// // ========= 請將此試算表 ID 換成您自己的 =========
// const SHEET_ID = "1WvMarcAHDP6-GKarleQBe1VK55uXDUXZKyirrT0jeGY"; 
// const SHEET_NAME = "受試者名單"; // 請確認您的工作表名稱是否為「資料」

// // doPost 函式，處理前端發來的 POST 請求
// function doPost(e) {
//   try {
//     // 記錄收到的請求內容，這是偵錯的關鍵
//     Logger.log("收到了 POST 請求");
//     Logger.log("請求參數 (e): " + JSON.stringify(e));

//     // e.postData.contents 包含了前端發送的原始資料
//     const postDataString = e.postData.contents;
//     Logger.log("收到的原始資料 (e.postData.contents): " + postDataString);
    
//     if (!postDataString) {
//       Logger.log("錯誤：postData.contents 是空的。");
//       return createJsonResponse({ status: 'error', message: 'Request body is empty.' });
//     }

//     // 解析 JSON 資料
//     const data = JSON.parse(postDataString);
//     Logger.log("成功解析 JSON 資料: " + JSON.stringify(data));

//     // 寫入 Google Sheet
//     const sheet = SpreadsheetApp.openById(SHEET_ID).getSheetByName(SHEET_NAME);
//     sheet.appendRow([
//       data.code || 'N/A',
//       data.url || 'N/A',
//       data.timestamp || new Date().toISOString()
//     ]);
    
//     Logger.log("資料成功寫入 Google Sheet");

//     // 回傳成功的 JSON 回應
//     return createJsonResponse({ status: 'success', receivedData: data });

//   } catch (error) {
//     // 如果發生任何錯誤，記錄下來
//     Logger.log("發生錯誤: " + error.toString());
//     Logger.log("錯誤堆疊: " + error.stack);
    
//     // 回傳包含錯誤訊息的 JSON 回應
//     return createJsonResponse({ status: 'error', message: error.toString() });
//   }
// }

// // 建立一個標準的 JSON 回應
// function createJsonResponse(obj) {
//   return ContentService.createTextOutput(JSON.stringify(obj))
//     .setMimeType(ContentService.MimeType.JSON);
// }

// // 你可以保留這個 doGet 以便在瀏覽器中直接測試 Web App 是否正常運作
// function doGet(e) {
//   return ContentService.createTextOutput("GAS Web App is running.");
// }