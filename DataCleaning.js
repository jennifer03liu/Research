/**
 * 資料清理與 SPSS 預處理腳本
 * 
 * 功能：
 * 1. 篩選 (檢核題、就業狀態、一本初衷、日期)
 * 2. 變數重新命名 (CP, PP, DP, CI...)
 * 3. 變數轉換 (年資合併、多選題拆分)
 * 4. 輸出 SPSS 專用格式
 */

function onOpen() {
    SpreadsheetApp.getUi()
        .createMenu('資料清理專用')
        .addItem('1. 執行篩選與清理', 'cleanAndExportData')
        .addToUi();
}

/**
 * 輔助函式：根據關鍵字尋找欄位索引
 */
function findCol(headers, keyword) {
    return headers.findIndex(function (h) {
        return h && h.toString().indexOf(keyword) > -1;
    });
}

function cleanAndExportData() {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sourceSheet = ss.getActiveSheet();
    var data = sourceSheet.getDataRange().getValues();

    if (data.length <= 1) {
        Browser.msgBox("資料不足，無法進行清理。");
        return;
    }

    var headers = data[0];

    // --- 0. 欄位定位 (Mapping) ---
    // 雖然可以用位置，但用標題關鍵字抓比較保險

    // 基本過濾用
    var colTimestamp = 0; // A欄
    var colAttn1 = findCol(headers, "共需填寫幾次問卷");
    var colAttn2 = findCol(headers, "這題請選擇「4」");
    var colJobStatus = findCol(headers, "就業狀態為何");

    // PM 變數 (4題)
    var colPM_Has = findCol(headers, "是否有進行績效考核");
    var colPM_Form = findCol(headers, "績效考核」通常包含哪些形式"); // 多選
    var colPM_Result = findCol(headers, "考核結果/回饋性質為何");
    var colPM_Help = findCol(headers, "職涯發展的幫助程度");

    // 量表變數
    // 假設題目順序是固定的，這裡我們用迴圈抓取從某個起始點開始的題目
    // 為了安全，我們手動抓取每個區塊的起始點，或者利用題目關鍵字

    // CP (12題): 1-6 HCP, 7-12 JCP
    // Q1: 晉升的可能性, Q7: 感到有挑戰性
    var colCP_Start = findCol(headers, "晉升的可能性是有限的");

    // PP (6題): 看不順眼
    var colPP_Start = findCol(headers, "看不順眼的事物");

    // DP (5題): 做出最終決定
    var colDP_Start = findCol(headers, "做出最終決定之前");

    // CI (9題): 調整或改變自己的職涯
    // 注意：中間夾了一個 Attn2 (第5題)
    var colCI_Start = findCol(headers, "我想調整或改變自己的職涯");

    // 背景變數
    var colGender = findCol(headers, "性別");
    var colAge = findCol(headers, "年齡");
    var colEdu = findCol(headers, "教育程度");
    var colMarriage = findCol(headers, "婚姻狀況");

    var colNowJobY = findCol(headers, "現職年資 (年)");
    var colNowJobM = findCol(headers, "現職年資 (月)");
    var colTotalJobY = findCol(headers, "工作總年資 (年)");
    var colTotalJobM = findCol(headers, "工作總年資 (月)");

    var colPos = findCol(headers, "工作職級");
    var colInd = findCol(headers, "產業別");
    var colSize = findCol(headers, "公司規模");

    // --- 檢查必要欄位 ---
    if (colAttn1 < 0 || colAttn2 < 0 || colCP_Start < 0 || colNowJobY < 0) {
        Browser.msgBox("欄位偵測失敗，請檢查問卷標題文字是否變動。");
        return;
    }

    // --- 設定新的標題列 (SPSS Format) ---
    var newHeaders = [
        "Timestamp",
        // PM
        "PM_Has",
        "PM_Form_Type1", "PM_Form_Type2", "PM_Form_Type3", "PM_Form_Other", // 多選拆分
        "PM_Result", "PM_Help",
        // HCP
        "HCP1", "HCP2", "HCP3", "HCP4", "HCP5", "HCP6",
        // JCP
        "JCP1", "JCP2", "JCP3", "JCP4", "JCP5", "JCP6",
        // PP
        "PP1", "PP2", "PP3", "PP4", "PP5", "PP6",
        // DP
        "DP1", "DP2", "DP3", "DP4", "DP5",
        // CI (8題，跳過 Attn)
        "CI1", "CI2", "CI3", "CI4", "CI5", "CI6", "CI7", "CI8",
        // Backgrounds
        "Gender", "Age", "Education", "Marriage",
        "NowJobTenure", "JobTenure", // 合併後
        "Position", "Industry", "OrgSize"
    ];

    var cleanedData = [];
    cleanedData.push(newHeaders);

    // 統計變數
    var STAGE_PREFIX = "T1";
    var now = new Date();
    var todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    var yesterday = new Date(todayStart);
    yesterday.setDate(todayStart.getDate() - 1);
    var dateString = ('0' + (yesterday.getMonth() + 1)).slice(-2) + ('0' + yesterday.getDate()).slice(-2);

    var stats = { total: 0, valid: 0 };
    var invalidJobs = ["兼職", "待業", "學生", "自由", "自營"]; // 簡化關鍵字

    // --- 逐行處理 ---
    for (var i = 1; i < data.length; i++) {
        var row = data[i];
        stats.total++;

        // 1. 日期過濾 (只收昨日以前)
        var ts = new Date(row[colTimestamp]);
        if (ts >= todayStart) continue;

        // 2. 注意力檢核
        // Attn1 必須是 '3次'
        // Attn2 必須是 '4'
        if (String(row[colAttn1]).trim() !== '3次' || String(row[colAttn2]).trim() !== '4') continue;

        // 3. 就業狀態
        var job = String(row[colJobStatus]);
        if (invalidJobs.some(function (k) { return job.indexOf(k) > -1; })) continue;

        // 4. 一本初衷 (檢查 CP, PP, DP, CI 範圍)
        // 這裡我們只簡單檢查主要量表區間是否全填一樣
        // 為了效能，我們在提取數據時順便檢查

        // --- 提取與轉換數據 ---
        var newRow = [];

        // Timestamp
        newRow.push(row[colTimestamp]);

        // PM Section
        newRow.push(row[colPM_Has]);

        // PM Multi-choice Split
        // 假設選項關鍵字 (請使用者自行修改這裡的關鍵字)
        var pmVal = String(row[colPM_Form]);
        // TODO: 請確認問卷中的實際選項文字，並修改下方的 keywords
        newRow.push(pmVal.indexOf("關鍵績效") > -1 || pmVal.indexOf("KPI") > -1 ? 1 : 0); // Type1
        newRow.push(pmVal.indexOf("目標管理") > -1 || pmVal.indexOf("MBO") > -1 ? 1 : 0); // Type2
        newRow.push(pmVal.indexOf("360") > -1 ? 1 : 0); // Type3
        newRow.push(pmVal.indexOf("其他") > -1 ? 1 : 0); // Other

        newRow.push(row[colPM_Result]);
        newRow.push(row[colPM_Help]);

        // Scales Extraction Helper
        var scaleValues = [];

        // HCP (6 items) from colCP_Start
        for (var k = 0; k < 6; k++) scaleValues.push(row[colCP_Start + k]);
        // JCP (6 items) follows HCP
        for (var k = 0; k < 6; k++) scaleValues.push(row[colCP_Start + 6 + k]);
        // PP (6 items)
        for (var k = 0; k < 6; k++) scaleValues.push(row[colPP_Start + k]);
        // DP (5 items)
        for (var k = 0; k < 5; k++) scaleValues.push(row[colDP_Start + k]);

        // CI (8 items, skip Q5)
        // Q1~Q4
        for (var k = 0; k < 4; k++) scaleValues.push(row[colCI_Start + k]);
        // Q5 is Attn, skip (colCI_Start + 4)
        // Q6~Q9
        for (var k = 5; k < 9; k++) scaleValues.push(row[colCI_Start + k]);

        // 數值化 & 一本初衷檢查
        var numericVals = [];
        var allSame = true;
        var firstVal = null;

        for (var v = 0; v < scaleValues.length; v++) {
            var val = scaleValues[v];
            var num = val;
            if (typeof val === 'string' && !isNaN(val) && val !== '') num = Number(val);

            numericVals.push(num);
            newRow.push(num); // Add to newRow

            // Check straight-lining
            if (v === 0) firstVal = num;
            else if (num !== firstVal) allSame = false;
        }

        if (allSame) continue; // 排除一本初衷

        // Backgrounds
        newRow.push(row[colGender]);
        newRow.push(row[colAge]);
        newRow.push(row[colEdu]);
        newRow.push(row[colMarriage]);

        // Tenure Calc
        // NowJob
        var ny = Number(row[colNowJobY]) || 0;
        var nm = Number(row[colNowJobM]) || 0;
        newRow.push(parseFloat((ny + nm / 12).toFixed(2)));

        // TotalJob
        var ty = Number(row[colTotalJobY]) || 0;
        var tm = Number(row[colTotalJobM]) || 0;
        newRow.push(parseFloat((ty + tm / 12).toFixed(2)));

        newRow.push(row[colPos]);
        newRow.push(row[colInd]);
        newRow.push(row[colSize]);

        cleanedData.push(newRow);
        stats.valid++;
    }

    // --- Export ---
    var targetSheetName = STAGE_PREFIX + "_" + dateString + "_" + stats.valid + "_SPSS";
    var targetSheet = ss.getSheetByName(targetSheetName);
    if (targetSheet) ss.deleteSheet(targetSheet);
    targetSheet = ss.insertSheet(targetSheetName);

    if (cleanedData.length > 0) {
        targetSheet.getRange(1, 1, cleanedData.length, cleanedData[0].length).setValues(cleanedData);
        targetSheet.setFrozenRows(1);
    }

    Browser.msgBox("SPSS 格式化完成！\n有效筆數: " + stats.valid);
}
