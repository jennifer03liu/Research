/**
 * 資料清理與 SPSS 預處理腳本
 * 
 * 功能：
 * 1. 篩選無效問卷（檢查兩題注意力檢核題）
 * 2. 格式化數據（將量表文字 "1"~"5" 轉為數字格式，方便 SPSS 判讀）
 * 3. 輸出至新工作表 "Cleaned_Data_For_SPSS"
 */

function onOpen() {
    SpreadsheetApp.getUi()
        .createMenu('資料清理專用')
        .addItem('1. 執行篩選與清理', 'cleanAndExportData')
        .addToUi();
}

function cleanAndExportData() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    // 假設資料在第一個工作表，或請使用者將此腳本綁定在原始資料表上並開啟該分頁
    var sourceSheet = ss.getActiveSheet();
    var data = sourceSheet.getDataRange().getValues();

    if (data.length <= 1) {
        Browser.msgBox("資料不足，無法進行清理。");
        return;
    }

    var headers = data[0];

    // 設定輸出工作表名稱
    var targetSheetName = "Cleaned_Data_For_SPSS";

    // --- 1. 自動尋找檢核題欄位 ---
    // 檢核題 1: "1. 詳述以上說明後，請問本研究共需填寫幾次問卷？" -> 答案必須是 3
    var idxAttn1 = headers.findIndex(function (h) {
        return h.toString().indexOf("詳述以上說明後，請問本研究共需填寫幾次問卷？") > -1;
    });

    // 檢核題 2: "5. 這題請選擇「4」" -> 答案必須是 4
    var idxAttn2 = headers.findIndex(function (h) {
        return h.toString().indexOf("這題請選擇「4」") > -1;
    });

    // 檢查是否找到欄位
    if (idxAttn1 === -1 || idxAttn2 === -1) {
        var msg = "找不到檢核題欄位，請檢查標題文字。\n";
        msg += "偵測結果: 檢核題1(idx=" + idxAttn1 + "), 檢核題2(idx=" + idxAttn2 + ")";
        Browser.msgBox(msg);
        return;
    }

    var cleanedData = [];
    cleanedData.push(headers); // 保留標題列

    var removedCount = 0;
    var totalProcessed = 0;

    // --- 2. 逐列檢查與轉換 ---
    // 從第 2 列 (index 1) 開始跑
    for (var i = 1; i < data.length; i++) {
        var row = data[i];
        totalProcessed++;

        // 取得檢核題答案 (轉成字串並去除前後空白，避免格式差異)
        var ans1 = String(row[idxAttn1]).trim();
        var ans2 = String(row[idxAttn2]).trim();

        // 判斷條件：第一題要選 '3'，第二題要選 '4'
        // 注意：表單回應有時可能是數值 3 或字串 "3"，所以上面轉 String 處理
        if (ans1 === '3次' && ans2 === '4') {

            // 通過檢核，進行資料型態轉換 (優化 SPSS 匯入)
            // 範圍：B欄 (index 1) 到 AZ欄 (index 51) 通常是量表題
            // 我們將這個範圍內看似數字的字串轉為真正數值
            for (var j = 1; j <= 51; j++) {
                if (j < row.length) {
                    var cellVal = row[j];
                    // 如果是純數字字串，轉成 Number
                    // 使用 isNaN 檢查，並排除空字串
                    if (typeof cellVal === 'string' && cellVal.trim() !== '' && !isNaN(cellVal)) {
                        row[j] = Number(cellVal);
                    }
                }
            }

            cleanedData.push(row);
        } else {
            removedCount++;
        }
    }

    // --- 3. 輸出結果 ---
    var targetSheet = ss.getSheetByName(targetSheetName);
    if (targetSheet) {
        // 如果已存在，先刪除舊的 (或清空)
        // 這裡選擇刪除重建，確保乾淨
        ss.deleteSheet(targetSheet);
    }
    targetSheet = ss.insertSheet(targetSheetName);

    // 寫入資料
    if (cleanedData.length > 0) {
        targetSheet.getRange(1, 1, cleanedData.length, cleanedData[0].length).setValues(cleanedData);

        // 簡單排版：凍結第一列
        targetSheet.setFrozenRows(1);
    }

    // 回報結果
    var resultMsg = "清理完成！\n";
    resultMsg += "處理總筆數: " + totalProcessed + "\n";
    resultMsg += "移除無效卷: " + removedCount + "\n";
    resultMsg += "有效樣本數: " + (cleanedData.length - 1); // 扣掉標題

    Browser.msgBox(resultMsg);
}
