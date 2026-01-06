*** SPSS Syntax for Research_GAS Data Definitions ***.

*** 1. 定義變數標籤 (Variable Labels) ***.
VARIABLE LABELS
  Match_ID "配對編號 (生日+手機)"
  WorkHours "每週平均工時"
  PM_Has "是否有進行績效考核"
  PM_Form_Supervisor "績效形式: 主管評核"
  PM_Form_Self "績效形式: 員工自評"
  PM_Form_Interview "績效形式: 績效面談"
  PM_Form_Other "績效形式: 其他"
  PM_Result "考核結果/回饋性質"
  PM_Help "職涯發展幫助程度"
  HCP1 "HCP1"
  HCP2 "HCP2"
  HCP3 "HCP3"
  HCP4_R "HCP4 (反向)"
  HCP5 "HCP5"
  HCP6_R "HCP6 (反向)"
  JCP1_R "JCP1 (反向)"
  JCP2_R "JCP2 (反向)"
  JCP3_R "JCP3 (反向)"
  JCP4_R "JCP4 (反向)"
  JCP5_R "JCP5 (反向)"
  JCP6 "JCP6"
  Gender "性別"
  Age "年齡"
  Education "教育程度"
  Marriage "婚姻狀況"
  NowJobTenure "現職年資 (總月數)"
  JobTenure "工作總年資 (總月數)"
  Position "工作職級"
  Industry "產業別"
  OrgSize "公司規模".
EXECUTE.

*** 2. 定義數值標籤 (Value Labels) ***.

* 工時 (WorkHours).
VALUE LABELS WorkHours
  1 "40小時(含)以上"
  0 "未滿40小時".

* 績效考核有無 (PM_Has).
VALUE LABELS PM_Has
  1 "是"
  0 "並沒有".

* 績效考核形式多選 (PM_Form_xxx).
VALUE LABELS PM_Form_Supervisor PM_Form_Self PM_Form_Interview PM_Form_Other
  1 "有"
  0 "無".

* 績效結果 (PM_Result).
VALUE LABELS PM_Result
  3 "正向回饋 (優於預期/肯定)"
  2 "中性/持平"
  1 "負向回饋 (低於預期/批評)".

* 性別 (Gender).
VALUE LABELS Gender
  1 "男"
  2 "女"
  3 "其他".

* 教育程度 (Education).
VALUE LABELS Education
  1 "高中職及以下"
  2 "專科"
  3 "大學"
  4 "碩士"
  5 "博士".

* 婚姻狀況 (Marriage).
VALUE LABELS Marriage
  1 "未婚"
  2 "已婚(無子女)"
  3 "已婚(有子女)"
  4 "其他".

* 職級 (Position).
VALUE LABELS Position
  1 "一般員工"
  2 "基層主管"
  3 "中階主管"
  4 "高階主管".

* 產業別 (Industry).
VALUE LABELS Industry
  1 "製造業"
  2 "科技/資訊業"
  3 "金融/保險業"
  4 "服務業"
  5 "醫療/生技"
  6 "教育/學術"
  7 "公部門/國營事業"
  8 "其他".

* 公司規模 (OrgSize).
VALUE LABELS OrgSize
  1 "30人以下"
  2 "31-100人"
  3 "101-500人"
  4 "501-1000人"
  5 "1001人以上".

EXECUTE.
