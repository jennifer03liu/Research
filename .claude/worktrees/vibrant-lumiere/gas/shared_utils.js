/**
 * Gas 共用輔助函式與變數 (shared_utils.js)
 */

var MANUAL_OVERRIDES = {
    'jaychen@trendforce.com': '0710588',
    'huang0447@itri.org.tw': '0315587',
    'baoan5669@gmail.com': '1003082',
    'zxcv70103@gmail.com': '0108108',
    'jhenjiahu@gmail.com': '1230016',
    'zxc52040@gmail.com': '0404983'
};

function cleanStr(val) {
    if (val === null || val === undefined || val === "") return "";
    return String(val).trim().toLowerCase();
}

function cleanMatchId(val) {
    if (val === "" || val === null || val === undefined) return "";
    var matchVal = String(val).replace(/\D/g, "");
    if (/^\d+$/.test(matchVal)) {
        while (matchVal.length > 0 && matchVal.length < 7) {
            matchVal = "0" + matchVal;
        }
    }
    return matchVal;
}

function getEffectiveMatchId(email, rawMatchId) {
    var cleanId = cleanMatchId(rawMatchId);
    var cleanMail = cleanStr(email);
    if (cleanMail && MANUAL_OVERRIDES[cleanMail]) {
        return MANUAL_OVERRIDES[cleanMail];
    }
    return cleanId;
}
