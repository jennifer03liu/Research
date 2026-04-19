/**
 * 鞈?皜???SPSS ?????(?券?畾菜??
 * 
 * ?嚗?
 * 1. 蝭拚??畾?(瑼Ｘ憿停璆剔????砍?銵?
 * 2. T1 ?箇?皜? (頧?撟渲????賊???)
 * 3. T2/T3 ????(皜祈?憿祟??
 * 4. 產生三階段合併總檔
 */

function onOpen() {
    SpreadsheetApp.getUi()
        .createMenu('資料清理實用集')
        .addItem('1. 清理 T1 (第一階段)', 'runCleanT1')
        .addItem('2. 清理 T2 (第二階段)', 'runCleanT2')
        .addItem('3. 清理 T3 (第三階段)', 'runCleanT3')
        .addSeparator()
        .addItem('4. 產生三階段合併總檔', 'runCleanAndMergeAll')
        .addToUi();
}

/**
 * 頛?賢?嚗???萄?撠甈?蝝Ｗ?
 */
function findCol(headers, keyword) {
    if (!headers) return -1;
    return headers.findIndex(function (h) {
        return h && h.toString().indexOf(keyword) > -1;
    });
}



/**
 * ??賢?嚗??????摰?畾菔?????
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
    var colEmail = findCol(headers, "?餃??萎辣?啣?") > -1 ? findCol(headers, "?餃??萎辣?啣?") : (findCol(headers, "Email") > -1 ? findCol(headers, "Email") : findCol(headers, "?舐窗鞈?"));

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
    var invalidJobs = ["?潸", "敺平", "摮貊?", "?芰", "?芰?"];

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
            if (colAttn1 > -1 && String(row[colAttn1]).trim() !== "3次") continue;
            var job = String(row[colJobStatus]);
            if (invalidJobs.some(function (k) { return job.indexOf(k) > -1; })) {
                stats.invalid_job++;
                continue;
            }
        }

        // Standardize Match ID for easier joining later
        var rawMatchId = (colMatchId > -1) ? String(row[colMatchId]) : "";
        var email = (colEmail > -1) ? String(row[colEmail]) : "";

        var cleanId = getEffectiveMatchId(email, rawMatchId);

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

    Browser.msgBox("T1 清理完成！\\n總筆數: " + result.stats.total + "\\n錯過注意力題: " + result.stats.invalid_attn + "\\n不符就業條件: " + result.stats.invalid_job + "\\n有效樣本數: " + result.stats.valid);
}

function runCleanT2() {
    var result = getCleanedData('第二階段');
    if (!result) return;
    writeSimpleExtract("T2_Cleaned", result);
    Browser.msgBox("T2 清理完成！\\n總筆數: " + result.stats.total + "\\n錯過注意力題: " + result.stats.invalid_attn + "\\n有效樣本數: " + result.stats.valid);
}

function runCleanT3() {
    var result = getCleanedData('第三階段');
    if (!result) return;
    writeSimpleExtract("T3_Cleaned", result);
    Browser.msgBox("T3 清理完成！\\n總筆數: " + result.stats.total + "\\n錯過注意力題: " + result.stats.invalid_attn + "\\n有效樣本數: " + result.stats.valid);
}

function runCleanAndMergeAll() {
    var t1Data = getCleanedData('第一階段');
    var t2Data = getCleanedData('第二階段');
    var t3Data = getCleanedData('第三階段');

    if (!t1Data || !t2Data) {
        Browser.msgBox("必須要有 T1 及 T2 資料才能執行合併。");
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
        if (h2.indexOf("同意") === -1 && h2.indexOf("信箱") === -1 && h2.indexOf("真實姓名") === -1) {
            t2HeadClean.push({ idx: c2, name: h2 + "_T2" });
            mergedHeaders.push(h2 + "_T2");
        }
    }

    // Add T3 headers with suffix
    var t3HeadClean = [];
    if (t3Data) {
        for (var c3 = 0; c3 < t3Data.headers.length; c3++) {
            var h3 = t3Data.headers[c3];
            if (h3.indexOf("同意") === -1 && h3.indexOf("信箱") === -1 && h3.indexOf("真實姓名") === -1) {
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
 * 摰頧? T1 ??SPSS ?????雿楊蝣潭撘?
 * (?瑕??????祇?頛?
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
        if (whVal.indexOf("40 小時") > -1) newRow.push(1);
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
            else if (pRes.indexOf("中立") > -1) newRow.push(2);
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
            return i + 1; // Return 1-based index
        }
    }
    return "";
}

// --- 設定區 ---
var FORM_ID = '1FZMcpaxYpR_0z9cTksgGsZxQ5s8hu61-JCUwn-UL-CM';
var SHEET_NAME = '表單回應2';
var STATUS_COL_HEADER = '狀態';
// -------------

function deleteTriggerByName(functionName) {
    var triggers = ScriptApp.getProjectTriggers();
    for (var i = 0; i < triggers.length; i++) {
        if (triggers[i].getHandlerFunction() === functionName) {
            ScriptApp.deleteTrigger(triggers[i]);
        }
    }
}

function startQueue() {
    processNextRow();
}

function processNextRow() {
    deleteTriggerByName('processNextRow');
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
    if (!sheet) {
        console.error('找不到工作表：' + SHEET_NAME);
        return;
    }
    var rows = sheet.getDataRange().getValues();
    var headers = rows[0];
    var statusColIndex = headers.indexOf(STATUS_COL_HEADER);
    if (statusColIndex === -1) {
        SpreadsheetApp.getUi().alert('找不到標題');
        return;
    }
    var targetRowIndex = -1;
    for (var i = 1; i < rows.length; i++) {
        if (rows[i][statusColIndex] === '' || rows[i][statusColIndex] === undefined) {
            targetRowIndex = i;
            break;
        }
    }
    if (targetRowIndex === -1) {
        console.log('所有資料皆已提交完成！');
        return;
    }
    submitRowToForm(rows[targetRowIndex], headers, sheet, targetRowIndex + 1, statusColIndex + 1);
    var minMinutes = 3;
    var maxMinutes = 5;
    var randomDelayMs = Math.floor((Math.random() * (maxMinutes - minMinutes) + minMinutes) * 60 * 1000);
    ScriptApp.newTrigger('processNextRow').timeBased().after(randomDelayMs).create();
}

function submitRowToForm(rowData, headers, sheet, rowNumber, statusColNumber) {
    var form = FormApp.openById(FORM_ID);
    var items = form.getItems();
    var formResponse = form.createResponse();
    for (var j = 0; j < headers.length; j++) {
        var headerName = headers[j];
        var cellData = rowData[j];
        if (headerName === STATUS_COL_HEADER || cellData === '') continue;
        for (var k = 0; k < items.length; k++) {
            var item = items[k];
            if (item.getTitle() === headerName) {
                var responseItem = null;
                if (item.getType() == FormApp.ItemType.TEXT) {
                    responseItem = item.asTextItem().createResponse(String(cellData));
                } else if (item.getType() == FormApp.ItemType.PARAGRAPH_TEXT) {
                    responseItem = item.asParagraphTextItem().createResponse(String(cellData));
                } else if (item.getType() == FormApp.ItemType.MULTIPLE_CHOICE) {
                    responseItem = item.asMultipleChoiceItem().createResponse(String(cellData));
                } else if (item.getType() == FormApp.ItemType.CHECKBOX) {
                    var choices = String(cellData).split(/,\s*/);
                    responseItem = item.asCheckboxItem().createResponse(choices);
                } else if (item.getType() == FormApp.ItemType.LIST) {
                    responseItem = item.asListItem().createResponse(String(cellData));
                } else if (item.getType() == FormApp.ItemType.SCALE) {
                    responseItem = item.asScaleItem().createResponse(parseInt(cellData));
                }
                if (responseItem) {
                    formResponse.withItemResponse(responseItem);
                }
                break;
            }
        }
    }
    formResponse.submit();
    sheet.getRange(rowNumber, statusColNumber).setValue('已完成 (' + new Date().toLocaleTimeString() + ')');
}

