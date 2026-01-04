// --- 設定區 ---
var FORM_ID = '1FZMcpaxYpR_0z9cTksgGsZxQ5s8hu61-JCUwn-UL-CM'; // 您的表單 ID
var SHEET_NAME = '表單回應2';     // 您存放資料的工作表名稱
var STATUS_COL_HEADER = '狀態'; // 您剛剛新增的那一欄標題名稱
// -------------

/**
 * 緊急救援工具：如果出現 "Too many triggers" 錯誤，
 * 請先手動執行一次這個函式，然後再執行 startQueue。
 
function deleteAllTriggers() {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    ScriptApp.deleteTrigger(triggers[i]);
  }
  console.log('已手動清除所有觸發器。');
}*/

/**
 * 工具函式：根據函式名稱刪除觸發器
 */
function deleteTriggerByName(functionName) {
  var triggers = ScriptApp.getProjectTriggers();
  for (var i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === functionName) {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }
}

function startQueue() {
  // 這是啟動用的函式，第一次執行請點選這個
  processNextRow();
  
}

/**
 * 主邏輯：處理下一筆資料
 */
// 2. 在 processNextRow 或 startQueue 中修改建立觸發器的部分
function processNextRow() {
// === 關鍵修正：執行的一開始，先刪除舊的觸發器 ===
  // 這樣保證每次執行時，舊的計時器都被清掉了，不會佔用配額
  deleteTriggerByName("processNextRow"); 

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(SHEET_NAME);
  if (!sheet) {
    console.error("找不到工作表：" + SHEET_NAME);
    return;
  }
  var rows = sheet.getDataRange().getValues();
  var headers = rows[0];

  // 1. 找出「狀態」欄位是第幾欄 (程式索引從0開始)
  var statusColIndex = headers.indexOf(STATUS_COL_HEADER);
  if (statusColIndex === -1) {
    SpreadsheetApp.getUi().alert('找不到標題為 "' + STATUS_COL_HEADER + '" 的欄位，請檢查您的試算表。');
    return;
  }

  // 2. 尋找下一筆「還沒處理」的資料
  var targetRowIndex = -1;
  // 從第1列(即第二行)開始找
  for (var i = 1; i < rows.length; i++) {
    // 如果狀態欄是空的，表示這筆還沒填
    if (rows[i][statusColIndex] === "" || rows[i][statusColIndex] === undefined) {
      targetRowIndex = i;
      break; 
    }
  }

  // 3. 如果找不到空白的，表示全部都填完了
  if (targetRowIndex === -1) {
    console.log("所有資料皆已提交完成！");
    return; // 結束程式
  }

  // 4. 開始提交這筆資料
  submitRowToForm(rows[targetRowIndex], headers, sheet, targetRowIndex + 1, statusColIndex + 1);

  // 5. 設定下一次的觸發器 (隨機 3~5 分鐘)
  var minMinutes = 3;
  var maxMinutes = 5;
  // 計算隨機毫秒數： (3 + 0~2的隨機數) * 60秒 * 1000毫秒
  var randomDelayMs = Math.floor((Math.random() * (maxMinutes - minMinutes) + minMinutes) * 60 * 1000);
  
  console.log("本筆處理完成。下一次執行將在 " + (randomDelayMs/1000/60).toFixed(2) + " 分鐘後啟動。");

  // 建立一次性觸發器，指定時間後再次執行 'processNextRow' 函式
  ScriptApp.newTrigger('processNextRow')
           .timeBased()
           .after(randomDelayMs)
           .create();
}

function submitRowToForm(rowData, headers, sheet, rowNumber, statusColNumber) {
  var form = FormApp.openById(FORM_ID);
  var items = form.getItems();
  var formResponse = form.createResponse();
  
  // 掃描欄位並填寫 (排除狀態欄)
  for (var j = 0; j < headers.length; j++) {
    var headerName = headers[j];
    var cellData = rowData[j];
    
    // 跳過狀態欄本身或空值
    if (headerName === STATUS_COL_HEADER || cellData === "") continue;

    for (var k = 0; k < items.length; k++) {
      var item = items[k];
      if (item.getTitle() === headerName) {
        var responseItem = null;
        
        // 根據題型填入資料 (您可根據需求擴充)
        if (item.getType() == FormApp.ItemType.TEXT) {
          responseItem = item.asTextItem().createResponse(String(cellData));
        } else if (item.getType() == FormApp.ItemType.PARAGRAPH_TEXT) {
          responseItem = item.asParagraphTextItem().createResponse(String(cellData));
        } else if (item.getType() == FormApp.ItemType.MULTIPLE_CHOICE) {
          responseItem = item.asMultipleChoiceItem().createResponse(String(cellData));
        } else if (item.getType() == FormApp.ItemType.CHECKBOX) {
             // 如果是多選(Checkboxes)，假設資料是用逗號分隔
             var choices = String(cellData).split(/,\s*/); 
             responseItem = item.asCheckboxItem().createResponse(choices);
        } else if (item.getType() == FormApp.ItemType.LIST) {
             // 下拉式選單
             responseItem = item.asListItem().createResponse(String(cellData));
        } else if (item.getType() == FormApp.ItemType.SCALE) {
             // 線性刻度
             responseItem = item.asScaleItem().createResponse(parseInt(cellData));
        }

        if (responseItem) {
          formResponse.withItemResponse(responseItem);
        }
        break;
      }
    }
  }
  
  // 提交表單
  formResponse.submit();
  
  // 在 Sheet 上標記「已完成」
  sheet.getRange(rowNumber, statusColNumber).setValue("已完成 (" + new Date().toLocaleTimeString() + ")");
}