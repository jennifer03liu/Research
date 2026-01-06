function doPost(e) {
  // 鎖定您的試算表與工作表
  var ss = SpreadsheetApp.openById('1WvMarcAHDP6-GKarleQBe1VK55uXDUXZKyirrT0jeGY');
  var sheet = ss.getSheetByName('受試者名單');
  
  try {
    // 解析前端傳來的資料
    var data = JSON.parse(e.postData.contents);
    var code = data.code;
    var url = data.url;
    
    // 依照您的要求寫入：[當前時間, "", "", 驗證碼, 完整網址]
    // new Date() 會自動記錄伺服器當下時間
    sheet.appendRow([new Date(), "", "", code, url]);
    
    return ContentService.createTextOutput("Success");
  } catch (error) {
    // 錯誤處理
    return ContentService.createTextOutput("Error");
  }
}