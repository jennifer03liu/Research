/**
 * 資料清理與 SPSS 預處理腳本 (全階段支援)
 * 
 * 功能：
 * 1. 篩選各階段 (檢核題、就業狀態、一本初衷)
 * 2. T1 基礎清理 (轉換年資、多選題拆分)
 * 3. T2/T3 的清理 (測謊題篩選)
 * 4. 合併所有過濾後結果
 */

function onOpen() {
    SpreadsheetApp.getUi()
        .createMenu('資料清理專用')
        .addItem('1. 清理 T1 (第一階段)', 'runCleanT1')
        .addItem('2. 清理 T2 (第二階段)', 'runCleanT2')
        .addItem('3. 清理 T3 (第三階段)', 'runCleanT3')
        .addSeparator()
        .addItem('4. 整合並清理全三階段', 'runCleanAndMergeAll')
        .addToUi();
}

/**
 * 輔助函式：根據關鍵字尋找欄位索引
 */
function findCol(headers, keyword) {
    if (!headers) return -1;
    return headers.findIndex(function (h) {
        return h && h.toString().indexOf(keyword) > -1;
    });
}

function cleanMatchId(val) {
    if (val === "" || val === null || val === undefined) return "";
    var matchVal = String(val).trim();
    if (/^\d+$/.test(matchVal)) {
        while (matchVal.length < 7) {
            matchVal = "0" + matchVal;
        }
    }
    return matchVal;
}

// 供合併使用的 Override (手動修復 T1 對不上的 Email)
var MANUAL_OVERRIDES = {
    'jaychen@trendforce.com': '0710588',
    'huang0447@itri.org.tw': '0315587',
    'baoan5669@gmail.com': '1003082',
    'zxcv70103@gmail.com': '0108108',
    'jhenjiahu@gmail.com': '1230016',
    'zxc52040@gmail.com': '0404983'
};

/**
 * 通用函式：抓取清理後的特定階段資料清單
 */
function getCleanedData(phaseName) {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(phaseName);
    if (!sheet) {
        Browser.msgBox("找不到工作表: " + phaseName);
        return null;
    }

    var data = sheet.getDataRange().getValues();
    if (data.length <= 1) return null;

    var headers = data[0];
    var isT1 = phaseName === '第一階段';
    var isT2 = phaseName === '第二階段';
    var isT3 = phaseName === '第三階段';

    // Locate core columns
    var colTimestamp = 0;
    var colEmail = findCol(headers, "電子郵件地址") > -1 ? findCol(headers, "電子郵件地址") : (findCol(headers, "Email") > -1 ? findCol(headers, "Email") : findCol(headers, "聯絡資訊"));

    var colMatchId = findCol(headers, "出生月份日期及手機末3碼");
    if (colMatchId === -1) colMatchId = findCol(headers, "手機末3碼");

    // Phase specific checks
    var colAttnTarget = -1;
    var requiredAttnVal = "";

    if (isT1) {
        colAttnTarget = findCol(headers, "這題請選擇「4」");
        requiredAttnVal = "4";
    } else {
        colAttnTarget = findCol(headers, "這題請選擇「2」");
        requiredAttnVal = "2";
    }

    // T1 specific filtering
    var colAttn1 = findCol(headers, "共需填寫幾次問卷");
    var colJobStatus = findCol(headers, "就業狀態為何");
    var invalidJobs = ["兼職", "待業", "學生", "自由", "自營"];

    var validRecords = [];
    var stats = { total: 0, valid: 0, invalid_attn: 0, invalid_job: 0 };

    for (var i = 1; i < data.length; i++) {
        var row = data[i];
        stats.total++;

        // Attn Check
        if (colAttnTarget > -1) {
            var val = String(row[colAttnTarget]).trim();
            if (val !== requiredAttnVal) {
                stats.invalid_attn++;
                continue;
            }
        }

        if (isT1) {
            if (colAttn1 > -1 && String(row[colAttn1]).trim() !== '3次') continue;
            var job = String(row[colJobStatus]);
            if (invalidJobs.some(function (k) { return job.indexOf(k) > -1; })) {
                stats.invalid_job++;
                continue;
            }
        }

        // Standardize Match ID for easier joining later
        var rawMatchId = (colMatchId > -1) ? String(row[colMatchId]).replace(/\D/g, "") : "";
        var cleanId = cleanMatchId(rawMatchId);
        var email = (colEmail > -1) ? String(row[colEmail]).trim().toLowerCase() : "";

        // Manual override application for T2/T3
        if (!isT1 && email && MANUAL_OVERRIDES[email]) {
            cleanId = MANUAL_OVERRIDES[email];
        } else if (!cleanId && email && MANUAL_OVERRIDES[email]) {
            cleanId = MANUAL_OVERRIDES[email];
        }

        // Store clean record alongside original row for modularity
        validRecords.push({
            Join_ID: cleanId,
            Email: email,
            OriginalRow: row
        });

        stats.valid++;
    }

    return {
        headers: headers,
        records: validRecords,
        stats: stats
    };
}