/**
 * 進階除錯工具：找出哪一筆 T2 回應沒有對應到 Tracking_Log
 */
function findMissingSubmission() {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sheetT2 = ss.getSheetByName(CONFIG.SHEET_NAME_PHASE2);
    const sheetLog = ss.getSheetByName(CONFIG.SHEET_NAME_TRACKING_LOG);
    if (!sheetT2 || !sheetLog) { console.error('找不到工作表'); return; }
    const t2Data = sheetT2.getDataRange().getValues();
    const logData = sheetLog.getDataRange().getValues();
    const logMap = new Map();
    const logMatchIdMap = new Map();
    for (let i = 1; i < logData.length; i++) {
        const row = logData[i];
        const isFilled = (row[5] && String(row[5]).trim() !== '');
        if (isFilled) {
            const email = String(row[2]).trim().toLowerCase();
            const matchId = String(row[3]).replace(/\D/g, '');
            if (email) logMap.set(email, i + 1);
            if (matchId) logMatchIdMap.set(matchId, i + 1);
        }
    }
    const headers = t2Data[0];
    let colEmailIdx = 40;
    let colMatchIdIdx = 39;
    const missingList = [];
    const seenEmails = new Map();
    const duplicates = [];
    for (let i = 1; i < t2Data.length; i++) {
        const row = t2Data[i];
        const rawEmail = (row[colEmailIdx] !== undefined) ? row[colEmailIdx] : '';
        const email = String(rawEmail).trim().toLowerCase();
        if (email && seenEmails.has(email)) {
            duplicates.push({ email: email, originalRow: seenEmails.get(email), duplicateRow: i + 1 });
        } else if (email) {
            seenEmails.set(email, i + 1);
        }
        let matchId = '';
        if (colMatchIdIdx > -1) {
            const rawMatchId = (row[colMatchIdIdx] !== undefined) ? row[colMatchIdIdx] : '';
            matchId = String(rawMatchId).replace(/\D/g, '');
        }
        let found = logMap.has(email);
        if (!found && matchId) found = logMatchIdMap.has(matchId);
        if (!found) missingList.push({ row: i + 1, email: email, matchId: matchId, timestamp: row[0] });
    }
}