// ----------------------------------------------------
// UI Triggered Functions
// ----------------------------------------------------

function runCleanT1() {
    var result = getCleanedData('第一階段');
    if (!result) return;

    // Convert to T1 specialized export format
    var exp = exportT1Format(result.headers, result.records);
    writeToNewSheet("T1_Cleaned", exp.headers, exp.data);

    Browser.msgBox("T1 清理完成\\n總數: " + result.stats.total + "\\n測謊失敗: " + result.stats.invalid_attn + "\\n就業不符: " + result.stats.invalid_job + "\\n保留有效: " + result.stats.valid);
}

function runCleanT2() {
    var result = getCleanedData('第二階段');
    if (!result) return;
    writeSimpleExtract("T2_Cleaned", result);
    Browser.msgBox("T2 清理完成\\n總數: " + result.stats.total + "\\n測謊失敗: " + result.stats.invalid_attn + "\\n保留有效: " + result.stats.valid);
}

function runCleanT3() {
    var result = getCleanedData('第三階段');
    if (!result) return;
    writeSimpleExtract("T3_Cleaned", result);
    Browser.msgBox("T3 清理完成\\n總數: " + result.stats.total + "\\n測謊失敗: " + result.stats.invalid_attn + "\\n保留有效: " + result.stats.valid);
}

function runCleanAndMergeAll() {
    var t1Data = getCleanedData('第一階段');
    var t2Data = getCleanedData('第二階段');
    var t3Data = getCleanedData('第三階段');

    if (!t1Data || !t2Data) {
        Browser.msgBox("必須要有 T1 與 T2 工作表才能執行合併。");
        return;
    }

    // Process T1 to its standardized export format
    var t1Exp = exportT1Format(t1Data.headers, t1Data.records);

    // Prepare dictionaries for T2 and T3 lookups by Join_ID
    var t2Map = {};
    for (var i = 0; i < t2Data.records.length; i++) {
        var rec = t2Data.records[i];
        if (rec.Join_ID) t2Map[rec.Join_ID] = rec.OriginalRow;
    }

    var t3Map = {};
    if (t3Data) {
        for (var j = 0; j < t3Data.records.length; j++) {
            var rec3 = t3Data.records[j];
            if (rec3.Join_ID) t3Map[rec3.Join_ID] = rec3.OriginalRow;
        }
    }

    // Prepare merged headers
    var mergedHeaders = t1Exp.headers.slice(); // Copy T1 headers

    // Add T2 headers with suffix
    var t2HeadClean = [];
    for (var c2 = 0; c2 < t2Data.headers.length; c2++) {
        var h2 = t2Data.headers[c2];
        if (h2.indexOf("配對") === -1 && h2.indexOf("聯絡") === -1 && h2.indexOf("時間戳記") === -1) {
            t2HeadClean.push({ idx: c2, name: h2 + "_T2" });
            mergedHeaders.push(h2 + "_T2");
        }
    }

    // Add T3 headers with suffix
    var t3HeadClean = [];
    if (t3Data) {
        for (var c3 = 0; c3 < t3Data.headers.length; c3++) {
            var h3 = t3Data.headers[c3];
            if (h3.indexOf("配對") === -1 && h3.indexOf("聯絡") === -1 && h3.indexOf("時間戳記") === -1) {
                t3HeadClean.push({ idx: c3, name: h3 + "_T3" });
                mergedHeaders.push(h3 + "_T3");
            }
        }
    }

    var mergedRows = [];
    var matchT2Count = 0;
    var matchT3Count = 0;

    // Perform Inner Join logic based on T1 elements
    // Only keeping elements that exist in BOTH T1 and T2
    for (var n = 0; n < t1Exp.data.length; n++) {
        var t1Row = t1Exp.data[n];
        var joinId = String(t1Row[3]).replace(/[']/g, ""); // Match_ID index in T1 Exp

        var t2RowTarget = t2Map[joinId];

        if (t2RowTarget) {
            matchT2Count++;
            var newRow = t1Row.slice();

            // Append T2 requested columns
            for (var c2x = 0; c2x < t2HeadClean.length; c2x++) {
                newRow.push(t2RowTarget[t2HeadClean[c2x].idx]);
            }

            // Append T3 if exists
            var t3RowTarget = t3Map[joinId];
            if (t3RowTarget) {
                matchT3Count++;
                for (var c3x = 0; c3x < t3HeadClean.length; c3x++) {
                    newRow.push(t3RowTarget[t3HeadClean[c3x].idx]);
                }
            } else if (t3Data) {
                for (var c3e = 0; c3e < t3HeadClean.length; c3e++) {
                    newRow.push("");
                }
            }

            mergedRows.push(newRow);
        }
    }

    writeToNewSheet("Longitudinal_Merged", mergedHeaders, mergedRows);
    Browser.msgBox("三階段合併完成！\\n保留 T1+T2 成功配對的有效樣本: " + matchT2Count + " 筆\\n其中包含 T3 成功配對的有效樣本: " + matchT3Count + " 筆");
}

// ----------------------------------------------------
// Formatting & Export Helpers
// ----------------------------------------------------

function writeSimpleExtract(prefix, extractData) {
    var outData = [extractData.headers];
    for (var i = 0; i < extractData.records.length; i++) {
        outData.push(extractData.records[i].OriginalRow);
    }
    writeToNewSheet(prefix + "_" + extractData.stats.valid, extractData.headers, outData.slice(1), true);
}

function writeToNewSheet(name, headers, dataRows, prependHeaders = false) {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var now = new Date();
    var tsStr = ('0' + (now.getMonth() + 1)).slice(-2) + ('0' + now.getDate()).slice(-2) + "_" + now.getHours() + now.getMinutes();

    var sheetName = name + "_" + tsStr;
    var targetSheet = ss.getSheetByName(sheetName);
    if (targetSheet) ss.deleteSheet(targetSheet);
    targetSheet = ss.insertSheet(sheetName);

    var finalArr = [headers].concat(dataRows);
    if (prependHeaders && dataRows.length > 0 && dataRows[0].length === headers.length && dataRows[0][0] !== headers[0]) {
        // Handled naturally by concat
    }

    if (finalArr.length > 0) {
        targetSheet.getRange(1, 1, finalArr.length, finalArr[0].length).setValues(finalArr);
        targetSheet.setFrozenRows(1);
        try { targetSheet.autoResizeColumns(1, 15); } catch (e) { }
    }
}

/**
 * 完整轉化 T1 到 SPSS 分析所需的數位編碼格式
 * (擷取原本的複雜腳本邏輯)
 */
function exportT1Format(headers, records) {
    var newHeaders = [
        "Timestamp", "Custom_UID", "Email", "Match_ID", "WorkHours",
        "PM_Has", "PM_Form_Supervisor", "PM_Form_Self", "PM_Form_Interview", "PM_Form_Other",
        "PM_Result", "PM_Help",
        "HP1", "HP2", "HP3", "HP4_R", "HP5", "HP6_R",
        "JCP1_R", "JCP2_R", "JCP3_R", "JCP4_R", "JCP5_R", "JCP6",
        "PP1", "PP2", "PP3", "PP4", "PP5", "PP6",
        "DP1", "DP2", "DP3", "DP4", "DP5",
        "CI1", "CI2", "CI3", "CI4", "CI5", "CI6", "CI7", "CI8",
        "Gender", "Age", "Education", "Marriage",
        "NowJobTenure", "JobTenure", "Position", "Industry", "OrgSize"
    ];

    var colTimestamp = 0;
    var colCustomUID = findCol(headers, "Custom_UID");
    var colWorkHours = findCol(headers, "每周平均工時");
    var colPM_Has = findCol(headers, "是否有進行績效考核");
    var colPM_Form = findCol(headers, "績效考核」通常包含哪些形式");
    var colPM_Result = findCol(headers, "考核結果/回饋性質為何");
    var colPM_Help = findCol(headers, "職涯發展的幫助程度");

    var colCP_Start = findCol(headers, "晉升的可能性是有限的");
    var colPP_Start = findCol(headers, "看不順眼的事物");
    var colDP_Start = findCol(headers, "做出最終決定之前");
    var colCI_Start = findCol(headers, "我想調整或改變自己的職涯");

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

    var cleanedRows = [];

    for (var i = 0; i < records.length; i++) {
        var rec = records[i];
        var row = rec.OriginalRow;
        var newRow = [];

        newRow.push(row[colTimestamp]);
        var cleanUID = (colCustomUID > -1 ? String(row[colCustomUID]).replace(/-/g, "") : "");
        newRow.push(cleanUID.length === 8 ? cleanUID.substr(0, 4) + "-" + cleanUID.substr(4, 4) : cleanUID);
        newRow.push(rec.Email);
        newRow.push("'" + rec.Join_ID);

        // Work Hours
        var whVal = String(row[colWorkHours]);
        if (whVal.indexOf("40 小時(含)以上") > -1) newRow.push(1);
        else if (whVal.indexOf("未滿 40 小時") > -1) newRow.push(0);
        else newRow.push("");

        // PM Settings
        var pmVal = String(row[colPM_Has]);
        var hasPM = pmVal.indexOf("是") > -1;
        newRow.push(hasPM ? 1 : 0);

        if (!hasPM) {
            for (var z = 0; z < 6; z++) newRow.push("");
        } else {
            var pForm = String(row[colPM_Form]);
            newRow.push(pForm.indexOf("主管") > -1 ? 1 : 0);
            newRow.push(pForm.indexOf("自評") > -1 ? 1 : 0);
            newRow.push(pForm.indexOf("面談") > -1 ? 1 : 0);
            newRow.push(pForm.indexOf("其他") > -1 ? 1 : 0);

            var pRes = String(row[colPM_Result]);
            if (pRes.indexOf("正向") > -1) newRow.push(3);
            else if (pRes.indexOf("中性") > -1) newRow.push(2);
            else if (pRes.indexOf("負向") > -1) newRow.push(1);
            else newRow.push("");

            newRow.push(row[colPM_Help]);
        }

        // SCALES - Extract and apply reverse scoring precisely
        var extractNumeric = function (val) {
            var num = Number(val);
            return (isNaN(num) || val === "") ? val : num;
        };

        var rev = function (val) {
            var num = extractNumeric(val);
            return (typeof num === 'number') ? (6 - num) : val;
        };

        // HP 1-6 (Reverse 4, 6)
        for (var k = 0; k < 6; k++) newRow.push((k === 3 || k === 5) ? rev(row[colCP_Start + k]) : extractNumeric(row[colCP_Start + k]));
        // JCP 1-6 (Reverse 1-5)
        for (var k = 0; k < 6; k++) newRow.push((k <= 4) ? rev(row[colCP_Start + 6 + k]) : extractNumeric(row[colCP_Start + 6 + k]));

        // PP 1-6
        for (var k = 0; k < 6; k++) newRow.push(extractNumeric(row[colPP_Start + k]));
        // DP 1-5
        for (var k = 0; k < 6; k++) {
            if (k === 3) continue; // Original logic missed indices or skipped based on previous script review? Actually just pure sequential.
            // Re-asserting direct sequencing based on T1 structure
        }
        for (var k = 0; k < 5; k++) newRow.push(extractNumeric(row[colDP_Start + k]));

        // CI (Skip index 4 which is Check)
        for (var k = 0; k < 4; k++) newRow.push(extractNumeric(row[colCI_Start + k]));
        for (var k = 5; k < 9; k++) newRow.push(extractNumeric(row[colCI_Start + k]));

        // Background
        newRow.push(encodeValue(row[colGender], ["男", "女", "其他"]));
        newRow.push(row[colAge]);
        newRow.push(encodeValue(row[colEdu], ["高中", "專科", "大學", "碩士", "博士"]));
        newRow.push(encodeValue(row[colMarriage], ["未婚", "無子女", "有子女", "其他"]));

        var ny = Number(row[colNowJobY]) || 0;
        var nm = Number(row[colNowJobM]) || 0;
        newRow.push(ny * 12 + nm);

        var ty = Number(row[colTotalJobY]) || 0;
        var tm = Number(row[colTotalJobM]) || 0;
        newRow.push(ty * 12 + tm);

        newRow.push(encodeValue(row[colPos], ["一般", "基層", "中階", "高階"]));
        newRow.push(encodeValue(row[colInd], ["製造", "科技", "金融", "服務", "醫療", "教育", "公部門", "其他"]));
        newRow.push(encodeValue(row[colSize], ["30", "31", "101", "501", "1001"]));

        cleanedRows.push(newRow);
    }

    return { headers: newHeaders, data: cleanedRows };
}

function encodeValue(val, keywords) {
    var str = String(val);
    for (var i = 0; i < keywords.length; i++) {
        if (str.indexOf(keywords[i]) > -1) {
            return i + 1;
        }
    }
    return "";
}
